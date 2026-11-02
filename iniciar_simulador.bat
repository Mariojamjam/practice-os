@echo off
chcp 65001 > nul
title Simulador de Sistema de Arquivos - UFRPE (Sistemas Operacionais)
cls
echo ===============================================================================
echo   Iniciando Simulador de Sistema de Arquivos (UFRPE - Entrega Parcial 01)
echo   Discentes: Luiz Maranhao e Mario Jorge
echo ===============================================================================
echo.
python "%~dp0fs_simulator.py"
pause
