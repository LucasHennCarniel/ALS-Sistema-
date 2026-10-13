"""
Diálogos Modernos de Notificação de Atualização e Barra de Progresso de Download
Construídos com QFluentWidgets seguindo os padrões do Windows 11 Fluent Design.
"""
import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from qfluentwidgets import (
    PushButton, PrimaryPushButton, ProgressBar, SubtitleLabel,
    BodyLabel, CaptionLabel, InfoBadge, InfoBadgePosition
)

from src.config import APP_VERSION
from src.services.updater_service import UpdateInfo, DownloadUpdateThread, UpdaterService


class UpdateNotificationDialog(QDialog):
    """Modal moderno de exibição de nova versão com suporte a flag [OBRIGATORIA]"""

    def __init__(self, update_info: UpdateInfo, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.aceitou_atualizar = False
        self._init_ui()

    def _init_ui(self):
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        if self.update_info.obrigatoria:
            # Impede fechar a janela pelo 'X' se for obrigatória
            self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        self.setWindowTitle("Atualização do Sistema ALS")
        self.setFixedSize(540, 420)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Cabeçalho com título e badge
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        if self.update_info.obrigatoria:
            titulo = SubtitleLabel("Atualização Obrigatória do Sistema", self)
            titulo.setStyleSheet("color: #DC2626; font-weight: bold;")
        else:
            titulo = SubtitleLabel("Nova Versão Disponível", self)
            titulo.setStyleSheet("color: #1E293B; font-weight: bold;")
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Subtítulo explicativo
        msg = (
            f"Uma nova versão ({self.update_info.versao}) está pronta para instalação.\n"
            f"Sua versão atual: v{APP_VERSION}."
        )
        if self.update_info.obrigatoria:
            msg += (
                "\n\nEsta versão contém alterações estruturais no banco de dados e regras de "
                "negócio essenciais. Para garantir a segurança dos dados, é necessário atualizar."
            )
        lbl_msg = BodyLabel(msg, self)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet("color: #475569; font-size: 13px;")
        layout.addWidget(lbl_msg)

        # Caixa com notas de versão (Changelog)
        layout.addWidget(CaptionLabel("O que mudou nesta versão:", self))
        self.txt_notas = QTextEdit(self)
        self.txt_notas.setReadOnly(True)
        self.txt_notas.setPlainText(self.update_info.notas_versao)
        self.txt_notas.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 10px;
                color: #334155;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.txt_notas)

        # Barra de botões inferior
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        if self.update_info.obrigatoria:
            self.btn_cancelar = PushButton("Fechar Sistema", self)
            self.btn_cancelar.clicked.connect(self._fechar_aplicacao)
        else:
            self.btn_cancelar = PushButton("Lembrar Mais Tarde", self)
            self.btn_cancelar.clicked.connect(self.reject)

        self.btn_atualizar = PrimaryPushButton("Atualizar Sistema Agora", self)
        self.btn_atualizar.setStyleSheet("background-color: #4CAF50; border-color: #4CAF50;")
        self.btn_atualizar.clicked.connect(self._confirmar_atualizacao)

        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_atualizar)
        layout.addLayout(btn_layout)

    def _confirmar_atualizacao(self):
        self.aceitou_atualizar = True
        self.accept()

    def _fechar_aplicacao(self):
        sys.exit(0)


class DownloadProgressDialog(QDialog):
    """Diálogo de progresso em tempo real durante o download do instalador"""

    def __init__(self, update_info: UpdateInfo, token=None, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.token = token
        self._init_ui()
        self._iniciar_download()

    def _init_ui(self):
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        self.setWindowTitle("Baixando Atualização")
        self.setFixedSize(460, 210)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        layout.addWidget(SubtitleLabel("Preparando Atualização...", self))

        self.lbl_status = BodyLabel("Iniciando download e criando backup de segurança...", self)
        self.lbl_status.setStyleSheet("color: #475569;")
        layout.addWidget(self.lbl_status)

        # Barra de progresso percentual (0 a 100%)
        self.progresso = ProgressBar(self)
        self.progresso.setValue(0)
        layout.addWidget(self.progresso)

        self.lbl_info = CaptionLabel(
            "Após o download, o instalador será iniciado automaticamente sem apagar seus dados.", self
        )
        self.lbl_info.setStyleSheet("color: #64748B;")
        layout.addWidget(self.lbl_info)

    def _iniciar_download(self):
        temp_dir = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "ALS_Update")
        destino = os.path.join(temp_dir, "Instalador_SistemaALS_Setup.exe")

        self.thread = DownloadUpdateThread(
            download_url=self.update_info.download_url,
            destino_path=destino,
            token=self.token,
            parent=self
        )
        self.thread.progresso.connect(self._on_progresso)
        self.thread.sucesso.connect(self._on_sucesso)
        self.thread.falha.connect(self._on_falha)
        self.thread.start()

    def _on_progresso(self, pct: int):
        self.progresso.setValue(pct)
        self.lbl_status.setText(f"Baixando nova versão: {pct}% concluído...")

    def _on_sucesso(self, caminho_instalador: str):
        self.lbl_status.setText("Download concluído! Iniciando instalação...")
        self.progresso.setValue(100)
        UpdaterService.aplicar_atualizacao(caminho_instalador)

    def _on_falha(self, mensagem: str):
        self.lbl_status.setText(f"Erro: {mensagem}")
        self.lbl_status.setStyleSheet("color: #DC2626;")
        btn_fechar = PushButton("Fechar", self)
        btn_fechar.clicked.connect(self.reject)
        self.layout().addWidget(btn_fechar)
