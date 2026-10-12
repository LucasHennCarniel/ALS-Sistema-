"""
Componentes e estilos corporativos de alto contraste (Tema Cinza Suave ALS & Modo Escuro)
Com Ícones Vetoriais Fluent (Sem emojis informais)
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    isDarkTheme, IconWidget, CaptionLabel, TitleLabel, FluentIcon as FIF
)


class ContrastCard(QFrame):
    """Card com fundo e borda de alto contraste real"""
    def __init__(self, parent=None, cor_acento=None):
        super().__init__(parent)
        self.cor_acento = cor_acento
        self.setObjectName("ContrastCard")
        self.atualizar_estilo()

    def atualizar_estilo(self):
        borda_esq = f"border-left: 4px solid {self.cor_acento};" if self.cor_acento else ""
        if isDarkTheme():
            self.setStyleSheet(f"""
                QFrame#ContrastCard {{
                    background-color: #282C34;
                    border: 1px solid #3E4451;
                    {borda_esq}
                    border-radius: 8px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame#ContrastCard {{
                    background-color: #EAEFF5;
                    border: 1px solid #94A3B8;
                    {borda_esq}
                    border-radius: 8px;
                }}
            """)


class CorporateStatCard(ContrastCard):
    """Card corporativo estilo Power BI com Ícone Vetorial Fluent e barra lateral de acento"""
    def __init__(self, titulo, valor_inicial="0", icone=FIF.DOCUMENT, cor_acento="#4CAF50", parent=None):
        super().__init__(parent, cor_acento=cor_acento)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Topo do Card: Título + Ícone Vetorial
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.label_titulo = CaptionLabel(titulo.upper(), self)
        self.label_titulo.setFont(QFont('Segoe UI', 9, QFont.Bold))

        self.icon_widget = IconWidget(icone, self)
        self.icon_widget.setFixedSize(18, 18)

        top_row.addWidget(self.label_titulo)
        top_row.addStretch()
        top_row.addWidget(self.icon_widget)

        # Valor Principal
        self.label_valor = TitleLabel(str(valor_inicial), self)
        self.label_valor.setFont(QFont('Segoe UI', 20, QFont.Bold))

        layout.addLayout(top_row)
        layout.addWidget(self.label_valor)
        self.setFixedHeight(86)

    def set_valor(self, valor):
        self.label_valor.setText(str(valor))


QSS_TABELA_CINZA = """
QTableWidget, TableWidget {
    background-color: #F1F5F9;
    alternate-background-color: #E2E8F0;
    border: 1px solid #94A3B8;
    border-radius: 8px;
    gridline-color: #CBD5E1;
    color: #0F172A;
    selection-background-color: #90E74A;
    selection-color: #0F172A;
}
QHeaderView::section {
    background-color: #607D8B;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 12px;
    padding: 8px 6px;
    border: none;
    border-right: 1px solid #546E7A;
    border-bottom: 2px solid #455A64;
}
QTableWidget::item, TableWidget::item {
    color: #0F172A;
    padding: 4px;
}
QTableWidget::item:selected, TableWidget::item:selected {
    background-color: #90E74A;
    color: #0F172A;
    font-weight: bold;
}
"""

QSS_TABELA_ESCURA = """
QTableWidget, TableWidget {
    background-color: #21252B;
    alternate-background-color: #282C34;
    border: 1px solid #3E4451;
    border-radius: 8px;
    gridline-color: #333842;
    color: #E6EDF3;
}
QHeaderView::section {
    background-color: #2C3E50;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 12px;
    padding: 8px 6px;
    border: none;
    border-right: 1px solid #3E5368;
    border-bottom: 2px solid #4CAF50;
}
"""
