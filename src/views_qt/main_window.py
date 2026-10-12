"""
Janela Principal Moderna do Sistema ALS usando QFluentWidgets (Fluent Design)
"""
import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon as FIF,
    SubtitleLabel, BodyLabel, TitleLabel, SimpleCardWidget,
    RadioButton, setTheme, Theme, setThemeColor, isDarkTheme
)

from src.views_qt.manutencao_view import ManutencaoView
from src.views_qt.veiculos_view import VeiculosView
from src.views_qt.notas_view import NotasView


class SettingsView(QWidget):
    """Página de Configurações e Tema"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        layout.addWidget(TitleLabel("Configurações do Sistema", self))
        
        # Card de Tema
        card_tema = SimpleCardWidget(self)
        tema_layout = QVBoxLayout(card_tema)
        tema_layout.setContentsMargins(20, 16, 20, 16)
        tema_layout.setSpacing(12)
        
        tema_layout.addWidget(SubtitleLabel("Aparência & Tema", card_tema))
        tema_layout.addWidget(BodyLabel("Escolha como você prefere visualizar a interface:", card_tema))
        
        self.radio_claro = RadioButton("Modo Claro (Padrão)", card_tema)
        self.radio_escuro = RadioButton("Modo Escuro (Dark Mode)", card_tema)
        self.radio_auto = RadioButton("Seguir o Sistema Windows", card_tema)
        
        self.radio_claro.setChecked(True)
        self.radio_claro.toggled.connect(lambda c: c and setTheme(Theme.LIGHT))
        self.radio_escuro.toggled.connect(lambda c: c and setTheme(Theme.DARK))
        self.radio_auto.toggled.connect(lambda c: c and setTheme(Theme.AUTO))
        
        tema_layout.addWidget(self.radio_claro)
        tema_layout.addWidget(self.radio_escuro)
        tema_layout.addWidget(self.radio_auto)
        layout.addWidget(card_tema)
        
        # Card Sobre
        card_sobre = SimpleCardWidget(self)
        sobre_layout = QVBoxLayout(card_sobre)
        sobre_layout.setContentsMargins(20, 16, 20, 16)
        sobre_layout.setSpacing(8)
        
        sobre_layout.addWidget(SubtitleLabel("Sobre o Sistema", card_sobre))
        sobre_layout.addWidget(BodyLabel("Sistema de Gestão de Manutenção de Frota - ALS", card_sobre))
        sobre_layout.addWidget(BodyLabel("Arquitetura: MVC com SQLite WAL e Interface Windows 11 Fluent Design.", card_sobre))
        layout.addWidget(card_sobre)
        
        layout.addStretch()


class MainWindow(FluentWindow):
    """Janela Principal com Fluent Design (Windows 11)"""
    
    def __init__(self, manutencao_ctrl, veiculo_ctrl, destino_ctrl, nota_ctrl):
        super().__init__()
        self.manutencao_ctrl = manutencao_ctrl
        self.veiculo_ctrl = veiculo_ctrl
        self.destino_ctrl = destino_ctrl
        self.nota_ctrl = nota_ctrl
        
        self._init_window()
        self._init_navigation()

    def _init_window(self):
        self.setWindowTitle("Sistema de Gestão de Manutenção - ALS")
        self.resize(1260, 780)
        self.setMinimumSize(980, 640)
        
        # Ícone da aplicação
        icon_path = os.path.abspath("img/logo ALS.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # Cor de destaque da marca ALS (Verde Moderno)
        setThemeColor('#4CAF50')
        setTheme(Theme.LIGHT)

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
        
        # 2. Veículos
        self.veiculos_view = VeiculosView(self.veiculo_ctrl, self)
        self.veiculos_view.setObjectName("veiculos_view")
        self.addSubInterface(
            self.veiculos_view,
            FIF.CAR,
            "Veículos",
            NavigationItemPosition.TOP
        )
        
        # 3. Notas
        self.notas_view = NotasView(self.nota_ctrl, self)
        self.notas_view.setObjectName("notas_view")
        self.addSubInterface(
            self.notas_view,
            FIF.CHAT,
            "Anotações",
            NavigationItemPosition.TOP
        )
        
        # 4. Configurações (inferior)
        self.settings_view = SettingsView(self)
        self.settings_view.setObjectName("settings_view")
        self.addSubInterface(
            self.settings_view,
            FIF.SETTING,
            "Configurações",
            NavigationItemPosition.BOTTOM
        )
