"""
Janela Principal Moderna do Sistema ALS usando QFluentWidgets (Fluent Design)
Com Tema Escuro por padrão (Cinza Suave de Alto Contraste como alternativa) e Dashboard Streamlit no Menu Lateral
"""
import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon as FIF,
    SubtitleLabel, BodyLabel, TitleLabel,
    RadioButton, setTheme, Theme, setThemeColor, isDarkTheme
)

from src.views_qt.manutencao_view import ManutencaoView
from src.views_qt.veiculos_view import VeiculosView
from src.views_qt.notas_view import NotasView
from src.views_qt.dashboard_view import DashboardView
from src.views_qt.theme_styles import ContrastCard, QSS_TABELA_CINZA, QSS_TABELA_ESCURA


class SettingsView(QWidget):
    """Página de Configurações e Tema"""
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self.main_win = main_win
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        layout.addWidget(TitleLabel("Configurações do Sistema", self))
        
        # Card de Tema
        self.card_tema = ContrastCard(self)
        tema_layout = QVBoxLayout(self.card_tema)
        tema_layout.setContentsMargins(20, 16, 20, 16)
        tema_layout.setSpacing(12)
        
        tema_layout.addWidget(SubtitleLabel("Aparência & Tema", self.card_tema))
        tema_layout.addWidget(BodyLabel("Escolha como você prefere visualizar a interface:", self.card_tema))
        
        self.radio_cinza = RadioButton("Modo Padrão Cinza Suave (Alto Contraste ALS)", self.card_tema)
        self.radio_escuro = RadioButton("Modo Escuro (Dark Mode)", self.card_tema)
        
        self.radio_escuro.setChecked(True)
        self.radio_cinza.toggled.connect(lambda c: c and self.main_win.aplicar_modo_cinza())
        self.radio_escuro.toggled.connect(lambda c: c and self.main_win.aplicar_modo_escuro())
        
        tema_layout.addWidget(self.radio_cinza)
        tema_layout.addWidget(self.radio_escuro)
        layout.addWidget(self.card_tema)
        
        # Card Sobre
        self.card_sobre = ContrastCard(self)
        sobre_layout = QVBoxLayout(self.card_sobre)
        sobre_layout.setContentsMargins(20, 16, 20, 16)
        sobre_layout.setSpacing(8)
        
        sobre_layout.addWidget(SubtitleLabel("Sobre o Sistema", self.card_sobre))
        sobre_layout.addWidget(BodyLabel("Sistema de Gestão de Manutenção de Frota - ALS", self.card_sobre))
        sobre_layout.addWidget(BodyLabel("Arquitetura: MVC com SQLite WAL, Dashboard Streamlit e Interface Windows 11 Fluent.", self.card_sobre))
        layout.addWidget(self.card_sobre)
        
        layout.addStretch()

    def atualizar_tema_cards(self, _=None):
        self.card_tema.atualizar_estilo()
        self.card_sobre.atualizar_estilo()


class MainWindow(FluentWindow):
    """Janela Principal com Fluent Design (Windows 11), tema escuro por padrão"""
    
    def __init__(self, manutencao_ctrl, veiculo_ctrl, destino_ctrl, nota_ctrl):
        super().__init__()
        self.manutencao_ctrl = manutencao_ctrl
        self.veiculo_ctrl = veiculo_ctrl
        self.destino_ctrl = destino_ctrl
        self.nota_ctrl = nota_ctrl
        self.modo_atual = "escuro"
        
        self._init_window()
        self._init_navigation()
        self.aplicar_modo_escuro()

    def _init_window(self):
        self.setWindowTitle("Sistema de Gestão de Manutenção - ALS")
        self.resize(1340, 820)
        self.setMinimumSize(1024, 660)
        
        # Desativa efeito Mica branco do Windows 11 e define o fundo cinza nativo
        try:
            self.setMicaEffectEnabled(False)
        except Exception:
            pass
            
        self.setCustomBackgroundColor(QColor("#C6D0DA"), QColor("#181B20"))
        
        icon_path = os.path.abspath("img/logo ALS.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # Cor de destaque da marca ALS (Verde)
        setThemeColor('#4CAF50')

    def _init_navigation(self):
        # 1. Manutenções
        self.manutencao_view = ManutencaoView(
            self.manutencao_ctrl, self.veiculo_ctrl, self.destino_ctrl, self
        )
        self.manutencao_view.setObjectName("manutencao_view")
        self.addSubInterface(
            self.manutencao_view,
            FIF.DOCUMENT,
            "Manutenções",
            NavigationItemPosition.TOP
        )
        
        # 2. Dashboard (Streamlit)
        self.dashboard_view = DashboardView(self)
        self.dashboard_view.setObjectName("dashboard_view")
        self.addSubInterface(
            self.dashboard_view,
            FIF.PIE_SINGLE,
            "Dashboard",
            NavigationItemPosition.TOP
        )
        
        # 3. Veículos
        self.veiculos_view = VeiculosView(self.veiculo_ctrl, self)
        self.veiculos_view.setObjectName("veiculos_view")
        self.addSubInterface(
            self.veiculos_view,
            FIF.CAR,
            "Veículos",
            NavigationItemPosition.TOP
        )
        
        # 4. Notas
        self.notas_view = NotasView(self.nota_ctrl, self)
        self.notas_view.setObjectName("notas_view")
        self.addSubInterface(
            self.notas_view,
            FIF.CHAT,
            "Anotações",
            NavigationItemPosition.TOP
        )
        
        # 5. Botão rápido de alternar Tema Cinza / Escuro
        self.navigationInterface.addItem(
            routeKey="toggle_theme",
            icon=FIF.CONSTRACT,
            text="Alternar Tema",
            onClick=self._alternar_tema,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )
        
        # 6. Configurações (inferior)
        self.settings_view = SettingsView(self, self)
        self.settings_view.setObjectName("settings_view")
        self.addSubInterface(
            self.settings_view,
            FIF.SETTING,
            "Configurações",
            NavigationItemPosition.BOTTOM
        )

    def aplicar_modo_cinza(self):
        """Aplica o Modo Padrão Cinza Suave com alto contraste ALS"""
        self.modo_atual = "cinza"
        setTheme(Theme.LIGHT)
        try:
            self.setMicaEffectEnabled(False)
        except Exception:
            pass
        self.setCustomBackgroundColor(QColor("#C6D0DA"), QColor("#181B20"))
        self.stackedWidget.setStyleSheet("""
            StackedWidget {
                background-color: #D5DFE8;
                border: 1px solid #94A3B8;
                border-right: none;
                border-bottom: none;
                border-top-left-radius: 10px;
            }
        """)
        for view in [self.manutencao_view, self.dashboard_view, self.veiculos_view, self.notas_view, self.settings_view]:
            view.atualizar_tema_cards(QSS_TABELA_CINZA)

    def aplicar_modo_escuro(self):
        """Aplica o Modo Escuro (Dark Mode)"""
        self.modo_atual = "escuro"
        setTheme(Theme.DARK)
        try:
            self.setMicaEffectEnabled(False)
        except Exception:
            pass
        self.setCustomBackgroundColor(QColor("#C6D0DA"), QColor("#181B20"))
        self.stackedWidget.setStyleSheet("""
            StackedWidget {
                background-color: #1E2227;
                border: 1px solid #333842;
                border-right: none;
                border-bottom: none;
                border-top-left-radius: 10px;
            }
        """)
        for view in [self.manutencao_view, self.dashboard_view, self.veiculos_view, self.notas_view, self.settings_view]:
            view.atualizar_tema_cards(QSS_TABELA_ESCURA)

    def _alternar_tema(self):
        if self.modo_atual == "cinza":
            self.settings_view.radio_escuro.setChecked(True)
            self.aplicar_modo_escuro()
        else:
            self.settings_view.radio_cinza.setChecked(True)
            self.aplicar_modo_cinza()

    def exibir_lembrete_atualizacao(self, update_info):
        """Adiciona um botão discreto no menu lateral para atualizar quando desejar"""
        try:
            self.navigationInterface.addItem(
                routeKey="btn_update_badge",
                icon=FIF.SYNC,
                text=f"Nova Versão ({update_info.versao})",
                onClick=lambda: self._abrir_dialogo_atualizacao(update_info),
                selectable=False,
                position=NavigationItemPosition.BOTTOM
            )
        except Exception:
            pass

    def _abrir_dialogo_atualizacao(self, update_info):
        """Abre o diálogo de atualização quando o usuário clica no badge"""
        from src.views_qt.update_dialog import UpdateNotificationDialog, DownloadProgressDialog
        dialog = UpdateNotificationDialog(update_info, self)
        if dialog.exec() == UpdateNotificationDialog.Accepted:
            progress_dialog = DownloadProgressDialog(update_info, parent=self)
            progress_dialog.exec()

    def closeEvent(self, event):
        """Encerra o processo Streamlit em segundo plano ao fechar o aplicativo"""
        try:
            self.dashboard_view.encerrar_servidor()
        except Exception:
            pass
        super().closeEvent(event)

