"""
Componentes e estilos de alto contraste (Tema Cinza Suave ALS & Modo Escuro)
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame
from qfluentwidgets import isDarkTheme


class ContrastCard(QFrame):
    """Card com fundo e borda de alto contraste real (não fica branco invisível)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContrastCard")
        self.atualizar_estilo()

    def atualizar_estilo(self):
        if isDarkTheme():
            self.setStyleSheet("""
                QFrame#ContrastCard {
                    background-color: #282C34;
                    border: 1px solid #3E4451;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#ContrastCard {
                    background-color: #EAEFF5;
                    border: 1px solid #94A3B8;
                    border-radius: 8px;
                }
            """)


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
