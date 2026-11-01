#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atalho raiz para execução do Simulador de Sistema de Arquivos (Entrega Parcial 01)
UFRPE - Sistemas Operacionais | Discentes: Luiz Maranhão & Mário Jorge
"""
import os
import sys

sim_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Simulador_Sistema_Arquivos")
sys.path.insert(0, sim_dir)

from fs_simulator import main

if __name__ == "__main__":
    main()
