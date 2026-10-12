"""
Sistema de Gestão de Manutenção de Frota - ALS
Ponto de entrada principal com interface moderna Windows 11 (PySide6 + QFluentWidgets)
"""
import sys
import os

# Adiciona diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.app_qt import main

if __name__ == "__main__":
    main()
