"""
Sistema de Gestão de Manutenção de Frota - ALS
Ponto de entrada principal com interface moderna Windows 11 (PySide6 + QFluentWidgets)
Suporta execução direta do aplicativo e modo servidor Streamlit embutido
"""
import sys
import os

# Adiciona diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.app_qt import main

if __name__ == "__main__":
    # Intercepta execução do servidor analítico Streamlit quando invocado como subprocesso
    if len(sys.argv) > 1 and sys.argv[1] == "--run-streamlit":
        from streamlit.web import cli as stcli
        base_dir = getattr(sys, '_MEIPASS', BASE_DIR)
        script_path = os.path.join(base_dir, "src", "dashboard_streamlit.py")
        sys.argv = ["streamlit", "run", script_path] + sys.argv[2:]
        sys.exit(stcli.main())
    else:
        main()
