"""
Interface Principal de Registros de Manutenção com QFluentWidgets
"""
from datetime import datetime
import pandas as pd
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, 
    QTableWidgetItem, QFileDialog, QAbstractItemView
)
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, CaptionLabel, BodyLabel,
    PrimaryPushButton, PushButton, SearchLineEdit, ComboBox,
    TableWidget, FluentIcon as FIF, InfoBar, MessageBox
)

from src.views_qt.dialogs import FormRegistroDialog
from src.views_qt.theme_styles import ContrastCard


class StatCard(ContrastCard):
    """Card de estatística moderno com fundo cinza-gelo e borda nítida"""
    def __init__(self, titulo, valor_inicial="0", icone="📊", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(4)
        
        self.label_titulo = CaptionLabel(f"{icone}  {titulo}", self)
        self.label_titulo.setFont(QFont('Segoe UI', 10, QFont.DemiBold))
        
        self.label_valor = TitleLabel(str(valor_inicial), self)
        self.label_valor.setFont(QFont('Segoe UI', 20, QFont.Bold))
        
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_valor)
        self.setFixedHeight(86)

    def set_valor(self, valor):
        self.label_valor.setText(str(valor))


class ManutencaoView(QWidget):
    """View de Manutenções estilo Fluent Design"""
    
    COLUNAS = [
        "ID", "DATA", "PLACA", "KM", "VEÍCULO", 
        "DESTINO PROGRAMADO", "SERVIÇO A EXECUTAR", "STATUS", 
        "DATA ENTRADA", "DATA SAÍDA", "DIAS", "NRº OF", "OBS"
    ]
    
    LARGURAS_COLUNAS = [
        55, 95, 90, 85, 110,
        165, 220, 130,
        115, 105, 65, 90, 180
    ]
    
    def __init__(self, manutencao_ctrl, veiculo_ctrl, destino_ctrl, parent=None):
        super().__init__(parent)
        self.ctrl = manutencao_ctrl
        self.veiculo_ctrl = veiculo_ctrl
        self.destino_ctrl = destino_ctrl
        self.df_atual = None
        
        self._init_ui()
        self.carregar_dados()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # 1. Cabeçalho com Título
        header_layout = QHBoxLayout()
        title = TitleLabel("Registros de Manutenção", self)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 2. Cards de Estatísticas
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        
        self.card_total = StatCard("Total de Registros", "0", "📊", self)
        self.card_servico = StatCard("Em Serviço", "0", "⚙️", self)
        self.card_finalizados = StatCard("Finalizados", "0", "✅", self)
        self.card_tempo = StatCard("Tempo Médio", "0 d", "⏱️", self)
        self.card_placas = StatCard("Placas Atendidas", "0", "🚛", self)
        
        self.cards = [
            self.card_total, self.card_servico, self.card_finalizados,
            self.card_tempo, self.card_placas
        ]
        for c in self.cards:
            stats_layout.addWidget(c)
        layout.addLayout(stats_layout)
        
        # 3. Barra de Ações (Botões)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.btn_novo = PrimaryPushButton("Novo Registro", self, FIF.ADD)
        self.btn_novo.clicked.connect(self._novo_registro)
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
        
        self.btn_relatorio = PushButton("Relatório", self, FIF.DOCUMENT)
        self.btn_relatorio.clicked.connect(self._abrir_relatorio)
        actions_layout.addWidget(self.btn_relatorio)
        
        self.btn_exportar = PushButton("Exportar", self, FIF.SHARE)
        self.btn_exportar.clicked.connect(self._exportar_dados)
        actions_layout.addWidget(self.btn_exportar)
        
        self.btn_importar = PushButton("Importar", self, FIF.DOWNLOAD)
        self.btn_importar.clicked.connect(self._importar_dados)
        actions_layout.addWidget(self.btn_importar)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # 4. Barra de Filtros
        self.filters_card = ContrastCard(self)
        filters_layout = QHBoxLayout(self.filters_card)
        filters_layout.setContentsMargins(14, 10, 14, 10)
        filters_layout.setSpacing(12)
        
        self.search_input = SearchLineEdit(self)
        self.search_input.setPlaceholderText("Pesquisar por Placa, Veículo, Serviço...")
        self.search_input.textChanged.connect(self._aplicar_filtro_busca)
        self.search_input.setFixedWidth(300)
        filters_layout.addWidget(self.search_input)
        
        filters_layout.addWidget(BodyLabel("Status:", self))
        self.combo_filtro_status = ComboBox(self)
        self.combo_filtro_status.addItem("Todos")
        self.combo_filtro_status.addItems(["EM MANUTENÇÃO", "FINALIZADO", "AGUARDANDO PEÇAS"])
        self.combo_filtro_status.currentTextChanged.connect(self._aplicar_filtro_busca)
        self.combo_filtro_status.setFixedWidth(180)
        filters_layout.addWidget(self.combo_filtro_status)
        
        self.btn_limpar_filtro = PushButton("Limpar", self)
        self.btn_limpar_filtro.clicked.connect(self._limpar_filtros)
        filters_layout.addWidget(self.btn_limpar_filtro)
        
        filters_layout.addStretch()
        layout.addWidget(self.filters_card)
        
        # 5. Tabela de Registros
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
        
        # Configura larguras das colunas para não cortar cabeçalhos
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        for i, width in enumerate(self.LARGURAS_COLUNAS):
            self.table.setColumnWidth(i, width)
        header.setStretchLastSection(True)
        
        layout.addWidget(self.table)

    def atualizar_tema_cards(self, qss_tabela):
        for c in self.cards:
            c.atualizar_estilo()
        self.filters_card.atualizar_estilo()
        self.table.setStyleSheet(qss_tabela)

    def carregar_dados(self):
        """Carrega e popula a tabela com dados do banco"""
        try:
            self.df_atual = self.ctrl.obter_dataframe_exibicao()
            self._render_tabela(self.df_atual)
            self._atualizar_estatisticas()
        except Exception as e:
            InfoBar.error("Erro", f"Falha ao carregar registros: {e}", parent=self)

    def _render_tabela(self, df):
        if df is None:
            self.table.setRowCount(0)
            return
            
        self.table.setRowCount(len(df))
        for row_idx, (_, row) in enumerate(df.iterrows()):
            for col_idx, col_name in enumerate(self.COLUNAS):
                val = row.get(col_name, '')
                if pd.isna(val):
                    val = ''
                elif col_name == 'KM' and val != '':
                    try:
                        val = f"{int(float(val)):,}".replace(',', '.')
                    except Exception:
                        pass
                elif col_name == 'DIAS' and val != '':
                    try:
                        val = f"{int(float(val))} d"
                    except Exception:
                        pass
                        
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter if col_name in ['ID', 'DATA', 'PLACA', 'STATUS', 'DIAS', 'DATA ENTRADA', 'DATA SAÍDA'] else Qt.AlignLeft | Qt.AlignVCenter)
                
                # Cores de Status com alto contraste
                if col_name == 'STATUS':
                    status_str = str(val).upper()
                    if 'FINALIZADO' in status_str:
                        item.setForeground(QColor('#2E7D32'))
                    elif 'MANUTENÇÃO' in status_str or 'SERVIÇO' in status_str:
                        item.setForeground(QColor('#D84315'))
                    elif 'AGUARDANDO' in status_str:
                        item.setForeground(QColor('#C62828'))
                        
                self.table.setItem(row_idx, col_idx, item)

    def _atualizar_estatisticas(self):
        stats = self.ctrl.obter_estatisticas()
        self.card_total.set_valor(stats.get('total', 0))
        self.card_servico.set_valor(stats.get('em_servico', 0))
        self.card_finalizados.set_valor(stats.get('finalizados', 0))
        self.card_tempo.set_valor(f"{stats.get('tempo_medio', 0.0)} d")
        self.card_placas.set_valor(stats.get('placas_unicas', 0))

    def _aplicar_filtro_busca(self):
        if self.df_atual is None:
            return
            
        termo = self.search_input.text().strip().lower()
        status_filtro = self.combo_filtro_status.currentText()
        
        df_filtrado = self.df_atual.copy()
        
        if status_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['STATUS'].str.upper() == status_filtro.upper()]
            
        if termo:
            mascara = (
                df_filtrado['PLACA'].str.lower().str.contains(termo, na=False) |
                df_filtrado['VEÍCULO'].str.lower().str.contains(termo, na=False) |
                df_filtrado['SERVIÇO A EXECUTAR'].str.lower().str.contains(termo, na=False) |
                df_filtrado['DESTINO PROGRAMADO'].str.lower().str.contains(termo, na=False)
            )
            df_filtrado = df_filtrado[mascara]
            
        self._render_tabela(df_filtrado)

    def _limpar_filtros(self):
        self.search_input.clear()
        self.combo_filtro_status.setCurrentIndex(0)
        self._render_tabela(self.df_atual)

    def _novo_registro(self):
        dialog = FormRegistroDialog(self, None, self.veiculo_ctrl, self.destino_ctrl)
        if dialog.exec():
            dados = dialog.obter_dados()
            sucesso, msg = self.ctrl.adicionar_registro(dados)
            if sucesso:
                InfoBar.success("Sucesso", "Registro criado com sucesso!", parent=self)
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self)

    def _obter_id_linha_selecionada(self):
        itens = self.table.selectedItems()
        if not itens:
            return None
        row = itens[0].row()
        id_item = self.table.item(row, 0)
        if id_item:
            try:
                return int(id_item.text())
            except Exception:
                pass
        return None

    def _on_row_double_click(self, item):
        self._editar_selecionado()

    def _editar_selecionado(self):
        id_reg = self._obter_id_linha_selecionada()
        if not id_reg:
            InfoBar.warning("Atenção", "Selecione um registro para editar.", parent=self)
            return
            
        registro = self.ctrl.obter_registro_por_id(id_reg)
        if not registro:
            InfoBar.error("Erro", "Registro não encontrado.", parent=self)
            return
            
        dialog = FormRegistroDialog(self, registro, self.veiculo_ctrl, self.destino_ctrl)
        if dialog.exec():
            dados = dialog.obter_dados()
            sucesso, msg = self.ctrl.atualizar_registro(id_reg, dados)
            if sucesso:
                InfoBar.success("Sucesso", "Registro atualizado com sucesso!", parent=self)
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self)

    def _excluir_selecionado(self):
        linhas_selecionadas = list(set(item.row() for item in self.table.selectedItems()))
        if not linhas_selecionadas:
            InfoBar.warning("Atenção", "Selecione um ou mais registros para excluir.", parent=self)
            return
            
        qtd = len(linhas_selecionadas)
        msg_box = MessageBox(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir {qtd} registro(s) selecionado(s)?",
            self
        )
        if msg_box.exec():
            ids = []
            for r in linhas_selecionadas:
                try:
                    ids.append(int(self.table.item(r, 0).text()))
                except Exception:
                    pass
                    
            if len(ids) == 1:
                self.ctrl.excluir_registro(ids[0])
            else:
                self.ctrl.excluir_multiplos(ids)
                
            InfoBar.success("Sucesso", f"{len(ids)} registro(s) excluído(s)!", parent=self)
            self.carregar_dados()

    def _exportar_dados(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Exportar para Excel", "manutencoes_als.xlsx", "Excel Files (*.xlsx)"
        )
        if caminho:
            try:
                from src.services.export_service import ExportService
                service = ExportService()
                service.exportar_excel(self.df_atual, caminho)
                InfoBar.success("Sucesso", f"Exportado com sucesso para:\n{caminho}", parent=self)
            except Exception as e:
                InfoBar.error("Erro", f"Falha na exportação: {e}", parent=self)

    def _importar_dados(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Importar Planilha", "", "Planilhas (*.xlsx *.xls *.csv)"
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
                InfoBar.error("Arquivo Inválido", "A planilha não possui a coluna 'PLACA'.", parent=self)
                return
                
            novos = 0
            for _, row in df.iterrows():
                placa = str(row.get('PLACA', '')).strip().upper()
                if not placa or placa == 'NAN':
                    continue
                dados = {
                    'data': str(row.get('DATA', '')) if pd.notna(row.get('DATA')) else '',
                    'placa': placa,
                    'km': float(row.get('KM', 0)) if pd.notna(row.get('KM')) else 0,
                    'veiculo': str(row.get('VEÍCULO', '')) if pd.notna(row.get('VEÍCULO')) else '',
                    'destino_programado': str(row.get('DESTINO PROGRAMADO', '')) if pd.notna(row.get('DESTINO PROGRAMADO')) else '',
                    'servico_executar': str(row.get('SERVIÇO A EXECUTAR', '')) if pd.notna(row.get('SERVIÇO A EXECUTAR')) else '',
                    'status': str(row.get('STATUS', 'EM MANUTENÇÃO')) if pd.notna(row.get('STATUS')) else 'EM MANUTENÇÃO',
                    'data_entrada': str(row.get('DATA ENTRADA', '')) if pd.notna(row.get('DATA ENTRADA')) else '',
                    'data_saida': str(row.get('DATA SAÍDA', '')) if pd.notna(row.get('DATA SAÍDA')) else '',
                    'nr_of': str(row.get('NRº OF', '')) if pd.notna(row.get('NRº OF')) else '',
                    'obs': str(row.get('OBS', '')) if pd.notna(row.get('OBS')) else ''
                }
                self.ctrl.adicionar_registro(dados)
                novos += 1
                
            InfoBar.success("Sucesso", f"Importação concluída! {novos} registro(s) adicionados.", parent=self)
            self.carregar_dados()
        except Exception as e:
            InfoBar.error("Erro", f"Falha ao importar planilha: {e}", parent=self)

    def _abrir_relatorio(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Relatório PDF", "relatorio_manutencoes.pdf", "PDF Files (*.pdf)"
        )
        if caminho:
            try:
                from src.services.export_service import ExportService
                service = ExportService()
                service.gerar_pdf(self.df_atual, self.ctrl.obter_estatisticas(), caminho)
                InfoBar.success("Sucesso", f"Relatório gerado em:\n{caminho}", parent=self)
            except Exception as e:
                InfoBar.error("Erro", f"Falha ao gerar relatório: {e}", parent=self)
