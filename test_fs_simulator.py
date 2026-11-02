#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atalho raiz para execução da suíte de testes unitários do Simulador (Entrega Parcial 01)
UFRPE - Sistemas Operacionais | Discentes: Luiz Maranhão & Mário Jorge
"""
import os
import sys
import unittest

sim_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Simulador_Sistema_Arquivos")
sys.path.insert(0, sim_dir)

from test_fs_simulator import TestFileSystem

if __name__ == "__main__":
    unittest.main()
