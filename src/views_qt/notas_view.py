"""
Interface de Notas e Anotações com QFluentWidgets (Fluent Design)
Visual Corporativo com Ícones Vetoriais Fluent e Endpoints Completos
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, 
    QTableWidgetItem, QAbstractItemView
)
from qfluentwidgets import (
    TitleLabel, CaptionLabel,
    PrimaryPushButton, PushButton, SearchLineEdit,
    TableWidget, IconWidget, FluentIcon as FIF, InfoBar, MessageBox
)

from src.views_qt.dialogs import FormNotaDialog
from src.views_qt.theme_styles import aplicar_selecao_visivel


class NotasView(QWidget):
    """View de Notas e Anotações com design Fluent Corporativo"""
    
    COLUNAS = ["ID", "DATA PROGRAMADA", "PLACA / ASSUNTO", "STATUS / PRIORIDADE", "OBSERVAÇÃO / CONTEÚDO"]
    LARGURAS = [60, 150, 180, 160, 420]
    
    def __init__(self, nota_ctrl, parent=None):
        super().__init__(parent)
        self.ctrl = nota_ctrl
        self.notas_atuais = []
        
        self._init_ui()
        self.carregar_dados()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # 1. Cabeçalho com Ícone Vetorial
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        header_icon = IconWidget(FIF.CHAT, self)
        header_icon.setFixedSize(26, 26)
        header_layout.addWidget(header_icon)
        header_layout.addWidget(TitleLabel("Notas e Anotações Internas", self))
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 2. Barra de Ações
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.btn_nova = PrimaryPushButton("Nova Nota", self, FIF.ADD)
        self.btn_nova.clicked.connect(lambda *_: self._nova_nota())
        actions_layout.addWidget(self.btn_nova)
        
        self.btn_editar = PushButton("Editar", self, FIF.EDIT)
        self.btn_editar.clicked.connect(lambda *_: self._editar_selecionada())
        actions_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = PushButton("Excluir", self, FIF.DELETE)
        self.btn_excluir.clicked.connect(lambda *_: self._excluir_selecionada())
        actions_layout.addWidget(self.btn_excluir)
        
        self.btn_atualizar = PushButton("Atualizar", self, FIF.SYNC)
        self.btn_atualizar.clicked.connect(lambda *_: self.carregar_dados())
        actions_layout.addWidget(self.btn_atualizar)
        
        actions_layout.addStretch()
        
        self.search_input = SearchLineEdit(self)
        self.search_input.setPlaceholderText("Pesquisar placa, observação, status...")
        self.search_input.textChanged.connect(self._filtrar)
        self.search_input.setFixedWidth(280)
        actions_layout.addWidget(self.search_input)
        
        layout.addLayout(actions_layout)
        
        # 3. Tabela
        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnCount(len(self.COLUNAS))
        self.table.setHorizontalHeaderLabels(self.COLUNAS)
        self.table.verticalHeader().hide()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        aplicar_selecao_visivel(self.table)
        self.table.itemDoubleClicked.connect(self._on_row_double_click)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        for i, w in enumerate(self.LARGURAS):
            self.table.setColumnWidth(i, w)
        header.setStretchLastSection(True)
        
        layout.addWidget(self.table)

    def atualizar_tema_cards(self, qss_tabela):
        self.table.setStyleSheet(qss_tabela)

    def carregar_dados(self):
        try:
            self.notas_atuais = self.ctrl.obter_todas() or []
            self._render_tabela(self.notas_atuais)
        except Exception as e:
            InfoBar.error("Erro", f"Falha ao carregar notas: {e}", parent=self.window())

    def _render_tabela(self, lista):
        self.table.setRowCount(len(lista))
        for row_idx, n in enumerate(lista):
            nid = n.get('id', '')
            data_prog = n.get('data_programada') or n.get('data_criacao') or ''
            placa = n.get('placa') or n.get('titulo') or ''
            status = n.get('status') or n.get('prioridade') or 'PENDENTE'
            obs = n.get('observacao') or n.get('conteudo') or ''
            
            valores = [nid, data_prog, placa, status, obs]
            for col_idx, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                if col_idx in [0, 1, 2, 3]:
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    
                if col_idx == 3:
                    st_str = str(val).upper()
                    if 'ALTA' in st_str or 'URGENTE' in st_str:
                        item.setForeground(QColor('#C62828'))
                    elif 'PENDENTE' in st_str or 'MÉDIA' in st_str:
                        item.setForeground(QColor('#D84315'))
                    else:
                        item.setForeground(QColor('#2E7D32'))
                        
                self.table.setItem(row_idx, col_idx, item)

    def _filtrar(self, *_):
        termo = self.search_input.text().strip().lower()
        if not termo:
            self._render_tabela(self.notas_atuais)
            return
            
        filtradas = [
            n for n in self.notas_atuais
            if termo in str(n.get('placa', '')).lower()
            or termo in str(n.get('observacao', '')).lower()
            or termo in str(n.get('status', '')).lower()
        ]
        self._render_tabela(filtradas)

    def _obter_id_selecionado(self):
        row = self.table.currentRow()
        if row < 0:
            itens = self.table.selectedItems()
            if itens:
                row = itens[0].row()
        if row >= 0:
            it = self.table.item(row, 0)
            if it:
                try:
                    return int(it.text())
                except Exception:
                    pass
        return None

    def _on_row_double_click(self, item):
        if item:
            self.table.selectRow(item.row())
        self._editar_selecionada()

    def _nova_nota(self):
        dialog = FormNotaDialog(self.window())
        if dialog.exec():
            dados = dialog.obter_dados()
            sucesso, msg = self.ctrl.adicionar_nota(dados)
            if sucesso:
                InfoBar.success("Sucesso", "Nota adicionada com sucesso!", parent=self.window())
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self.window())

    def _editar_selecionada(self):
        nid = self._obter_id_selecionado()
        if not nid:
            InfoBar.warning("Atenção", "Selecione uma nota na tabela para editar.", parent=self.window())
            return
            
        nota = self.ctrl.obter_nota_por_id(nid)
        if not nota:
            InfoBar.error("Erro", "Nota não encontrada.", parent=self.window())
            return
            
        dialog = FormNotaDialog(self.window(), nota)
        if dialog.exec():
            dados = dialog.obter_dados()
            sucesso, msg = self.ctrl.atualizar_nota(nid, dados)
            if sucesso:
                InfoBar.success("Sucesso", "Nota atualizada com sucesso!", parent=self.window())
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self.window())

    def _excluir_selecionada(self):
        linhas = set(item.row() for item in self.table.selectedItems())
        if not linhas and self.table.currentRow() >= 0:
            linhas.add(self.table.currentRow())

        if not linhas:
            InfoBar.warning("Atenção", "Selecione uma nota na tabela para excluir.", parent=self.window())
            return
            
        msg_box = MessageBox(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir {len(linhas)} anotação(ões) selecionada(s)?",
            self.window()
        )
        msg_box.yesButton.setText("Excluir")
        msg_box.cancelButton.setText("Cancelar")
        if msg_box.exec():
            excluidas = 0
            for r in linhas:
                it = self.table.item(r, 0)
                if it:
                    try:
                        ok, _ = self.ctrl.excluir_nota(int(it.text()))
                        if ok:
                            excluidas += 1
                    except Exception:
                        pass
            InfoBar.success("Sucesso", f"{excluidas} nota(s) excluída(s) com sucesso!", parent=self.window())
            self.carregar_dados()
