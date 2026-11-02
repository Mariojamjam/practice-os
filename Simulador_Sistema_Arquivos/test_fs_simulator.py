#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados para o Simulador de Sistema de Arquivos
Disciplina: Sistemas Operacionais - UFRPE (Entrega Parcial 01)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fs_simulator import (
    FileSystem,
    AllocationStrategyName,
    parse_size_to_bytes,
    format_bytes,
    BlockType
)


class TestFileSystem(unittest.TestCase):

    def setUp(self):
        # Inicia disco padrão de 16 blocos de 4 KB com alocação indexada
        self.fs = FileSystem(block_size=4096, total_blocks=16, strategy_name=AllocationStrategyName.INDEXED)

    def test_parse_size(self):
        self.assertEqual(parse_size_to_bytes("10KB"), 10240)
        self.assertEqual(parse_size_to_bytes("4KB"), 4096)
        self.assertEqual(parse_size_to_bytes("512B"), 512)
        self.assertEqual(parse_size_to_bytes("1MB"), 1048576)
        self.assertEqual(parse_size_to_bytes("2048"), 2048)

    def test_tree_hierarchy_and_example_1_1(self):
        # Exemplo 1.1 do enunciado
        ok, _ = self.fs.mkdir("/sistema")
        self.assertTrue(ok)
        ok, _ = self.fs.mkdir("/sistema/logs")
        self.assertTrue(ok)
        ok, _ = self.fs.create_file("/sistema/logs/app.log", 10240)
        self.assertTrue(ok)

        tree = self.fs.get_tree_lines()
        tree_text = "\n".join(tree)
        self.assertIn("sistema/ [DIR]", tree_text)
        self.assertIn("logs/ [DIR]", tree_text)
        self.assertIn("app.log (10 KB) [ARQ]", tree_text)

    def test_indexed_allocation_and_fragmentation_example_1_2(self):
        # Exemplo 1.2 do enunciado
        self.fs.mkdir("/sistema")
        self.fs.mkdir("/sistema/logs")
        self.fs.create_file("/sistema/logs/app.log", 10240)

        status = self.fs.get_disk_status(details=True)
        self.assertIn("Bloco 00 [INODE_RAIZ]  : Diretório '/'", status)
        self.assertIn("Bloco 01 [INODE_APP]   : Arquivo '/sistema/logs/app.log'", status)
        self.assertIn("Bloco 02 [DADO]        : '/sistema/logs/app.log' (Bloco 1 - 4096 bytes ocupados)", status)
        self.assertIn("Bloco 03 [DADO]        : '/sistema/logs/app.log' (Bloco 2 - 4096 bytes ocupados)", status)
        self.assertIn("Bloco 04 [DADO]        : '/sistema/logs/app.log' (Bloco 3 - 2048 bytes ocupados)", status)
        self.assertIn("Bloco 05..15           : [LIVRE]", status)

        self.assertIn("Tamanho Real do Arquivo 'app.log': 10240 bytes (10 KB)", status)
        self.assertIn("Espaço Alocado no Disco          : 12288 bytes (3 blocos de 4 KB)", status)
        self.assertIn("Fragmentação Interna             : 2048 bytes (50% de desperdício no Bloco 04)", status)
        self.assertIn("Fragmentação Externa             : 0 bytes", status)
        self.assertIn("Necessidade de Compactação       : NÃO (Blocos alocados via i-node indexado)", status)

    def test_crud_operations(self):
        # Create
        ok, msg = self.fs.mkdir("/docs")
        self.assertTrue(ok)
        ok, msg = self.fs.create_file("/docs/relatorio.txt", 1000, content="Texto confidencial")
        self.assertTrue(ok)

        # Read
        ok, content = self.fs.read_file("/docs/relatorio.txt")
        self.assertTrue(ok)
        self.assertIn("Texto confidencial", content)

        # Update
        ok, msg = self.fs.update_file("/docs/relatorio.txt", 5000, new_content="Texto expandido")
        self.assertTrue(ok)
        node = self.fs.resolve_path("/docs/relatorio.txt")
        self.assertEqual(node.size_bytes, 5000)
        self.assertEqual(len(node.allocated_blocks), 2)  # ceil(5000 / 4096) = 2

        # Delete
        ok, msg = self.fs.delete_node("/docs/relatorio.txt")
        self.assertTrue(ok)
        self.assertIsNone(self.fs.resolve_path("/docs/relatorio.txt"))

        # Delete directory
        ok, msg = self.fs.delete_node("/docs")
        self.assertTrue(ok)
        self.assertIsNone(self.fs.resolve_path("/docs"))

    def test_relative_paths_and_navigation(self):
        self.fs.mkdir("/a/b/c")
        ok, path = self.fs.change_dir("/a/b")
        self.assertTrue(ok)
        self.assertEqual(path, "/a/b")

        # Cria arquivo usando caminho relativo
        ok, _ = self.fs.create_file("c/teste.txt", 2048)
        self.assertTrue(ok)

        # Navega com ..
        self.fs.change_dir("..")
        self.assertEqual(self.fs.current_dir.get_path(), "/a")

        # Resolve relativo com . e ..
        node = self.fs.resolve_path("b/c/../c/./teste.txt")
        self.assertNotNull(node) if hasattr(self, 'assertNotNull') else self.assertIsNotNone(node)
        self.assertEqual(node.get_path(), "/a/b/c/teste.txt")

    def test_contiguous_allocation_and_external_fragmentation(self):
        fs = FileSystem(block_size=4096, total_blocks=16, strategy_name=AllocationStrategyName.CONTIGUOUS)
        
        # Aloca 4 arquivos contíguos
        fs.create_file("/f1.bin", 16384)  # 4 blocos (0..3)
        fs.create_file("/f2.bin", 8192)   # 2 blocos (4..5)
        fs.create_file("/f3.bin", 24576)  # 6 blocos (6..11)
        fs.create_file("/f4.bin", 8192)   # 2 blocos (12..13)
        # Livres: blocos 14 e 15 (2 blocos = 8 KB)

        # Remove f2.bin, criando buraco nos blocos 4..5 (2 blocos = 8 KB)
        fs.delete_node("/f2.bin")
        # Total livre agora: 4 blocos (16 KB), mas separados em 4..5 e 14..15!

        # Tentar alocar 16 KB (4 blocos contíguos) DEVE FALHAR por fragmentação externa!
        ok, msg = fs.create_file("/grande.bin", 16384)
        self.assertFalse(ok)
        self.assertIn("Espaço insuficiente ou blocos contíguos indisponíveis", msg)

        status = fs.get_disk_status(details=True)
        self.assertIn("Fragmentação Externa             : 8192 bytes", status)
        self.assertIn("Necessidade de Compactação       : SIM", status)

        # Compacta o disco
        ok, msg = fs.compact_disk()
        self.assertTrue(ok)

        # Agora a alocação de 16 KB DEVE FUNCIONAR
        ok, msg = fs.create_file("/grande.bin", 16384)
        self.assertTrue(ok)

        status_after = fs.get_disk_status(details=True)
        self.assertIn("Fragmentação Externa             : 0 bytes", status_after)
        self.assertIn("Necessidade de Compactação       : NÃO", status_after)

    def test_linked_allocation(self):
        fs = FileSystem(block_size=4096, total_blocks=16, strategy_name=AllocationStrategyName.LINKED)
        ok, _ = fs.create_file("/encadeado.bin", 12288)  # 3 blocos
        self.assertTrue(ok)
        node = fs.resolve_path("/encadeado.bin")
        self.assertEqual(len(node.allocated_blocks), 3)
        
        # Verifica ponteiros de encadeamento
        b0 = fs.disk.blocks[node.allocated_blocks[0]]
        b1 = fs.disk.blocks[node.allocated_blocks[1]]
        b2 = fs.disk.blocks[node.allocated_blocks[2]]
        self.assertEqual(b0.next_block, node.allocated_blocks[1])
        self.assertEqual(b1.next_block, node.allocated_blocks[2])
        self.assertIsNone(b2.next_block)


if __name__ == "__main__":
    unittest.main()
