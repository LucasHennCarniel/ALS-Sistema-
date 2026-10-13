"""
Tela de Carregamento (Splash Screen) Moderna em Fluent Design
Exibe a logo ALS, barra de progresso fluida e checa integridade e atualizacoes em segundo plano.
"""
import os
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QIcon, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import IndeterminateProgressBar, TitleLabel, SubtitleLabel, CaptionLabel, setThemeColor

from src.services.updater_service import CheckUpdateThread, UpdateInfo


class ModernSplashScreen(QWidget):
    """Tela de Abertura Fluent com verificacao assincrona de atualizacoes"""
    concluido = Signal(object)  # Emite UpdateInfo ou None

    def __init__(self, token=None, parent=None):
        super().__init__(parent)
        self.token = token
        self.update_info = None
        self._init_ui()
        self._iniciar_checagem()

    def _init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(480, 320)

        # Container principal com bordas arredondadas e sombra suave
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.card = QWidget(self)
        self.card.setStyleSheet("""
            QWidget {
                background-color: #F3F6F9;
                border: 1px solid #D0D7DE;
                border-radius: 16px;
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 25, 30, 25)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignCenter)

        # Logotipo da ALS
        self.lbl_logo = QLabel(self.card)
        self.lbl_logo.setAlignment(Qt.AlignCenter)
        caminho_logo = os.path.abspath("img/logo ALS.png")
        if os.path.exists(caminho_logo):
            pixmap = QPixmap(caminho_logo).scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo.setPixmap(pixmap)
        card_layout.addWidget(self.lbl_logo)

        # Titulo e Subtitulo
        lbl_titulo = TitleLabel("Sistema ALS", self.card)
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        card_layout.addWidget(lbl_titulo)

        self.lbl_status = CaptionLabel("Inicializando e verificando atualizações...", self.card)
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: #64748B; font-size: 12px;")
        card_layout.addWidget(self.lbl_status)

        # Barra de Progresso Fluida Indeterminada
        self.progress = IndeterminateProgressBar(self.card)
        self.progress.setFixedWidth(340)
        card_layout.addWidget(self.progress, alignment=Qt.AlignCenter)

        layout.addWidget(self.card)

    def _iniciar_checagem(self):
        setThemeColor('#4CAF50')
        # Thread de checagem
        self.thread = CheckUpdateThread(self.token, self)
        self.thread.resultado.connect(self._on_resultado)
        self.thread.start()

        # Timeout de seguranca (maximo 1.5s para nao atrasar a abertura se a rede estiver lenta)
        self.timer_timeout = QTimer(self)
        self.timer_timeout.setSingleShot(True)
        self.timer_timeout.timeout.connect(self._finalizar)
        self.timer_timeout.start(1500)

    def _on_resultado(self, info: UpdateInfo):
        self.update_info = info
        # Pequeno atraso estetico para a animacao rodar de forma fluida
        QTimer.singleShot(400, self._finalizar)

    def _finalizar(self):
        if self.timer_timeout.isActive():
            self.timer_timeout.stop()
        self.concluido.emit(self.update_info)
        self.close()
