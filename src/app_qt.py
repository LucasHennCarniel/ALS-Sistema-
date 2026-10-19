"""
Ponto de entrada da aplicação moderna (PySide6 + QFluentWidgets)
Com Splash Screen animada e verificação de auto-atualização assíncrona
"""
import sys
import os
import tempfile

# Adiciona o diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QLockFile

from src.controllers.manutencao_controller import ManutencaoController
from src.controllers.veiculo_controller import VeiculoController
from src.controllers.destino_controller import DestinoController
from src.controllers.nota_controller import NotaController
from src.views_qt.main_window import MainWindow
from src.views_qt.splash_screen import ModernSplashScreen
from src.views_qt.update_dialog import UpdateNotificationDialog, DownloadProgressDialog


def main():
    # Habilitar High DPI scaling no Windows
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema ALS")
    app.setOrganizationName("ALS Transportes")

    # Instância única: uma segunda abertura do .exe não cria outra janela
    lock = QLockFile(os.path.join(tempfile.gettempdir(), "sistema_als_instancia.lock"))
    lock.setStaleLockTime(0)
    if not lock.tryLock(100):
        return
    
    # Exibe a SplashScreen animada
    splash = ModernSplashScreen()
    splash.show()
    
    # Inicializa os Controllers
    manutencao_ctrl = ManutencaoController()
    veiculo_ctrl = VeiculoController()
    destino_ctrl = DestinoController()
    nota_ctrl = NotaController()
    
    # Instancia a janela principal
    window = MainWindow(manutencao_ctrl, veiculo_ctrl, destino_ctrl, nota_ctrl)
    
    def on_splash_concluido(update_info):
        if update_info is not None and update_info.disponivel:
            dialog = UpdateNotificationDialog(update_info)
            if dialog.exec() == UpdateNotificationDialog.Accepted:
                prog_dialog = DownloadProgressDialog(update_info)
                prog_dialog.exec()
                return
            else:
                # Se não for obrigatória e o usuário adiou, adiciona lembrete no menu
                window.exibir_lembrete_atualizacao(update_info)

        window.show()

    splash.concluido.connect(on_splash_concluido)
    codigo = app.exec()
    lock.unlock()
    sys.exit(codigo)


if __name__ == "__main__":
    main()
