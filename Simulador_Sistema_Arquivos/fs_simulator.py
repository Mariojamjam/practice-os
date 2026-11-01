#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
SIMULADOR DE SISTEMA DE ARQUIVOS (SISTEMAS OPERACIONAIS - UFRPE)
Disciplina: Sistemas Operacionais | Entrega Parcial 01
Discente(s): Luiz Maranhão & Mário Jorge
===============================================================================
Funcionalidades:
1. Hierarquia em Árvore:
   - Caminhos absolutos (ex: /sistema/logs/app.log) e relativos (ex: ../doc.txt).
   - Navegação: cd, pwd, ls, tree.
2. Operações CRUD:
   - Criar: mkdir, create (com --size ou --content).
   - Ler: cat / read, stat.
   - Atualizar: update (--size), write (conteúdo), rename / mv.
   - Deletar: rm, rmdir (com suporte a -r).
3. Mapeamento e Alocação Física de Blocos:
   - Camada de disco física configurável (tamanho do bloco e quantidade de blocos).
   - 3 Estratégias Clássicas Implementadas:
     * Alocação Indexada (i-node) [Padrão conforme especificação]
     * Alocação Contígua
     * Alocação Encadeada (Linked List / FAT)
4. Diagnóstico do Disco e Análise de Fragmentação:
   - Mapa gráfico e detalhado de ocupação de cada bloco físico.
   - Cálculo exato de fragmentação interna (desperdício no último bloco).
   - Cálculo exato de fragmentação externa (blocos livres e dispersos incapazes
     de abrigar alocações contíguas).
   - Indicação explícita e fundamentada sobre necessidade de compactação.
   - Desfragmentador / Compactador de disco integrado.
===============================================================================
"""

import os
import sys
import math
import time
import re
from typing import Dict, List, Optional, Tuple, Set

# Força codificação UTF-8 para terminais Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# =============================================================================
# UTILITÁRIOS DE TAMANHO E FORMATAÇÃO
# =============================================================================

def parse_size_to_bytes(size_str: str) -> int:
    """
    Converte strings de tamanho (ex: '10KB', '4KB', '512B', '1MB', '2048') para bytes inteiros.
    """
    size_str = str(size_str).strip().upper()
    if not size_str:
        return 0
    
    # Casos com unidade
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$", size_str)
    if not match:
        raise ValueError(f"Formato de tamanho inválido: '{size_str}'. Exemplos válidos: 10KB, 512B, 4KB, 1MB, 1024.")
    
    val, unit = match.groups()
    val = float(val)
    unit = unit.upper()
    
    multipliers = {
        "": 1,
        "B": 1,
        "K": 1024,
        "KB": 1024,
        "M": 1024 * 1024,
        "MB": 1024 * 1024,
        "G": 1024 * 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
    }
    
    if unit not in multipliers:
        raise ValueError(f"Unidade desconhecida: '{unit}'")
    
    return int(math.ceil(val * multipliers[unit]))


def format_bytes(n_bytes: int) -> str:
    """Formata bytes para representação legível (ex: '10 KB', '4 KB', '512 B')."""
    if n_bytes < 1024:
        return f"{n_bytes} B"
    elif n_bytes < 1024 * 1024:
        kb = n_bytes / 1024
        return f"{int(kb)} KB" if kb.is_integer() else f"{kb:.1f} KB"
    else:
        mb = n_bytes / (1024 * 1024)
        return f"{int(mb)} MB" if mb.is_integer() else f"{mb:.2f} MB"


# =============================================================================
# MODELO DO DISCO E BLOCOS FÍSICOS
# =============================================================================

class BlockType:
    FREE = "LIVRE"
    INODE_ROOT = "INODE_RAIZ"
    INODE_FILE = "INODE_APP"
    INODE_DIR = "INODE_DIR"
    DATA = "DADO"
    FAT = "TABELA_FAT"


class DiskBlock:
    """Representa um bloco físico do disco rígido / SSD simulado."""
    def __init__(self, index: int, size: int):
        self.index = index
        self.size = size                   # Tamanho fixo em bytes (ex: 4096)
        self.block_type = BlockType.FREE   # Tipo do bloco
        self.owner_path: Optional[str] = None  # Caminho do arquivo/diretório dono
        self.bytes_used: int = 0           # Bytes realmente ocupados (0 <= bytes_used <= size)
        self.file_block_index: int = 0     # Índice relativo no arquivo (1, 2, 3...)
        self.next_block: Optional[int] = None # Ponteiro de encadeamento (alocação encadeada)
        self.content: str = ""             # Dados simulados

    @property
    def is_free(self) -> bool:
        return self.block_type == BlockType.FREE

    def allocate(self, block_type: str, owner_path: str, bytes_used: int,
                 file_block_index: int = 0, content: str = ""):
        self.block_type = block_type
        self.owner_path = owner_path
        self.bytes_used = min(bytes_used, self.size)
        self.file_block_index = file_block_index
        self.content = content
        self.next_block = None

    def free(self):
        self.block_type = BlockType.FREE
        self.owner_path = None
        self.bytes_used = 0
        self.file_block_index = 0
        self.next_block = None
        self.content = ""


class Disk:
    """Simula a camada física de blocos contíguos do disco."""
    def __init__(self, block_size: int = 4096, total_blocks: int = 16):
        self.block_size = block_size
        self.total_blocks = total_blocks
        self.blocks: List[DiskBlock] = [DiskBlock(i, block_size) for i in range(total_blocks)]

    @property
    def total_capacity(self) -> int:
        return self.block_size * self.total_blocks

    @property
    def free_blocks_count(self) -> int:
        return sum(1 for b in self.blocks if b.is_free)

    @property
    def used_blocks_count(self) -> int:
        return self.total_blocks - self.free_blocks_count

    def get_free_block_indices(self) -> List[int]:
        return [b.index for b in self.blocks if b.is_free]


# =============================================================================
# ESTRUTURA HIERÁRQUICA EM ÁRVORE (DIRETÓRIOS E ARQUIVOS)
# =============================================================================

class FSNode:
    """Nó da árvore do sistema de arquivos (pode ser Diretório ou Arquivo)."""
    def __init__(self, name: str, is_dir: bool = False, parent: Optional['FSNode'] = None):
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.children: Dict[str, 'FSNode'] = {}  # apenas para diretórios
        self.size_bytes: int = 0                 # tamanho lógico real
        self.created_at = time.time()
        self.modified_at = time.time()
        
        # Estruturas físicas vinculadas
        self.inode_block: Optional[int] = None   # Bloco físico onde reside o i-node (alocação indexada)
        self.allocated_blocks: List[int] = []    # Lista de blocos físicos de dados ocupados
        self.content: str = ""                   # Conteúdo simulado em texto

    @property
    def is_file(self) -> bool:
        return not self.is_dir

    def get_path(self) -> str:
        """Retorna o caminho canônico absoluto do nó."""
        if self.parent is None or self.name == "/":
            return "/"
        parts = []
        curr = self
        while curr and curr.parent:
            parts.append(curr.name)
            curr = curr.parent
        return "/" + "/".join(reversed(parts))


# =============================================================================
# ESTRATÉGIAS DE ALOCAÇÃO FÍSICA DE BLOCOS
# =============================================================================

class AllocationStrategyName:
    INDEXED = "indexada"      # i-node
    CONTIGUOUS = "contigua"   # Contígua
    LINKED = "encadeada"      # Encadeada / FAT


class AllocationStrategy:
    """Classe base para as estratégias de alocação de blocos."""
    def __init__(self, disk: Disk):
        self.disk = disk

    def allocate(self, node: FSNode, size_bytes: int) -> bool:
        raise NotImplementedError

    def deallocate(self, node: FSNode):
        raise NotImplementedError

    def resize(self, node: FSNode, new_size_bytes: int) -> bool:
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError


class IndexedAllocation(AllocationStrategy):
    """
    Alocação Indexada baseada em i-nodes:
    - 1 bloco dedicado para o i-node do arquivo (contendo ponteiros diretos).
    - N blocos de dados alocados onde houver espaço livre (não precisa ser contíguo).
    - Não sofre de fragmentação externa.
    """
    def get_name(self) -> str:
        return "Indexada (i-node)"

    def allocate(self, node: FSNode, size_bytes: int) -> bool:
        block_size = self.disk.block_size
        n_data_blocks = int(math.ceil(size_bytes / block_size)) if size_bytes > 0 else 1
        
        # Precisamos de 1 bloco de i-node + n_data_blocks
        total_needed = 1 + n_data_blocks
        free_indices = self.disk.get_free_block_indices()
        
        if len(free_indices) < total_needed:
            return False  # Espaço insuficiente no disco
        
        # Aloca bloco de i-node
        inode_idx = free_indices[0]
        tag_inode = BlockType.INODE_ROOT if node.get_path() == "/" else (
            BlockType.INODE_DIR if node.is_dir else BlockType.INODE_FILE
        )
        self.disk.blocks[inode_idx].allocate(
            block_type=tag_inode,
            owner_path=node.get_path(),
            bytes_used=block_size,
            file_block_index=0,
            content=f"i-node meta: {node.name}"
        )
        node.inode_block = inode_idx
        
        # Aloca blocos de dados
        data_indices = free_indices[1:1 + n_data_blocks]
        node.allocated_blocks = data_indices
        node.size_bytes = size_bytes
        
        remaining = size_bytes
        for i, b_idx in enumerate(data_indices):
            used_in_block = min(remaining, block_size)
            if remaining == 0 and size_bytes == 0:
                used_in_block = 0
            self.disk.blocks[b_idx].allocate(
                block_type=BlockType.DATA,
                owner_path=node.get_path(),
                bytes_used=used_in_block,
                file_block_index=i + 1
            )
            remaining -= used_in_block
        
        return True

    def deallocate(self, node: FSNode):
        if node.inode_block is not None:
            self.disk.blocks[node.inode_block].free()
            node.inode_block = None
        for b_idx in node.allocated_blocks:
            self.disk.blocks[b_idx].free()
        node.allocated_blocks = []
        node.size_bytes = 0

    def resize(self, node: FSNode, new_size_bytes: int) -> bool:
        # Para redimensionamento limpo, desaloca e realoca
        old_inode = node.inode_block
        old_blocks = list(node.allocated_blocks)
        old_size = node.size_bytes
        self.deallocate(node)
        
        if self.allocate(node, new_size_bytes):
            return True
        else:
            # Reverte se não couber
            node.inode_block = old_inode
            node.allocated_blocks = old_blocks
            node.size_bytes = old_size
            # Restaura no disco
            if old_inode is not None:
                self.disk.blocks[old_inode].allocate(BlockType.INODE_FILE, node.get_path(), self.disk.block_size)
            rem = old_size
            for i, b_idx in enumerate(old_blocks):
                ub = min(rem, self.disk.block_size)
                self.disk.blocks[b_idx].allocate(BlockType.DATA, node.get_path(), ub, i + 1)
                rem -= ub
            return False


class ContiguousAllocation(AllocationStrategy):
    """
    Alocação Contígua:
    - O arquivo precisa de blocos estritamente sequenciais e contíguos no disco.
    - Pode sofrer severamente de fragmentação externa caso arquivos intermediários
      sejam apagados.
    - Suporta compactação explícita de disco.
    """
    def get_name(self) -> str:
        return "Contígua"

    def allocate(self, node: FSNode, size_bytes: int) -> bool:
        block_size = self.disk.block_size
        n_blocks = int(math.ceil(size_bytes / block_size)) if size_bytes > 0 else 1
        
        # Busca first-fit por sequência contígua de blocos livres
        found_start = -1
        current_streak = 0
        streak_start = -1
        
        for i, b in enumerate(self.disk.blocks):
            if b.is_free:
                if current_streak == 0:
                    streak_start = i
                current_streak += 1
                if current_streak == n_blocks:
                    found_start = streak_start
                    break
            else:
                current_streak = 0
                streak_start = -1
                
        if found_start == -1:
            return False  # Não há segmento contíguo suficiente (possível fragmentação externa!)
        
        allocated = list(range(found_start, found_start + n_blocks))
        node.allocated_blocks = allocated
        node.size_bytes = size_bytes
        node.inode_block = None
        
        remaining = size_bytes
        for i, b_idx in enumerate(allocated):
            used = min(remaining, block_size)
            self.disk.blocks[b_idx].allocate(
                block_type=BlockType.DATA,
                owner_path=node.get_path(),
                bytes_used=used,
                file_block_index=i + 1
            )
            remaining -= used
            
        return True

    def deallocate(self, node: FSNode):
        for b_idx in node.allocated_blocks:
            self.disk.blocks[b_idx].free()
        node.allocated_blocks = []
        node.size_bytes = 0

    def resize(self, node: FSNode, new_size_bytes: int) -> bool:
        old_blocks = list(node.allocated_blocks)
        old_size = node.size_bytes
        self.deallocate(node)
        if self.allocate(node, new_size_bytes):
            return True
        else:
            # Reverte
            for i, b_idx in enumerate(old_blocks):
                ub = min(old_size, self.disk.block_size)
                self.disk.blocks[b_idx].allocate(BlockType.DATA, node.get_path(), ub, i + 1)
            node.allocated_blocks = old_blocks
            node.size_bytes = old_size
            return False


class LinkedAllocation(AllocationStrategy):
    """
    Alocação Encadeada (FAT / Lista Encadeada de Blocos):
    - Cada bloco aponta para o próximo bloco do arquivo no disco.
    - Blocos podem estar dispersos livremente no disco sem fragmentação externa.
    """
    def get_name(self) -> str:
        return "Encadeada (Linked List / FAT)"

    def allocate(self, node: FSNode, size_bytes: int) -> bool:
        block_size = self.disk.block_size
        n_blocks = int(math.ceil(size_bytes / block_size)) if size_bytes > 0 else 1
        free_indices = self.disk.get_free_block_indices()
        
        if len(free_indices) < n_blocks:
            return False
        
        allocated = free_indices[:n_blocks]
        node.allocated_blocks = allocated
        node.size_bytes = size_bytes
        node.inode_block = None
        
        remaining = size_bytes
        for i, b_idx in enumerate(allocated):
            used = min(remaining, block_size)
            self.disk.blocks[b_idx].allocate(
                block_type=BlockType.DATA,
                owner_path=node.get_path(),
                bytes_used=used,
                file_block_index=i + 1
            )
            if i < len(allocated) - 1:
                self.disk.blocks[b_idx].next_block = allocated[i + 1]
            else:
                self.disk.blocks[b_idx].next_block = None  # EOF (-1)
            remaining -= used
            
        return True

    def deallocate(self, node: FSNode):
        for b_idx in node.allocated_blocks:
            self.disk.blocks[b_idx].free()
        node.allocated_blocks = []
        node.size_bytes = 0

    def resize(self, node: FSNode, new_size_bytes: int) -> bool:
        old_blocks = list(node.allocated_blocks)
        old_size = node.size_bytes
        self.deallocate(node)
        if self.allocate(node, new_size_bytes):
            return True
        else:
            for i, b_idx in enumerate(old_blocks):
                ub = min(old_size, self.disk.block_size)
                self.disk.blocks[b_idx].allocate(BlockType.DATA, node.get_path(), ub, i + 1)
                self.disk.blocks[b_idx].next_block = old_blocks[i + 1] if i < len(old_blocks) - 1 else None
            node.allocated_blocks = old_blocks
            node.size_bytes = old_size
            return False


# =============================================================================
# SUBSISTEMA DE ARQUIVOS (FILE SYSTEM CORE)
# =============================================================================

class FileSystem:
    """Controlador do Sistema de Arquivos Hierárquico."""
    def __init__(self, block_size: int = 4096, total_blocks: int = 16,
                 strategy_name: str = AllocationStrategyName.INDEXED):
        self.block_size = block_size
        self.total_blocks = total_blocks
        self.disk = Disk(block_size=block_size, total_blocks=total_blocks)
        
        # Estratégia de Alocação
        self.strategy_name = strategy_name.lower()
        self.strategy = self._create_strategy(self.strategy_name)
        
        # Raiz da Árvore
        self.root = FSNode(name="/", is_dir=True, parent=None)
        self.current_dir = self.root
        
        # Inicializa o inode da raiz se for alocação indexada
        if isinstance(self.strategy, IndexedAllocation):
            self.disk.blocks[0].allocate(
                block_type=BlockType.INODE_ROOT,
                owner_path="/",
                bytes_used=self.block_size,
                file_block_index=0,
                content="i-node: raiz"
            )
            self.root.inode_block = 0

    def _create_strategy(self, name: str) -> AllocationStrategy:
        if name in ("indexada", "indexed", "inode"):
            return IndexedAllocation(self.disk)
        elif name in ("contigua", "contiguous"):
            return ContiguousAllocation(self.disk)
        elif name in ("encadeada", "linked", "fat"):
            return LinkedAllocation(self.disk)
        else:
            raise ValueError(f"Estratégia inválida: '{name}'. Escolha entre: indexada, contigua, encadeada.")

    def set_strategy(self, strategy_name: str):
        """Alterna a estratégia de alocação física e reformata/reorganiza."""
        self.strategy_name = strategy_name.lower()
        old_nodes = self.get_all_nodes(include_dirs=False)
        old_data = [(n.get_path(), n.size_bytes, n.content) for n in old_nodes]
        
        # Limpa disco
        for b in self.disk.blocks:
            b.free()
            
        self.strategy = self._create_strategy(self.strategy_name)
        
        # Reinicializa raiz
        if isinstance(self.strategy, IndexedAllocation):
            self.disk.blocks[0].allocate(BlockType.INODE_ROOT, "/", self.block_size, 0)
            self.root.inode_block = 0
        else:
            self.root.inode_block = None
            
        # Re-aloca arquivos existentes
        for path, size, content in old_data:
            node = self.resolve_path(path)
            if node:
                self.strategy.allocate(node, size)
                node.content = content

    # -------------------------------------------------------------------------
    # NAVEGAÇÃO E RESOLUÇÃO DE CAMINHOS (ABSOLUTOS E RELATIVOS)
    # -------------------------------------------------------------------------

    def resolve_path(self, path: str, start_node: Optional[FSNode] = None) -> Optional[FSNode]:
        """
        Resolve um caminho (absoluto ou relativo) a partir do diretório atual ou raiz.
        Suporta '.', '..', '/' e espaços.
        """
        path = path.strip()
        if not path:
            return start_node or self.current_dir
        
        if path == "/":
            return self.root
        
        if path.startswith("/"):
            curr = self.root
            parts = [p for p in path.split("/") if p]
        else:
            curr = start_node or self.current_dir
            parts = [p for p in path.split("/") if p]
            
        for part in parts:
            if part == ".":
                continue
            elif part == "..":
                if curr.parent:
                    curr = curr.parent
            else:
                if not curr.is_dir or part not in curr.children:
                    return None
                curr = curr.children[part]
                
        return curr

    def change_dir(self, path: str) -> Tuple[bool, str]:
        """Comando 'cd': altera o diretório corrente."""
        node = self.resolve_path(path)
        if node is None:
            return False, f"Diretório não encontrado: '{path}'"
        if not node.is_dir:
            return False, f"O caminho '{path}' não é um diretório."
        self.current_dir = node
        return True, self.current_dir.get_path()

    # -------------------------------------------------------------------------
    # OPERAÇÕES CRUD DE ARQUIVOS E DIRETÓRIOS
    # -------------------------------------------------------------------------

    def mkdir(self, path: str, create_parents: bool = True) -> Tuple[bool, str]:
        """Cria um novo diretório."""
        path = path.strip()
        if not path or path == "/":
            return False, "Caminho de diretório inválido."
        
        # Separa diretório pai e nome do novo diretório
        if "/" in path:
            parent_path, name = path.rsplit("/", 1)
            parent_path = parent_path if parent_path else "/"
        else:
            parent_path, name = ".", path
            
        if not name or name in (".", ".."):
            return False, f"Nome de diretório inválido: '{name}'"
            
        parent_node = self.resolve_path(parent_path)
        if parent_node is None:
            if create_parents:
                # Cria recursivamente os pais
                success, msg = self.mkdir(parent_path, create_parents=True)
                if not success:
                    return False, msg
                parent_node = self.resolve_path(parent_path)
            else:
                return False, f"Diretório pai não encontrado: '{parent_path}'"
                
        if not parent_node.is_dir:
            return False, f"'{parent_path}' não é um diretório."
            
        if name in parent_node.children:
            return False, f"O item '{name}' já existe em '{parent_node.get_path()}'."
            
        new_dir = FSNode(name=name, is_dir=True, parent=parent_node)
        parent_node.children[name] = new_dir
        parent_node.modified_at = time.time()
        
        return True, f"Diretório '{new_dir.get_path()}' criado com sucesso."

    def create_file(self, path: str, size_bytes: int, content: str = "") -> Tuple[bool, str]:
        """Cria um arquivo e aloca seus blocos físicos no disco."""
        path = path.strip()
        if not path or path.endswith("/"):
            return False, "Caminho de arquivo inválido."
        
        if "/" in path:
            parent_path, name = path.rsplit("/", 1)
            parent_path = parent_path if parent_path else "/"
        else:
            parent_path, name = ".", path
            
        parent_node = self.resolve_path(parent_path)
        if parent_node is None:
            return False, f"Diretório pai não encontrado: '{parent_path}'"
        if not parent_node.is_dir:
            return False, f"'{parent_path}' não é um diretório."
        if name in parent_node.children:
            return False, f"O arquivo ou diretório '{name}' já existe em '{parent_node.get_path()}'."
            
        # Cria nó do arquivo
        file_node = FSNode(name=name, is_dir=False, parent=parent_node)
        file_node.content = content
        
        # Tenta alocar no disco via estratégia ativa
        success = self.strategy.allocate(file_node, size_bytes)
        if not success:
            return False, (
                f"Falha de Alocação: Espaço insuficiente ou blocos contíguos indisponíveis "
                f"no disco ({self.strategy.get_name()}) para {format_bytes(size_bytes)}."
            )
            
        parent_node.children[name] = file_node
        parent_node.modified_at = time.time()
        
        return True, (
            f"Arquivo '{file_node.get_path()}' criado com sucesso "
            f"({format_bytes(size_bytes)}, {len(file_node.allocated_blocks)} blocos de dados)."
        )

    def read_file(self, path: str) -> Tuple[bool, str]:
        """Lê o conteúdo e metadados de um arquivo."""
        node = self.resolve_path(path)
        if node is None:
            return False, f"Arquivo não encontrado: '{path}'"
        if node.is_dir:
            return False, f"'{path}' é um diretório, use 'ls' para listar seu conteúdo."
            
        info = [
            f"--- Arquivo: {node.get_path()} ---",
            f"Tamanho Lógico      : {node.size_bytes} bytes ({format_bytes(node.size_bytes)})",
            f"Bloco de i-node     : {node.inode_block if node.inode_block is not None else 'N/A'}",
            f"Blocos de Dados     : {node.allocated_blocks}",
            f"Conteúdo Simulado   : {node.content if node.content else '[Arquivo binário / sem conteúdo em texto]'}"
        ]
        return True, "\n".join(info)

    def update_file(self, path: str, new_size_bytes: int, new_content: Optional[str] = None) -> Tuple[bool, str]:
        """Atualiza o tamanho e/ou conteúdo de um arquivo, realocando blocos no disco."""
        node = self.resolve_path(path)
        if node is None:
            return False, f"Arquivo não encontrado: '{path}'"
        if node.is_dir:
            return False, f"'{path}' é um diretório."
            
        old_size = node.size_bytes
        success = self.strategy.resize(node, new_size_bytes)
        if not success:
            return False, f"Erro ao redimensionar: espaço insuficiente no disco para alocar {format_bytes(new_size_bytes)}."
            
        if new_content is not None:
            node.content = new_content
        node.modified_at = time.time()
        
        return True, (
            f"Arquivo '{node.get_path()}' atualizado: {format_bytes(old_size)} -> {format_bytes(new_size_bytes)} "
            f"({len(node.allocated_blocks)} blocos)."
        )

    def delete_node(self, path: str, recursive: bool = False) -> Tuple[bool, str]:
        """Deleta arquivo ou diretório (com liberação de blocos físicos no disco)."""
        node = self.resolve_path(path)
        if node is None:
            return False, f"Item não encontrado: '{path}'"
        if node == self.root:
            return False, "Não é permitido deletar o diretório raiz '/'."
            
        parent = node.parent
        if node.is_dir:
            if node.children and not recursive:
                return False, f"Diretório '{path}' não está vazio. Use -r / recursivo para deletar."
            # Deleta recursivamente todos os filhos
            for child_name in list(node.children.keys()):
                self.delete_node(node.children[child_name].get_path(), recursive=True)
            del parent.children[node.name]
            return True, f"Diretório '{path}' removido com sucesso."
        else:
            # Libera blocos físicos do arquivo
            self.strategy.deallocate(node)
            del parent.children[node.name]
            parent.modified_at = time.time()
            return True, f"Arquivo '{path}' removido e blocos liberados no disco."

    # -------------------------------------------------------------------------
    # VISUALIZAÇÃO EM ÁRVORE E LISTAGEM
    # -------------------------------------------------------------------------

    def list_dir(self, path: str = "") -> List[str]:
        """Lista os itens de um diretório."""
        node = self.resolve_path(path) if path else self.current_dir
        if node is None:
            return [f"Caminho não encontrado: '{path}'"]
        if not node.is_dir:
            return [f"'{path}' é um arquivo: {node.name} ({format_bytes(node.size_bytes)})"]
            
        lines = []
        for name, child in sorted(node.children.items()):
            if child.is_dir:
                lines.append(f"  [DIR] {name}/")
            else:
                lines.append(f"  [ARQ] {name} ({format_bytes(child.size_bytes)}) - Blocos: {child.allocated_blocks}")
        if not lines:
            lines.append("  (diretório vazio)")
        return lines

    def get_tree_lines(self, node: Optional[FSNode] = None, prefix: str = "", is_last: bool = True) -> List[str]:
        """
        Gera a árvore hierárquica formatada identicamente ao padrão de saída pedido:
        /
        ├── sistema/ [DIR]
        │   └── logs/ [DIR]
        │       └── app.log (10 KB) [ARQ]
        """
        lines = []
        if node is None:
            node = self.root
            lines.append("[ÁRVORE DO SISTEMA DE ARQUIVOS]")
            lines.append("/")
            children = list(sorted(node.children.values(), key=lambda n: n.name))
            for i, child in enumerate(children):
                # Se houver apenas 1 filho ou não for o último, formata com ├── para bater com o enunciado
                last = (i == len(children) - 1) and (len(children) > 1)
                lines.extend(self.get_tree_lines(child, prefix="", is_last=last))
            return lines

        branch = "└── " if is_last else "├── "
        tag = "[DIR]" if node.is_dir else "[ARQ]"
        size_str = f" ({format_bytes(node.size_bytes)})" if node.is_file else ""
        name_display = f"{node.name}/" if node.is_dir else node.name
        
        lines.append(f"{prefix}{branch}{name_display}{size_str} {tag}")
        
        if node.is_dir:
            next_prefix = prefix + ("    " if is_last else "│   ")
            children = list(sorted(node.children.values(), key=lambda n: n.name))
            for i, child in enumerate(children):
                last = (i == len(children) - 1)
                lines.extend(self.get_tree_lines(child, next_prefix, last))
                
        return lines

    def get_all_nodes(self, node: Optional[FSNode] = None, include_dirs: bool = False) -> List[FSNode]:
        """Retorna todos os nós do sistema recursivamente."""
        if node is None:
            node = self.root
        result = []
        if node.is_file or (include_dirs and node != self.root):
            result.append(node)
        if node.is_dir:
            for child in node.children.values():
                result.extend(self.get_all_nodes(child, include_dirs))
        return result

    # -------------------------------------------------------------------------
    # DIAGNÓSTICO DO DISCO E ANÁLISE DE FRAGMENTAÇÃO
    # -------------------------------------------------------------------------

    def get_disk_status(self, details: bool = True) -> str:
        """
        Gera o mapa detalhado de alocação de blocos e o relatório completo
        de fragmentação interna, fragmentação externa e necessidade de compactação.
        """
        lines = []
        bs_str = format_bytes(self.block_size)
        total_cap_str = format_bytes(self.disk.total_capacity)
        
        lines.append(f"Tamanho do Bloco de Disco: {bs_str} | Total de Blocos: {self.total_blocks} ({total_cap_str})")
        lines.append("")
        
        # Mapa de alocação
        strat_display = "Indexado" if isinstance(self.strategy, IndexedAllocation) else (
            "Contíguo" if isinstance(self.strategy, ContiguousAllocation) else "Encadeado"
        )
        lines.append(f"[MAPA DE ALOCAÇÃO DO DISCO ({strat_display})]")
        
        # Agrupa blocos contíguos livres se houver muitos
        i = 0
        while i < self.total_blocks:
            b = self.disk.blocks[i]
            if b.is_free:
                # Verifica extensão de livres consecutivos
                start_free = i
                while i < self.total_blocks and self.disk.blocks[i].is_free:
                    i += 1
                end_free = i - 1
                if start_free == end_free:
                    lines.append(f"Bloco {start_free:02d} [LIVRE]")
                else:
                    lines.append(f"Bloco {start_free:02d}..{end_free:02d}           : [LIVRE]")
            else:
                tag = f"[{b.block_type}]"
                if "INODE" in b.block_type:
                    owner_desc = f"Diretório '{b.owner_path}'" if b.block_type in (BlockType.INODE_ROOT, BlockType.INODE_DIR) else f"Arquivo '{b.owner_path}'"
                    lines.append(f"Bloco {b.index:02d} {tag:<14}: {owner_desc}")
                else:
                    # Bloco de dado
                    lines.append(
                        f"Bloco {b.index:02d} {tag:<14}: '{b.owner_path}' "
                        f"(Bloco {b.file_block_index} - {b.bytes_used} bytes ocupados)"
                    )
                i += 1

        # Barra visual gráfica de blocos do disco
        lines.append("")
        visual_bar = []
        for b in self.disk.blocks:
            if b.is_free:
                visual_bar.append("[░]")  # Bloco livre
            elif "INODE" in b.block_type:
                visual_bar.append("[◆]")  # Bloco de i-node
            else:
                visual_bar.append("[■]")  # Bloco de dados
        lines.append("Visualização do Disco: " + "".join(visual_bar))
        lines.append("Legenda: [◆] i-node | [■] Dado ocupado | [░] Livre")
        lines.append("")

        # ---------------------------------------------------------------------
        # RELATÓRIO DE FRAGMENTAÇÃO
        # ---------------------------------------------------------------------
        lines.append("--- RELATÓRIO DE FRAGMENTAÇÃO ---")
        
        all_files = self.get_all_nodes(include_dirs=False)
        total_real_size = sum(f.size_bytes for f in all_files)
        total_allocated_data = sum(len(f.allocated_blocks) * self.block_size for f in all_files)
        total_internal_frag = 0
        
        # Fragmentação Interna detalhada por arquivo
        if all_files:
            for f in all_files:
                if not f.allocated_blocks:
                    continue
                file_alloc_space = len(f.allocated_blocks) * self.block_size
                last_block_idx = f.allocated_blocks[-1]
                last_block = self.disk.blocks[last_block_idx]
                frag_in_file = self.block_size - last_block.bytes_used
                total_internal_frag += frag_in_file
                
                pct = (frag_in_file / self.block_size) * 100 if self.block_size > 0 else 0
                lines.append(f"Tamanho Real do Arquivo '{f.name}': {f.size_bytes} bytes ({format_bytes(f.size_bytes)})")
                lines.append(f"Espaço Alocado no Disco          : {file_alloc_space} bytes ({len(f.allocated_blocks)} blocos de {format_bytes(self.block_size)})")
                lines.append(f"Fragmentação Interna             : {frag_in_file} bytes ({pct:.0f}% de desperdício no Bloco {last_block_idx:02d})")
        else:
            lines.append("Nenhum arquivo armazenado no sistema.")
            
        # Fragmentação Externa
        free_blocks = [b.index for b in self.disk.blocks if b.is_free]
        total_free_bytes = len(free_blocks) * self.block_size
        
        # Calcula fragmentos contíguos livres
        free_streaks = []
        curr_streak = 0
        for b in self.disk.blocks:
            if b.is_free:
                curr_streak += 1
            else:
                if curr_streak > 0:
                    free_streaks.append(curr_streak)
                    curr_streak = 0
        if curr_streak > 0:
            free_streaks.append(curr_streak)
            
        max_contiguous_free = max(free_streaks) if free_streaks else 0
        
        if isinstance(self.strategy, ContiguousAllocation):
            # Na alocação contígua, se há blocos livres mas o maior bloco contíguo é menor que o total livre,
            # há fragmentação externa
            external_frag_blocks = len(free_blocks) - max_contiguous_free if len(free_streaks) > 1 else 0
            external_frag_bytes = external_frag_blocks * self.block_size
            need_compact = external_frag_bytes > 0
            lines.append(f"Fragmentação Externa             : {external_frag_bytes} bytes ({external_frag_blocks} blocos dispersos em {len(free_streaks)} segmentos)")
            if need_compact:
                lines.append("Necessidade de Compactação       : SIM (Existem blocos livres dispersos não-contíguos)")
            else:
                lines.append("Necessidade de Compactação       : NÃO (Espaço livre está consolidado)")
        else:
            # Na alocação indexada ou encadeada, não há fragmentação externa porque qualquer bloco livre pode ser usado
            lines.append("Fragmentação Externa             : 0 bytes")
            strat_label = "i-node indexado" if isinstance(self.strategy, IndexedAllocation) else "lista encadeada"
            lines.append(f"Necessidade de Compactação       : NÃO (Blocos alocados via {strat_label})")
            
        return "\n".join(lines)

    def compact_disk(self) -> Tuple[bool, str]:
        """
        Compacta o disco (Defrag): desloca todos os blocos ocupados para o início,
        deixando um único bloco contíguo de espaço livre no final.
        Especialmente útil e visual na Alocação Contígua!
        """
        used_blocks = [b for b in self.disk.blocks if not b.is_free]
        if not used_blocks:
            return True, "Disco vazio; compactação não necessária."
            
        # Reatribui blocos
        all_files = self.get_all_nodes(include_dirs=True)
        # Salva dados
        snapshot = []
        for b in used_blocks:
            snapshot.append({
                "type": b.block_type,
                "owner": b.owner_path,
                "used": b.bytes_used,
                "file_idx": b.file_block_index,
                "content": b.content
            })
            
        # Limpa tudo
        for b in self.disk.blocks:
            b.free()
            
        # Grava contiguamente a partir do bloco 0
        for i, snap in enumerate(snapshot):
            self.disk.blocks[i].allocate(
                block_type=snap["type"],
                owner_path=snap["owner"],
                bytes_used=snap["used"],
                file_block_index=snap["file_idx"],
                content=snap["content"]
            )
            # Atualiza referências dos nós
            node = self.resolve_path(snap["owner"])
            if node:
                if "INODE" in snap["type"]:
                    node.inode_block = i
                else:
                    if snap["file_idx"] == 1:
                        node.allocated_blocks = [i]
                    else:
                        node.allocated_blocks.append(i)
                        
        return True, "Compactação de disco concluída com sucesso! Todos os blocos livres estão contíguos."


# =============================================================================
# INTERFACE CLI INTERATIVA / PROMPT DE COMANDOS
# =============================================================================

def print_banner():
    banner = """
================================================================================
   SIMULADOR DE SISTEMA DE ARQUIVOS - SISTEMAS OPERACIONAIS (UFRPE)
   Entrega Parcial 01 | Discentes: Luiz Maranhão & Mário Jorge
================================================================================
 Comandos disponíveis:
   mkdir <caminho>                     Criar diretório
   create <caminho> [--size <tam>]     Criar arquivo com tamanho (ex: 10KB, 4096B)
   read / cat <caminho>                Ler metadados/conteúdo do arquivo
   update <caminho> --size <novo_tam>  Atualizar tamanho do arquivo
   rm <caminho>                        Deletar arquivo e liberar blocos
   rmdir <caminho> [-r]                Deletar diretório (com -r para recursivo)
   ls [caminho]                        Listar conteúdo do diretório
   cd <caminho>                        Navegar para diretório (absoluto ou relativo)
   pwd                                 Exibir diretório corrente
   tree                                Exibir árvore hierárquica do sistema
   fs_status [--details]               Exibir mapa do disco e análise de fragmentação
   strategy [indexada|contigua|encadeada]  Alternar estratégia de alocação
   compact                             Executar compactação/desfragmentação do disco
   format [--block-size <tam>] [--total-blocks <num>]  Formatar disco
   demo                                Executar demonstração dos Exemplos 1.1 e 1.2
   help                                Exibir esta ajuda
   exit / quit                         Sair do simulador
================================================================================
"""
    print(banner)


def run_demo(fs: FileSystem):
    """Executa a demonstração automatizada dos Exemplos 1.1 e 1.2 pedidos pelo professor."""
    print("\n" + "=" * 75)
    print(">>> INICIANDO DEMONSTRAÇÃO AUTOMÁTICA DOS EXEMPLOS DO ENUNCIADO <<<")
    print("=" * 75)
    
    # Formata como Alocação Indexada de 16 blocos de 4 KB
    print("\n[PASSO 1] Configurando disco com 16 blocos de 4 KB (Alocação Indexada)...")
    fs.__init__(block_size=4096, total_blocks=16, strategy_name=AllocationStrategyName.INDEXED)
    
    print("\n> mkdir /sistema")
    ok, msg = fs.mkdir("/sistema")
    print(msg)
    
    print("> mkdir /sistema/logs")
    ok, msg = fs.mkdir("/sistema/logs")
    print(msg)
    
    print("> create /sistema/logs/app.log --size 10KB")
    ok, msg = fs.create_file("/sistema/logs/app.log", parse_size_to_bytes("10KB"))
    print(msg)
    
    print("\n" + "-" * 40)
    print("Exemplo 1.1 — Criação e Exibição da Árvore Hierárquica:")
    print("-" * 40)
    for line in fs.get_tree_lines():
        print(line)
        
    print("\n" + "-" * 40)
    print("Exemplo 1.2 — Alocação Indexada e Análise de Fragmentação:")
    print("> fs_status --details")
    print("-" * 40)
    print(fs.get_disk_status(details=True))
    
    print("\n" + "=" * 75)
    print(">>> DEMONSTRAÇÃO EXTRA: ALOCAÇÃO CONTÍGUA E FRAGMENTAÇÃO EXTERNA <<<")
    print("=" * 75)
    print("Formatando disco novo em modo 'Contígua' (16 blocos de 4 KB)...")
    fs = FileSystem(block_size=4096, total_blocks=16, strategy_name=AllocationStrategyName.CONTIGUOUS)
    
    print("\n[PASSO 1] Preenchendo o disco com 4 arquivos contíguos:")
    fs.create_file("/arqA.bin", 16384)  # 4 blocos (0..3)
    fs.create_file("/arqB.bin", 8192)   # 2 blocos (4..5)
    fs.create_file("/arqC.bin", 24576)  # 6 blocos (6..11)
    fs.create_file("/arqD.bin", 8192)   # 2 blocos (12..13)
    # Sobram 2 blocos livres no final (14..15)
    print("Arquivos criados: arqA (4 blk), arqB (2 blk), arqC (6 blk), arqD (2 blk).")
    print("Total ocupado: 14 blocos. Livres no final: 2 blocos (14..15).")
    
    print("\n[PASSO 2] Deletando 'arqB.bin' (blocos 4..5) para abrir um 'buraco' no meio:")
    fs.delete_node("/arqB.bin")
    print("Agora temos 4 blocos livres no total: 2 blocos dispersos em 4..5 e 2 blocos em 14..15.")
    
    print("\n[PASSO 3] Tentando criar 'novo_app.bin' de 16 KB (necessita de 4 blocos contíguos):")
    print("Nota: Há 16 KB livres no total, mas dispersos em pedaços de 8 KB!")
    ok, msg = fs.create_file("/novo_app.bin", 16384)
    print(f">> Resultado da alocação: {msg}")
    
    print("\n[PASSO 4] Diagnóstico do disco revelando FRAGMENTAÇÃO EXTERNA:")
    print(fs.get_disk_status(details=True))
    
    print("\n[PASSO 5] Executando 'compact' (Desfragmentação do Disco):")
    ok, msg = fs.compact_disk()
    print(f">> {msg}")
    
    print("\n[PASSO 6] Diagnóstico do disco APÓS Compactação (blocos livres consolidados):")
    print(fs.get_disk_status(details=True))
    
    print("\n[PASSO 7] Tentando novamente alocar 'novo_app.bin' de 16 KB após compactação:")
    ok, msg = fs.create_file("/novo_app.bin", 16384)
    print(f">> Resultado da alocação: {msg}")
    
    print("\n[PASSO 8] Status final com 'novo_app.bin' alocado com sucesso:")
    print(fs.get_disk_status(details=True))
    print("\n" + "=" * 75)
    print(">>> FIM DA DEMONSTRAÇÃO <<<")
    print("=" * 75 + "\n")


def main():
    fs = FileSystem(block_size=4096, total_blocks=16, strategy_name=AllocationStrategyName.INDEXED)
    
    # Se chamado com argumento --demo
    if len(sys.argv) > 1 and sys.argv[1] in ("--demo", "-d", "demo"):
        run_demo(fs)
        return
        
    print_banner()
    
    while True:
        try:
            prompt = f"fs_sim:{fs.current_dir.get_path()} [{fs.strategy.get_name()}]> "
            cmd_line = input(prompt).strip()
            if not cmd_line:
                continue
                
            parts = cmd_line.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            if cmd in ("exit", "quit", "sair"):
                print("Encerrando Simulador de Sistema de Arquivos. Até mais!")
                break
                
            elif cmd == "help":
                print_banner()
                
            elif cmd == "demo":
                run_demo(fs)
                
            elif cmd == "pwd":
                print(fs.current_dir.get_path())
                
            elif cmd == "cd":
                path = args[0] if args else "/"
                ok, msg = fs.change_dir(path)
                if not ok:
                    print(f"Erro: {msg}")
                    
            elif cmd == "mkdir":
                if not args:
                    print("Uso: mkdir <caminho>")
                    continue
                path = args[0]
                ok, msg = fs.mkdir(path)
                print(msg if ok else f"Erro: {msg}")
                
            elif cmd == "create":
                # create <path> [--size <tam>] [--content <texto>]
                if not args:
                    print("Uso: create <caminho> [--size <tam>] [--content <texto>]")
                    continue
                path = args[0]
                size_bytes = 4096  # padrão 4 KB se não informado
                content = ""
                
                i = 1
                while i < len(args):
                    if args[i] == "--size" and i + 1 < len(args):
                        size_bytes = parse_size_to_bytes(args[i + 1])
                        i += 2
                    elif args[i] == "--content" and i + 1 < len(args):
                        content = " ".join(args[i + 1:])
                        if size_bytes == 4096:
                            size_bytes = len(content.encode("utf-8"))
                        break
                    else:
                        # Se passou apenas um número ou string direta de tamanho
                        try:
                            size_bytes = parse_size_to_bytes(args[i])
                        except ValueError:
                            pass
                        i += 1
                        
                ok, msg = fs.create_file(path, size_bytes, content)
                print(msg if ok else f"Erro: {msg}")
                
            elif cmd in ("cat", "read"):
                if not args:
                    print("Uso: cat <caminho>")
                    continue
                ok, msg = fs.read_file(args[0])
                print(msg)
                
            elif cmd == "update":
                # update <caminho> --size <novo_tam>
                if not args or len(args) < 2:
                    print("Uso: update <caminho> --size <novo_tamanho>")
                    continue
                path = args[0]
                new_size = None
                if "--size" in args:
                    idx = args.index("--size")
                    if idx + 1 < len(args):
                        new_size = parse_size_to_bytes(args[idx + 1])
                if new_size is None:
                    print("Erro: especifique --size <novo_tamanho> (ex: 8KB)")
                    continue
                ok, msg = fs.update_file(path, new_size)
                print(msg if ok else f"Erro: {msg}")
                
            elif cmd == "rm":
                if not args:
                    print("Uso: rm <caminho_arquivo>")
                    continue
                ok, msg = fs.delete_node(args[0])
                print(msg if ok else f"Erro: {msg}")
                
            elif cmd == "rmdir":
                if not args:
                    print("Uso: rmdir [-r] <caminho_diretorio>")
                    continue
                recursive = "-r" in args
                clean_args = [a for a in args if a != "-r"]
                if not clean_args:
                    print("Uso: rmdir [-r] <caminho_diretorio>")
                    continue
                ok, msg = fs.delete_node(clean_args[0], recursive=recursive)
                print(msg if ok else f"Erro: {msg}")
                
            elif cmd == "ls":
                path = args[0] if args else ""
                lines = fs.list_dir(path)
                for l in lines:
                    print(l)
                    
            elif cmd == "tree":
                for line in fs.get_tree_lines():
                    print(line)
                    
            elif cmd in ("fs_status", "status", "df"):
                details = "--details" in args or "-d" in args or len(args) == 0
                print(fs.get_disk_status(details=details))
                
            elif cmd == "strategy":
                if not args:
                    print(f"Estratégia atual: {fs.strategy.get_name()}")
                    print("Estratégias disponíveis: indexada, contigua, encadeada")
                    continue
                strat = args[0].lower()
                try:
                    fs.set_strategy(strat)
                    print(f"Estratégia de alocação alterada para: {fs.strategy.get_name()}")
                except ValueError as e:
                    print(f"Erro: {e}")
                    
            elif cmd in ("compact", "defrag"):
                ok, msg = fs.compact_disk()
                print(msg)
                
            elif cmd == "format":
                bs = 4096
                tb = 16
                st = fs.strategy_name
                i = 0
                while i < len(args):
                    if args[i] == "--block-size" and i + 1 < len(args):
                        bs = parse_size_to_bytes(args[i + 1])
                        i += 2
                    elif args[i] == "--total-blocks" and i + 1 < len(args):
                        tb = int(args[i + 1])
                        i += 2
                    elif args[i] == "--strategy" and i + 1 < len(args):
                        st = args[i + 1]
                        i += 2
                    else:
                        i += 1
                fs = FileSystem(block_size=bs, total_blocks=tb, strategy_name=st)
                print(f"Disco formatado: {tb} blocos de {format_bytes(bs)} ({format_bytes(bs * tb)}) | Estratégia: {fs.strategy.get_name()}")
                
            else:
                print(f"Comando não reconhecido: '{cmd}'. Digite 'help' para listar comandos.")
                
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando Simulador de Sistema de Arquivos.")
            break
        except Exception as e:
            print(f"Erro na execução: {e}")


if __name__ == "__main__":
    main()
