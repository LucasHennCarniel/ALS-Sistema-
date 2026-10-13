"""
Interface de Dashboard Streamlit embutida no menu lateral do PySide6 (QFluentWidgets)
Visual Corporativo com Ícones Vetoriais Fluent
"""
import os
import sys
import socket
import subprocess
import webbrowser
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from qfluentwidgets import (
    TitleLabel, BodyLabel, PrimaryPushButton, PushButton,
    IconWidget, FluentIcon as FIF, InfoBar
)

from src.views_qt.theme_styles import ContrastCard


class DashboardView(QWidget):
    """View que hospeda o Dashboard Streamlit diretamente dentro do sistema"""
    
    PORTA = 8505
    URL = f"http://localhost:{PORTA}"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processo_streamlit = None
        self.servidor_pronto = False
        
        self._init_ui()
        
        self.timer_check = QTimer(self)
        self.timer_check.setInterval(800)
        self.timer_check.timeout.connect(self._verificar_servidor)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Barra de Topo Corporativa do Dashboard
        self.header_card = ContrastCard(self, cor_acento="#4CAF50")
        header_layout = QHBoxLayout(self.header_card)
        header_layout.setContentsMargins(16, 10, 16, 10)
        header_layout.setSpacing(12)
        
        header_icon = IconWidget(FIF.PIE_SINGLE, self.header_card)
        header_icon.setFixedSize(24, 24)
        header_layout.addWidget(header_icon)
        
        self.title_label = TitleLabel("Dashboard Analítico", self.header_card)
        header_layout.addWidget(self.title_label)
        
        self.status_label = BodyLabel("Inicializando motor gráfico...", self.header_card)
        header_layout.addWidget(self.status_label)
        
        header_layout.addStretch()
        
        self.btn_recarregar = PrimaryPushButton("Atualizar Indicadores", self.header_card, FIF.SYNC)
        self.btn_recarregar.clicked.connect(self.recarregar_dashboard)
        header_layout.addWidget(self.btn_recarregar)
        
        self.btn_navegador = PushButton("Abrir no Navegador", self.header_card, FIF.GLOBE)
        self.btn_navegador.clicked.connect(lambda: webbrowser.open(self.URL))
        header_layout.addWidget(self.btn_navegador)
        
        layout.addWidget(self.header_card)
        
        # Área Web Embutida (QWebEngineView)
        self.web_container = ContrastCard(self)
        web_layout = QVBoxLayout(self.web_container)
        web_layout.setContentsMargins(2, 2, 2, 2)
        
        self.webview = QWebEngineView(self.web_container)
        self.webview.setHtml("""
            <html>
            <body style="background-color:#D5DFE8; color:#1E293B; font-family:'Segoe UI', sans-serif;
                         display:flex; flex-direction:column; align-items:center; justify-content:center; height:90vh; margin:0;">
                <h2 style="margin-bottom:8px; font-weight:600;">Carregando Painel de Indicadores ALS...</h2>
                <p style="color:#475569;">Conectando ao motor analítico e banco de dados SQLite.</p>
            </body>
            </html>
        """)
        web_layout.addWidget(self.webview)
        layout.addWidget(self.web_container, stretch=1)

    def showEvent(self, event):
        """Inicia o servidor Streamlit automaticamente ao abrir a aba Dashboard"""
        super().showEvent(event)
        self.iniciar_servidor_se_necessario()

    def _porta_em_uso(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(('127.0.0.1', self.PORTA)) == 0

    def iniciar_servidor_se_necessario(self):
        if self._porta_em_uso():
            if not self.servidor_pronto:
                self.servidor_pronto = True
                self.status_label.setText("Status: Conectado em tempo real")
                self.webview.setUrl(QUrl(self.URL))
            return

        if self.processo_streamlit is None or self.processo_streamlit.poll() is not None:
            if getattr(sys, 'frozen', False):
                cmd_exec = [sys.executable, "--run-streamlit"]
            else:
                main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
                cmd_exec = [sys.executable, main_py, "--run-streamlit"]

            cmd = cmd_exec + [
                "--server.port", str(self.PORTA),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false",
                "--theme.base", "light",
                "--theme.primaryColor", "#4CAF50",
                "--theme.backgroundColor", "#D5DFE8",
                "--theme.secondaryBackgroundColor", "#C6D0DA",
                "--theme.textColor", "#1E293B"
            ]
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            try:
                self.processo_streamlit = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=creationflags
                )
                self.status_label.setText("Status: Iniciando servidor analítico...")
                self.timer_check.start()
            except Exception as e:
                self.status_label.setText(f"Erro ao iniciar servidor: {e}")

    def _verificar_servidor(self):
        if self._porta_em_uso():
            self.timer_check.stop()
            self.servidor_pronto = True
            self.status_label.setText("Status: Online em tempo real")
            self.webview.setUrl(QUrl(self.URL))

    def recarregar_dashboard(self):
        if self._porta_em_uso():
            self.webview.reload()
            InfoBar.success("Atualizado", "Recarregando indicadores do Dashboard...", parent=self)
        else:
            self.servidor_pronto = False
            self.iniciar_servidor_se_necessario()

    def atualizar_tema_cards(self, _=None):
        self.header_card.atualizar_estilo()
        self.web_container.atualizar_estilo()

    def encerrar_servidor(self):
        self.timer_check.stop()
        if self.processo_streamlit and self.processo_streamlit.poll() is None:
            try:
                if os.name == 'nt':
                    subprocess.run(
                        f"taskkill /F /T /PID {self.processo_streamlit.pid}",
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    self.processo_streamlit.terminate()
            except Exception:
                pass
