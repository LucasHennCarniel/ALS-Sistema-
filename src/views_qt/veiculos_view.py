"""
Interface de Gestão de Veículos com QFluentWidgets (Fluent Design)
"""
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, 
    QTableWidgetItem, QFileDialog, QAbstractItemView
)
from qfluentwidgets import (
    TitleLabel, CaptionLabel, BodyLabel,
    PrimaryPushButton, PushButton, SearchLineEdit,
    TableWidget, SimpleCardWidget,
    FluentIcon as FIF, InfoBar, MessageBox
)

from src.views_qt.dialogs import FormVeiculoDialog


class VeiculoStatCard(SimpleCardWidget):
    """Card de estatística para veículos"""
    def __init__(self, titulo, valor_inicial="0", icone="🚛", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(4)
        
        self.label_titulo = CaptionLabel(f"{icone} {titulo}", self)
        self.label_valor = TitleLabel(str(valor_inicial), self)
        self.label_valor.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_valor)
        self.setFixedHeight(75)

    def set_valor(self, valor):
        self.label_valor.setText(str(valor))


class VeiculosView(QWidget):
    """View de Veículos com design Fluent"""
    
    COLUNAS = ["TIPO / MARCA", "PLACA", "DESCRIÇÃO", "ÚLTIMA KM", "DATA CADASTRO", "STATUS"]
    
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
        
        # 1. Cabeçalho
        header_layout = QHBoxLayout()
        header_layout.addWidget(TitleLabel("Gestão de Veículos da Frota", self))
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 2. Estatísticas
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        self.card_total = VeiculoStatCard("Total de Veículos", "0", "🚛", self)
        self.card_ativos = VeiculoStatCard("Veículos Ativos", "0", "✅", self)
        self.card_inativos = VeiculoStatCard("Veículos Inativos", "0", "⛔", self)
        
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_ativos)
        stats_layout.addWidget(self.card_inativos)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # 3. Barra de Ações
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.btn_novo = PrimaryPushButton("Novo Veículo", self, FIF.ADD)
        self.btn_novo.clicked.connect(self._novo_veiculo)
        actions_layout.addWidget(self.btn_novo)
        
        self.btn_editar = PushButton("Editar", self, FIF.EDIT)
        self.btn_editar.clicked.connect(self._editar_selecionado)
        actions_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = PushButton("Excluir", self, FIF.DELETE)
        self.btn_excluir.clicked.connect(self._excluir_selecionado)
        actions_layout.addWidget(self.btn_excluir)
        
        self.btn_atualizar = PushButton("Atualizar", self, FIF.SYNC)
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        actions_layout.addWidget(self.btn_atualizar)
        
        self.btn_importar = PushButton("Importar Planilha", self, FIF.DOWNLOAD)
        self.btn_importar.clicked.connect(self._importar_planilha)
        actions_layout.addWidget(self.btn_importar)
        
        self.btn_exportar = PushButton("Exportar Planilha", self, FIF.SHARE)
        self.btn_exportar.clicked.connect(self._exportar_planilha)
        actions_layout.addWidget(self.btn_exportar)
        
        actions_layout.addStretch()
        
        # Pesquisa rápida
        self.search_input = SearchLineEdit(self)
        self.search_input.setPlaceholderText("Pesquisar placa, tipo, descrição...")
        self.search_input.textChanged.connect(self._filtrar)
        self.search_input.setFixedWidth(280)
        actions_layout.addWidget(self.search_input)
        
        layout.addLayout(actions_layout)
        
        # 4. Tabela
        self.table = TableWidget(self)
        self.table.setColumnCount(len(self.COLUNAS))
        self.table.setHorizontalHeaderLabels(self.COLUNAS)
        self.table.verticalHeader().hide()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self._editar_selecionado)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
        layout.addWidget(self.table)

    def carregar_dados(self):
        """Carrega dados dos veículos"""
        try:
            self.veiculos_atuais = self.ctrl.obter_todos() or []
            self._render_tabela(self.veiculos_atuais)
            self._atualizar_stats()
        except Exception as e:
            InfoBar.error("Erro", f"Falha ao carregar veículos: {e}", parent=self)

    def _render_tabela(self, lista):
        self.table.setRowCount(len(lista))
        for row_idx, v in enumerate(lista):
            tipo = v.get('tipo_veiculo', '') or v.get('tipo', '')
            placa = v.get('placa', '')
            desc = v.get('descricao', '')
            km = v.get('ultima_km', 0)
            data_cad = v.get('data_cadastro', '')
            ativo = v.get('ativo', 1)
            
            status_txt = "ATIVO" if ativo else "INATIVO"
            km_txt = f"{int(float(km)):,}".replace(',', '.') if km else "0"
            
            valores = [tipo, placa, desc, km_txt, data_cad, status_txt]
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

    def _filtrar(self):
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
        dialog = FormVeiculoDialog(self)
        if dialog.exec():
            dados = dialog.obter_dados()
            sucesso, msg = self.ctrl.adicionar_veiculo(
                tipo=dados['tipo'],
                placa=dados['placa'],
                descricao=dados['descricao'],
                km_inicial=dados['km_inicial']
            )
            if sucesso:
                InfoBar.success("Sucesso", "Veículo cadastrado com sucesso!", parent=self)
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self)

    def _obter_placa_selecionada(self):
        itens = self.table.selectedItems()
        if not itens:
            return None
        row = itens[0].row()
        return self.table.item(row, 1).text()

    def _editar_selecionado(self):
        placa = self._obter_placa_selecionada()
        if not placa:
            InfoBar.warning("Atenção", "Selecione um veículo para editar.", parent=self)
            return
            
        veiculo = self.ctrl.obter_veiculo_por_placa(placa)
        if not veiculo:
            InfoBar.error("Erro", "Veículo não encontrado.", parent=self)
            return
            
        dialog = FormVeiculoDialog(self, veiculo)
        if dialog.exec():
            dados = dialog.obter_dados()
            sucesso, msg = self.ctrl.atualizar_veiculo(
                placa_antiga=placa,
                tipo=dados['tipo'],
                nova_placa=dados['placa'],
                descricao=dados['descricao'],
                ativo=dados['ativo']
            )
            if sucesso:
                InfoBar.success("Sucesso", "Veículo atualizado com sucesso!", parent=self)
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self)

    def _excluir_selecionado(self):
        placa = self._obter_placa_selecionada()
        if not placa:
            InfoBar.warning("Atenção", "Selecione um veículo para excluir.", parent=self)
            return
            
        msg_box = MessageBox(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o veículo de placa {placa}?",
            self
        )
        if msg_box.exec():
            sucesso, msg = self.ctrl.excluir_veiculo(placa)
            if sucesso:
                InfoBar.success("Sucesso", "Veículo excluído com sucesso!", parent=self)
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self)

    def _importar_planilha(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Importar Veículos", "", "Planilhas (*.xlsx *.xls *.csv)"
        )
        if not caminho:
            return
            
        try:
            if caminho.endswith('.csv'):
                df = pd.read_csv(caminho)
            else:
                df = pd.read_excel(caminho)
                
            df.columns = df.columns.str.strip().str.upper()
            
            if 'PLACA' not in df.columns:
                InfoBar.error("Erro", "A planilha não possui a coluna 'PLACA'.", parent=self)
                return
                
            col_tipo = 'MARCA' if 'MARCA' in df.columns else 'TIPO' if 'TIPO' in df.columns else 'FROTA' if 'FROTA' in df.columns else None
            col_km = 'KM ATUAL' if 'KM ATUAL' in df.columns else 'KM' if 'KM' in df.columns else None
            col_modelo = 'MODELO' if 'MODELO' in df.columns else None
            col_cor = 'COR' if 'COR' in df.columns else None
            
            novos = 0
            atuais = {v['placa'].upper() for v in self.ctrl.obter_todos()}
            
            for _, row in df.iterrows():
                placa = str(row.get('PLACA', '')).strip().upper()
                if not placa or placa == 'NAN' or placa in atuais:
                    continue
                    
                tipo = str(row.get(col_tipo, '')) if col_tipo else 'Indefinido'
                desc_parts = []
                if col_modelo and pd.notna(row.get(col_modelo)):
                    desc_parts.append(str(row.get(col_modelo)))
                if col_cor and pd.notna(row.get(col_cor)):
                    desc_parts.append(str(row.get(col_cor)))
                descricao = ' - '.join(desc_parts)
                
                try:
                    km = float(row.get(col_km, 0)) if col_km and pd.notna(row.get(col_km)) else 0
                except Exception:
                    km = 0
                    
                self.ctrl.adicionar_veiculo(tipo, placa, descricao, km)
                atuais.add(placa)
                novos += 1
                
            InfoBar.success("Sucesso", f"Importação concluída! {novos} novo(s) veículo(s) cadastrados.", parent=self)
            self.carregar_dados()
        except Exception as e:
            InfoBar.error("Erro", f"Falha ao importar: {e}", parent=self)

    def _exportar_planilha(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Exportar Veículos", "veiculos_frota.xlsx", "Excel Files (*.xlsx)"
        )
        if caminho:
            try:
                df = pd.DataFrame(self.veiculos_atuais)
                df.to_excel(caminho, index=False)
                InfoBar.success("Sucesso", f"Exportado com sucesso para:\n{caminho}", parent=self)
            except Exception as e:
                InfoBar.error("Erro", f"Falha ao exportar: {e}", parent=self)
