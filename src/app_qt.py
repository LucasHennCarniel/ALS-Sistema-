"""
Ponto de entrada da aplicação moderna (PySide6 + QFluentWidgets)
"""
import sys
import os

# Adiciona o diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.controllers.manutencao_controller import ManutencaoController
from src.controllers.veiculo_controller import VeiculoController
from src.controllers.destino_controller import DestinoController
from src.controllers.nota_controller import NotaController
from src.views_qt.main_window import MainWindow


def main():
    # Habilitar High DPI scaling no Windows
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema ALS")
    app.setOrganizationName("ALS Transportes")
    
    # Inicializa os Controllers
    manutencao_ctrl = ManutencaoController()
    veiculo_ctrl = VeiculoController()
    destino_ctrl = DestinoController()
    nota_ctrl = NotaController()
    
    # Cria e exibe a janela moderna
    window = MainWindow(manutencao_ctrl, veiculo_ctrl, destino_ctrl, nota_ctrl)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
