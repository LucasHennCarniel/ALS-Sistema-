"""
Ponto de entrada da aplicação moderna (PySide6 + QFluentWidgets)
Com Splash Screen animada e verificação de auto-atualização assíncrona
"""
import sys
import os
import tempfile
import logging
import faulthandler

# Adiciona o diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QLockFile, QTimer

from qfluentwidgets import setTheme, Theme
from src.config import DATA_DIR, APP_VERSION
from src.views_qt.splash_screen import ModernSplashScreen


def _configurar_log():
    """Log em data/logs/als.log (funciona no .exe sem console) + dump de travamentos"""
    pasta = os.path.join(DATA_DIR, "logs")
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, "als.log")
    logging.basicConfig(
        filename=caminho, level=logging.INFO, encoding="utf-8",
        format="%(asctime)s %(levelname)s %(message)s"
    )
    arq_falhas = open(os.path.join(pasta, "faulthandler.log"), "a")
    faulthandler.enable(arq_falhas)
    # Se a abertura passar de 20s, grava a pilha de todas as threads
    faulthandler.dump_traceback_later(20, repeat=False, file=arq_falhas)

    def _excecao(tipo, valor, tb):
        logging.critical("Erro nao tratado", exc_info=(tipo, valor, tb))
    sys.excepthook = _excecao


def main():
    _configurar_log()
    logging.info("Iniciando Sistema ALS v%s (frozen=%s)", APP_VERSION, getattr(sys, "frozen", False))
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
    
    logging.info("QApplication criada")
    # Tema escuro desde a splash (a MainWindow mantem o mesmo padrao)
    setTheme(Theme.DARK)
    # Exibe a SplashScreen animada
    splash = ModernSplashScreen()
    splash.show()
    
    logging.info("Splash exibida")
    estado = {}

    def construir_janela():
        """Cria controllers e janela principal (depois do 1o paint da splash)"""
        if "window" in estado:
            return estado["window"]
        logging.info("Carregando modulos principais")
        # Imports pesados (pandas, SQLAlchemy, QtWebEngine) ficam aqui para a splash aparecer antes
        from src.controllers.manutencao_controller import ManutencaoController
        from src.controllers.veiculo_controller import VeiculoController
        from src.controllers.destino_controller import DestinoController
        from src.controllers.nota_controller import NotaController
        from src.views_qt.main_window import MainWindow
        logging.info("Iniciando controllers")
        manutencao_ctrl = ManutencaoController()
        veiculo_ctrl = VeiculoController()
        destino_ctrl = DestinoController()
        nota_ctrl = NotaController()
        logging.info("Controllers prontos; criando janela principal")
        estado["window"] = MainWindow(manutencao_ctrl, veiculo_ctrl, destino_ctrl, nota_ctrl)
        logging.info("Janela principal criada")
        # A janela foi construida sem travar: o dump de travamento deixa de ser necessario
        faulthandler.cancel_dump_traceback_later()
        return estado["window"]

    def on_splash_concluido(update_info):
        faulthandler.cancel_dump_traceback_later()
        logging.info("Splash concluida; update=%s", getattr(update_info, 'versao', None))
        window = construir_janela()
        if update_info is not None and update_info.disponivel:
            # Usuario adiou: deixa lembrete no menu lateral
            window.exibir_lembrete_atualizacao(update_info)
        window.show()

    splash.concluido.connect(on_splash_concluido)
    QTimer.singleShot(50, construir_janela)
    codigo = app.exec()
    lock.unlock()
    sys.exit(codigo)


if __name__ == "__main__":
    main()
