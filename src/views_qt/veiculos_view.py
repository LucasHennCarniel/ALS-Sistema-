"""
Interface de Gestão de Veículos com QFluentWidgets (Fluent Design)
Visual Corporativo com Ícones Vetoriais Fluent e Endpoints Completos
"""
import os
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, 
    QTableWidgetItem, QFileDialog, QAbstractItemView
)
from qfluentwidgets import (
    TitleLabel, CaptionLabel, BodyLabel,
    PrimaryPushButton, PushButton, SearchLineEdit,
    TableWidget, IconWidget, FluentIcon as FIF, InfoBar, MessageBox
)

from src.views_qt.dialogs import FormVeiculoDialog, ImportarOpcoesDialog
from src.views_qt.manutencao_view import ler_planilha_inteligente
from src.views_qt.theme_styles import CorporateStatCard


class VeiculosView(QWidget):
    """View de Veículos com design Fluent Corporativo"""
    
    COLUNAS = ["TIPO / MARCA", "PLACA", "DESCRIÇÃO", "ÚLTIMA KM", "DATA CADASTRO", "STATUS"]
    LARGURAS = [150, 110, 260, 120, 140, 100]
    
    def __init__(self, veiculo_ctrl, parent=None):
        super().__init__(parent)
        self.ctrl = veiculo_ctrl
        self.veiculos_atuais = []
        
        self._init_ui()
        self.carregar_dados()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # 1. Cabeçalho com Ícone Vetorial
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        header_icon = IconWidget(FIF.CAR, self)
        header_icon.setFixedSize(26, 26)
        header_layout.addWidget(header_icon)
        header_layout.addWidget(TitleLabel("Gestão de Veículos da Frota", self))
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 2. Estatísticas com Ícones Vetoriais e Borda de Acento
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        self.card_total = CorporateStatCard("Total de Veículos", "0", FIF.CAR, "#607D8B", self)
        self.card_ativos = CorporateStatCard("Veículos Ativos", "0", FIF.ACCEPT, "#4CAF50", self)
        self.card_inativos = CorporateStatCard("Veículos Inativos", "0", FIF.CLOSE, "#EF5350", self)
        
        self.cards = [self.card_total, self.card_ativos, self.card_inativos]
        for c in self.cards:
            c.setMinimumWidth(220)
            stats_layout.addWidget(c)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # 3. Barra de Ações
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.btn_novo = PrimaryPushButton("Novo Veículo", self, FIF.ADD)
        self.btn_novo.clicked.connect(lambda *_: self._novo_veiculo())
        actions_layout.addWidget(self.btn_novo)
        
        self.btn_editar = PushButton("Editar", self, FIF.EDIT)
        self.btn_editar.clicked.connect(lambda *_: self._editar_selecionado())
        actions_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = PushButton("Excluir", self, FIF.DELETE)
        self.btn_excluir.clicked.connect(lambda *_: self._excluir_selecionado())
        actions_layout.addWidget(self.btn_excluir)
        
        self.btn_atualizar = PushButton("Atualizar", self, FIF.SYNC)
        self.btn_atualizar.clicked.connect(lambda *_: self.carregar_dados())
        actions_layout.addWidget(self.btn_atualizar)
        
        self.btn_importar = PushButton("Importar Planilha", self, FIF.DOWNLOAD)
        self.btn_importar.clicked.connect(lambda *_: self._importar_planilha())
        actions_layout.addWidget(self.btn_importar)
        
        self.btn_exportar = PushButton("Exportar Planilha", self, FIF.SHARE)
        self.btn_exportar.clicked.connect(lambda *_: self._exportar_planilha())
        actions_layout.addWidget(self.btn_exportar)
        
        actions_layout.addStretch()
        
        self.search_input = SearchLineEdit(self)
        self.search_input.setPlaceholderText("Pesquisar placa, tipo, descrição...")
        self.search_input.textChanged.connect(self._filtrar)
        self.search_input.setFixedWidth(280)
        actions_layout.addWidget(self.search_input)
        
        layout.addLayout(actions_layout)
        
        # 4. Tabela
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
        self.table.itemDoubleClicked.connect(self._on_row_double_click)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        for i, w in enumerate(self.LARGURAS):
            self.table.setColumnWidth(i, w)
        header.setStretchLastSection(True)
        
        layout.addWidget(self.table)

    def atualizar_tema_cards(self, qss_tabela):
        for c in self.cards:
            c.atualizar_estilo()
        self.table.setStyleSheet(qss_tabela)

    def carregar_dados(self):
        try:
            self.veiculos_atuais = self.ctrl.obter_todos() or []
            self._render_tabela(self.veiculos_atuais)
            self._atualizar_stats()
        except Exception as e:
            InfoBar.error("Erro", f"Falha ao carregar veículos: {e}", parent=self.window())

    def _render_tabela(self, lista):
        self.table.setRowCount(len(lista))
        for row_idx, v in enumerate(lista):
            tipo = v.get('tipo_veiculo', '') or v.get('tipo', '') or ''
            placa = v.get('placa', '') or ''
            desc = v.get('descricao')
            desc_txt = '' if desc is None or str(desc) == 'None' else str(desc)
            km = v.get('ultima_km', 0)
            data_cad = v.get('data_cadastro', '') or ''
            ativo = v.get('ativo', 1)
            
            status_txt = "ATIVO" if ativo else "INATIVO"
            try:
                km_txt = f"{int(float(km)):,}".replace(',', '.') if km else "0"
            except Exception:
                km_txt = "0"
            
            valores = [tipo, placa, desc_txt, km_txt, data_cad, status_txt]
            for col_idx, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                if col_idx in [1, 3, 4, 5]:
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    
                if col_idx == 5:
                    item.setForeground(QColor('#2E7D32') if ativo else QColor('#C62828'))
                    
                self.table.setItem(row_idx, col_idx, item)

    def _atualizar_stats(self):
        total = len(self.veiculos_atuais)
        ativos = sum(1 for v in self.veiculos_atuais if v.get('ativo', 1))
        inativos = total - ativos
        self.card_total.set_valor(total)
        self.card_ativos.set_valor(ativos)
        self.card_inativos.set_valor(inativos)

    def _filtrar(self, *_):
        termo = self.search_input.text().strip().lower()
        if not termo:
            self._render_tabela(self.veiculos_atuais)
            return
            
        filtrados = [
            v for v in self.veiculos_atuais
            if termo in str(v.get('placa', '')).lower()
            or termo in str(v.get('tipo_veiculo', '')).lower()
            or termo in str(v.get('descricao', '')).lower()
        ]
        self._render_tabela(filtrados)

    def _novo_veiculo(self):
        dialog = FormVeiculoDialog(self.window())
        if dialog.exec():
            dados = dialog.obter_dados()
            sucesso, msg = self.ctrl.adicionar_veiculo(
                tipo=dados['tipo'],
                placa=dados['placa'],
                descricao=dados['descricao'],
                km_inicial=dados['km_inicial']
            )
            if sucesso:
                InfoBar.success("Sucesso", "Veículo cadastrado com sucesso!", parent=self.window())
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self.window())

    def _obter_placa_selecionada(self):
        row = self.table.currentRow()
        if row < 0:
            itens = self.table.selectedItems()
            if itens:
                row = itens[0].row()
        if row >= 0:
            item_placa = self.table.item(row, 1)
            if item_placa:
                return item_placa.text().strip()
        return None

    def _on_row_double_click(self, item):
        if item:
            self.table.selectRow(item.row())
        self._editar_selecionado()

    def _editar_selecionado(self):
        placa = self._obter_placa_selecionada()
        if not placa:
            InfoBar.warning("Atenção", "Selecione um veículo na tabela para editar.", parent=self.window())
            return
            
        veiculo = self.ctrl.obter_veiculo_por_placa(placa)
        if not veiculo:
            InfoBar.error("Erro", f"Veículo de placa {placa} não encontrado.", parent=self.window())
            return
            
        dialog = FormVeiculoDialog(self.window(), veiculo)
        if dialog.exec():
            dados = dialog.obter_dados()
            sucesso, msg = self.ctrl.atualizar_veiculo(
                placa_antiga=placa,
                tipo=dados['tipo'],
                nova_placa=dados['placa'],
                descricao=dados['descricao'],
                ativo=dados['ativo'],
                ultima_km=dados['km_inicial']
            )
            if sucesso:
                InfoBar.success("Sucesso", "Veículo atualizado com sucesso!", parent=self.window())
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self.window())

    def _excluir_selecionado(self):
        linhas = set(item.row() for item in self.table.selectedItems())
        if not linhas and self.table.currentRow() >= 0:
            linhas.add(self.table.currentRow())

        if not linhas:
            InfoBar.warning("Atenção", "Selecione um ou mais veículos na tabela para excluir.", parent=self.window())
            return

        placas = []
        for r in linhas:
            it = self.table.item(r, 1)
            if it and it.text().strip():
                placas.append(it.text().strip())

        if not placas:
            return

        texto_conf = (
            f"Tem certeza que deseja excluir permanentemente o veículo de placa {placas[0]}?"
            if len(placas) == 1
            else f"Tem certeza que deseja excluir permanentemente {len(placas)} veículos selecionados?"
        )
        msg_box = MessageBox("Confirmar Exclusão", texto_conf, self.window())
        msg_box.yesButton.setText("Excluir")
        msg_box.cancelButton.setText("Cancelar")
        if msg_box.exec():
            excluidos = 0
            for p in placas:
                ok, _ = self.ctrl.excluir_veiculo(p)
                if ok:
                    excluidos += 1
            InfoBar.success("Sucesso", f"{excluidos} veículo(s) excluído(s) com sucesso!", parent=self.window())
            self.carregar_dados()

    def processar_dataframe_veiculos(self, df, modo="atualizar"):
        """Processa um DataFrame de veículos suportando os modos 'novo', 'atualizar' e 'substituir'"""
        if modo == "substituir":
            conn = self.ctrl.model.conn
            conn.execute("DELETE FROM veiculos")
            conn.commit()

        col_tipo = (
            'MARCA' if 'MARCA' in df.columns
            else 'TIPO / MARCA' if 'TIPO / MARCA' in df.columns
            else 'TIPO_VEICULO' if 'TIPO_VEICULO' in df.columns
            else 'TIPO' if 'TIPO' in df.columns
            else 'FROTA' if 'FROTA' in df.columns
            else None
        )
        col_km = (
            'KM ATUAL' if 'KM ATUAL' in df.columns
            else 'ÚLTIMA KM' if 'ÚLTIMA KM' in df.columns
            else 'ULTIMA_KM' if 'ULTIMA_KM' in df.columns
            else 'KM' if 'KM' in df.columns
            else None
        )
        col_modelo = 'MODELO' if 'MODELO' in df.columns else 'DESCRIÇÃO' if 'DESCRIÇÃO' in df.columns else 'DESCRICAO' if 'DESCRICAO' in df.columns else None
        col_cor = 'COR' if 'COR' in df.columns else None

        novos = 0
        atualizados = 0

        for _, row in df.iterrows():
            placa = str(row.get('PLACA', '')).strip().upper()
            if not placa or placa == 'NAN' or placa == 'NONE':
                continue

            tipo = str(row.get(col_tipo, '')).strip().upper() if col_tipo and pd.notna(row.get(col_tipo)) else 'FROTA'
            if not tipo or tipo == 'NAN':
                tipo = 'FROTA'

            desc_parts = []
            if col_modelo and pd.notna(row.get(col_modelo)):
                m_str = str(row.get(col_modelo)).strip()
                if m_str and m_str.upper() != 'NAN':
                    desc_parts.append(m_str)
            if col_cor and pd.notna(row.get(col_cor)):
                c_str = str(row.get(col_cor)).strip()
                if c_str and c_str.upper() != 'NAN':
                    desc_parts.append(c_str)
            descricao = ' - '.join(desc_parts)

            try:
                km = float(row.get(col_km, 0)) if col_km and pd.notna(row.get(col_km)) else 0.0
            except Exception:
                km = 0.0

            existente = self.ctrl.obter_veiculo_por_placa(placa)
            if existente:
                if modo == "novo":
                    continue
                elif modo == "atualizar":
                    novo_tipo = tipo if tipo != 'FROTA' else existente.get('tipo_veiculo', 'FROTA')
                    nova_desc = descricao if descricao else (existente.get('descricao') or '')
                    nova_km = km if km > 0 else (existente.get('ultima_km') or 0)
                    self.ctrl.atualizar_veiculo(
                        placa_antiga=placa,
                        tipo=novo_tipo,
                        nova_placa=placa,
                        descricao=nova_desc,
                        ativo=existente.get('ativo', 1),
                        ultima_km=nova_km
                    )
                    atualizados += 1
            else:
                self.ctrl.adicionar_veiculo(tipo, placa, descricao, km)
                novos += 1

        return novos, atualizados

    def _importar_planilha(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self.window(), "Importar Planilha de Veículos", "", "Planilhas (*.xlsx *.xls *.csv)"
        )
        if not caminho:
            return
            
        try:
            df = ler_planilha_inteligente(caminho)
            if 'PLACA' not in df.columns:
                InfoBar.error(
                    "Arquivo Inválido",
                    f"A planilha não possui a coluna 'PLACA'.\nColunas encontradas: {', '.join(df.columns[:6])}",
                    parent=self.window()
                )
                return

            dlg_opcoes = ImportarOpcoesDialog(self.window(), os.path.basename(caminho))
            if not dlg_opcoes.exec():
                return
            modo = dlg_opcoes.obter_modo()

            novos, atualizados = self.processar_dataframe_veiculos(df, modo)
            self.carregar_dados()
            InfoBar.success(
                "Importação Concluída",
                f"{novos} novo(s) veículo(s) cadastrado(s) e {atualizados} atualizado(s)!",
                parent=self.window()
            )
        except Exception as e:
            InfoBar.error("Erro", f"Falha ao importar planilha: {e}", parent=self.window())

    def _exportar_planilha(self):
        if not self.veiculos_atuais:
            InfoBar.warning("Atenção", "Não há veículos cadastrados para exportar.", parent=self.window())
            return
            
        caminho, _ = QFileDialog.getSaveFileName(
            self.window(), "Exportar Veículos", "veiculos_frota_als.xlsx", "Excel Files (*.xlsx)"
        )
        if caminho:
            try:
                from src.services.export_service import ExportService
                df = pd.DataFrame(self.veiculos_atuais).rename(columns={
                    'placa': 'PLACA',
                    'tipo_veiculo': 'TIPO / MARCA',
                    'descricao': 'DESCRIÇÃO',
                    'ultima_km': 'KM ATUAL',
                    'data_cadastro': 'DATA CADASTRO',
                    'ativo': 'ATIVO'
                })
                ExportService.exportar_excel(df, caminho)
                InfoBar.success("Sucesso", "Frota exportada para Excel com sucesso!", parent=self.window())
                try:
                    os.startfile(caminho)
                except Exception:
                    pass
            except Exception as e:
                InfoBar.error("Erro", f"Falha ao exportar: {e}", parent=self.window())
