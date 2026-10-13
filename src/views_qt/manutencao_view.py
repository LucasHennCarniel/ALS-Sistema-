"""
Interface Principal de Registros de Manutenção com QFluentWidgets
Visual Corporativo com Ícones Vetoriais Fluent e Endpoints Completos
"""
import os
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
    TableWidget, IconWidget, FluentIcon as FIF, InfoBar, MessageBox
)

from src.views_qt.dialogs import FormRegistroDialog, ImportarOpcoesDialog
from src.views_qt.theme_styles import ContrastCard, CorporateStatCard


def ler_planilha_inteligente(caminho):
    """Lê planilha CSV ou Excel descobrindo automaticamente a linha de cabeçalho que contém PLACA"""
    if caminho.lower().endswith('.csv'):
        df = pd.read_csv(caminho)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df

    for h in [0, 1, 2, 3]:
        try:
            df = pd.read_excel(caminho, header=h)
            cols = [str(c).strip().upper() for c in df.columns]
            if 'PLACA' in cols:
                df.columns = cols
                return df
        except Exception:
            continue

    df = pd.read_excel(caminho)
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df


def formatar_valor_data(val):
    """Converte Timestamp/datetime/string do Excel para dd/mm/yyyy"""
    if pd.isna(val) or val is None:
        return ''
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.strftime('%d/%m/%Y')
    s = str(val).strip()
    if not s or s.upper() == 'NAN' or s.upper() == 'NAT':
        return ''
    if ' ' in s and '-' in s:
        try:
            dt = pd.to_datetime(s)
            return dt.strftime('%d/%m/%Y')
        except Exception:
            pass
    return s


class ManutencaoView(QWidget):
    """View de Manutenções estilo Fluent Design Corporativo"""
    
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
        
        # 1. Cabeçalho com Ícone Vetorial e Título
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        header_icon = IconWidget(FIF.DOCUMENT, self)
        header_icon.setFixedSize(26, 26)
        title = TitleLabel("Registros de Manutenção", self)
        header_layout.addWidget(header_icon)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 2. Cards Corporativos de Estatísticas
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        
        self.card_total = CorporateStatCard("Total de Registros", "0", FIF.DOCUMENT, "#607D8B", self)
        self.card_servico = CorporateStatCard("Em Serviço", "0", FIF.SETTING, "#D97706", self)
        self.card_finalizados = CorporateStatCard("Finalizados", "0", FIF.ACCEPT, "#4CAF50", self)
        self.card_tempo = CorporateStatCard("Tempo Médio", "0 d", FIF.HISTORY, "#0284C7", self)
        self.card_placas = CorporateStatCard("Placas Atendidas", "0", FIF.CAR, "#475569", self)
        
        self.cards = [
            self.card_total, self.card_servico, self.card_finalizados,
            self.card_tempo, self.card_placas
        ]
        for c in self.cards:
            stats_layout.addWidget(c)
        layout.addLayout(stats_layout)
        
        # 3. Barra de Ações (Botões com Ícones Vetoriais)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.btn_novo = PrimaryPushButton("Novo Registro", self, FIF.ADD)
        self.btn_novo.clicked.connect(lambda *_: self._novo_registro())
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
        
        self.btn_relatorio = PushButton("Relatório PDF", self, FIF.DOCUMENT)
        self.btn_relatorio.clicked.connect(lambda *_: self._abrir_relatorio())
        actions_layout.addWidget(self.btn_relatorio)
        
        self.btn_exportar = PushButton("Exportar Excel", self, FIF.SHARE)
        self.btn_exportar.clicked.connect(lambda *_: self._exportar_dados())
        actions_layout.addWidget(self.btn_exportar)
        
        self.btn_importar = PushButton("Importar Planilha", self, FIF.DOWNLOAD)
        self.btn_importar.clicked.connect(lambda *_: self._importar_dados())
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
        self.combo_filtro_status.addItems(["EM MANUTENÇÃO", "EM SERVIÇO", "FINALIZADO", "AGUARDANDO PEÇAS"])
        self.combo_filtro_status.currentTextChanged.connect(self._aplicar_filtro_busca)
        self.combo_filtro_status.setFixedWidth(180)
        filters_layout.addWidget(self.combo_filtro_status)
        
        self.btn_limpar_filtro = PushButton("Limpar Filtros", self)
        self.btn_limpar_filtro.clicked.connect(lambda *_: self._limpar_filtros())
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
            InfoBar.error("Erro", f"Falha ao carregar registros: {e}", parent=self.window())

    def _render_tabela(self, df):
        if df is None or df.empty:
            self.table.setRowCount(0)
            return
            
        self.table.setRowCount(len(df))
        for row_idx, (_, row) in enumerate(df.iterrows()):
            for col_idx, col_name in enumerate(self.COLUNAS):
                val = row.get(col_name, '')
                if pd.isna(val) or str(val) == 'None':
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

    def _aplicar_filtro_busca(self, *_):
        if self.df_atual is None or self.df_atual.empty:
            return
            
        termo = self.search_input.text().strip().lower()
        status_filtro = self.combo_filtro_status.currentText()
        
        df_filtrado = self.df_atual.copy()
        
        if status_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['STATUS'].astype(str).str.upper() == status_filtro.upper()]
            
        if termo:
            mascara = (
                df_filtrado['PLACA'].astype(str).str.lower().str.contains(termo, na=False) |
                df_filtrado['VEÍCULO'].astype(str).str.lower().str.contains(termo, na=False) |
                df_filtrado['SERVIÇO A EXECUTAR'].astype(str).str.lower().str.contains(termo, na=False) |
                df_filtrado['DESTINO PROGRAMADO'].astype(str).str.lower().str.contains(termo, na=False)
            )
            df_filtrado = df_filtrado[mascara]
            
        self._render_tabela(df_filtrado)

    def _limpar_filtros(self):
        self.search_input.clear()
        self.combo_filtro_status.setCurrentIndex(0)
        self._render_tabela(self.df_atual)

    def _novo_registro(self):
        dialog = FormRegistroDialog(self.window(), None, self.veiculo_ctrl, self.destino_ctrl)
        if dialog.exec():
            dados = dialog.obter_dados()
            if not dados.get('placa'):
                InfoBar.warning("Atenção", "Informe a Placa do veículo.", parent=self.window())
                return
            sucesso, msg = self.ctrl.adicionar_registro(dados)
            if sucesso:
                # Atualiza última KM do veículo se maior
                if dados.get('km', 0) > 0:
                    self.veiculo_ctrl.atualizar_km(dados['placa'], dados['km'])
                InfoBar.success("Sucesso", "Registro criado com sucesso!", parent=self.window())
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self.window())

    def _obter_id_linha_selecionada(self):
        row = self.table.currentRow()
        if row < 0:
            itens = self.table.selectedItems()
            if itens:
                row = itens[0].row()
        if row >= 0:
            id_item = self.table.item(row, 0)
            if id_item:
                try:
                    return int(id_item.text())
                except Exception:
                    pass
        return None

    def _on_row_double_click(self, item):
        if item:
            self.table.selectRow(item.row())
        self._editar_selecionado()

    def _editar_selecionado(self):
        id_reg = self._obter_id_linha_selecionada()
        if not id_reg:
            InfoBar.warning("Atenção", "Selecione uma linha na tabela para editar.", parent=self.window())
            return
            
        registro = self.ctrl.obter_registro_por_id(id_reg)
        if not registro:
            InfoBar.error("Erro", f"Registro ID {id_reg} não encontrado no banco.", parent=self.window())
            return
            
        dialog = FormRegistroDialog(self.window(), registro, self.veiculo_ctrl, self.destino_ctrl)
        if dialog.exec():
            dados = dialog.obter_dados()
            sucesso, msg = self.ctrl.atualizar_registro(id_reg, dados)
            if sucesso:
                InfoBar.success("Sucesso", "Registro atualizado com sucesso!", parent=self.window())
                self.carregar_dados()
            else:
                InfoBar.error("Erro", msg, parent=self.window())

    def _excluir_selecionado(self):
        linhas = set(item.row() for item in self.table.selectedItems())
        if not linhas and self.table.currentRow() >= 0:
            linhas.add(self.table.currentRow())
            
        if not linhas:
            InfoBar.warning("Atenção", "Selecione um ou mais registros na tabela para excluir.", parent=self.window())
            return
            
        qtd = len(linhas)
        msg_box = MessageBox(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir {qtd} registro(s) selecionado(s)?",
            self.window()
        )
        msg_box.yesButton.setText("Excluir")
        msg_box.cancelButton.setText("Cancelar")
        if msg_box.exec():
            ids = []
            for r in linhas:
                item_id = self.table.item(r, 0)
                if item_id:
                    try:
                        ids.append(int(item_id.text()))
                    except Exception:
                        pass
                        
            if len(ids) == 1:
                self.ctrl.excluir_registro(ids[0])
            elif len(ids) > 1:
                self.ctrl.excluir_multiplos(ids)
                
            InfoBar.success("Sucesso", f"{len(ids)} registro(s) excluído(s) com sucesso!", parent=self.window())
            self.carregar_dados()

    def _exportar_dados(self):
        if self.df_atual is None or self.df_atual.empty:
            InfoBar.warning("Atenção", "Não há registros na tabela para exportar.", parent=self.window())
            return
            
        caminho, _ = QFileDialog.getSaveFileName(
            self.window(), "Exportar para Excel", "manutencoes_als.xlsx", "Excel Files (*.xlsx)"
        )
        if caminho:
            try:
                from src.services.export_service import ExportService
                service = ExportService()
                service.exportar_excel(self.df_atual, caminho)
                InfoBar.success("Sucesso", f"Planilha exportada com sucesso!", parent=self.window())
                try:
                    os.startfile(caminho)
                except Exception:
                    pass
            except Exception as e:
                InfoBar.error("Erro", f"Falha na exportação: {e}", parent=self.window())

    def _importar_dados(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self.window(), "Importar Planilha (Manutenções ou Veículos)", "", "Planilhas (*.xlsx *.xls *.csv)"
        )
        if not caminho:
            return
            
        try:
            df = ler_planilha_inteligente(caminho)
            if 'PLACA' not in df.columns:
                InfoBar.error(
                    "Arquivo Inválido",
                    f"Não foi encontrada a coluna 'PLACA' na planilha.\nColunas lidas: {', '.join(df.columns[:6])}",
                    parent=self.window()
                )
                return

            # Pede o modo de importação ao usuário
            dlg_opcoes = ImportarOpcoesDialog(self.window(), os.path.basename(caminho))
            if not dlg_opcoes.exec():
                return
            modo = dlg_opcoes.obter_modo()

            # Verifica se é planilha de Veículos (ex: Frota, Placa, Marca, Modelo, Km Atual) ou de Manutenção
            eh_planilha_manutencao = any(
                c in df.columns for c in ['DATA ENTRADA', 'SERVIÇO A EXECUTAR', 'DESTINO PROGRAMADO', 'NR° OF', 'NRº OF']
            )

            if not eh_planilha_manutencao:
                # Redireciona automaticamente para importação de veículos!
                win = self.window()
                if hasattr(win, 'veiculos_view'):
                    novos, atualizados = win.veiculos_view.processar_dataframe_veiculos(df, modo)
                    win.veiculos_view.carregar_dados()
                    InfoBar.success(
                        "Planilha de Veículos Importada",
                        f"Foram processados: {novos} veículo(s) novo(s) e {atualizados} atualizado(s)!",
                        parent=self.window()
                    )
                    return

            # Processamento de Planilha de Manutenção
            conn = self.ctrl.model.conn
            cursor = conn.cursor()

            if modo == "substituir":
                cursor.execute("DELETE FROM manutencoes")
                conn.commit()

            novos = 0
            atualizados = 0

            for _, row in df.iterrows():
                placa = str(row.get('PLACA', '')).strip().upper()
                if not placa or placa == 'NAN' or placa == 'NONE':
                    continue

                data_str = formatar_valor_data(row.get('DATA'))
                data_entrada = formatar_valor_data(row.get('DATA ENTRADA'))
                data_saida = formatar_valor_data(row.get('DATA SAÍDA'))

                if not data_str and data_entrada:
                    data_str = data_entrada
                elif not data_entrada and data_str:
                    data_entrada = data_str

                if not data_str and not data_entrada:
                    continue

                km_raw = row.get('KM', 0)
                try:
                    km = float(km_raw) if pd.notna(km_raw) and str(km_raw).lower() != 'xxx' else 0.0
                except Exception:
                    km = 0.0

                veiculo_txt = str(row.get('VEÍCULO', '')).strip().upper() if pd.notna(row.get('VEÍCULO')) else ''
                destino_txt = str(row.get('DESTINO PROGRAMADO', '')).strip().upper() if pd.notna(row.get('DESTINO PROGRAMADO')) else ''
                servico_txt = str(row.get('SERVIÇO A EXECUTAR', '')).strip() if pd.notna(row.get('SERVIÇO A EXECUTAR')) else ''
                status_txt = str(row.get('STATUS', '')).strip().upper() if pd.notna(row.get('STATUS')) else ''
                of_val = row.get('NR° OF') if 'NR° OF' in df.columns else row.get('NRº OF', '')
                of_txt = str(of_val).strip() if pd.notna(of_val) else ''
                obs_txt = str(row.get('OBS', '')).strip() if pd.notna(row.get('OBS')) else ''

                dados = {
                    'data': data_str,
                    'placa': placa,
                    'km': km,
                    'veiculo': veiculo_txt,
                    'destino_programado': destino_txt,
                    'servico_executar': servico_txt,
                    'status': status_txt,
                    'data_entrada': data_entrada,
                    'data_saida': data_saida,
                    'nr_of': of_txt,
                    'obs': obs_txt
                }

                # Verifica se já existe registro idêntico (placa + data + data_entrada)
                cursor.execute(
                    "SELECT id FROM manutencoes WHERE placa = ? AND data = ? AND data_entrada = ?",
                    (placa, data_str, data_entrada)
                )
                existente = cursor.fetchone()

                if existente:
                    if modo == "novo":
                        continue
                    elif modo == "atualizar":
                        self.ctrl.atualizar_registro(existente[0], dados)
                        atualizados += 1
                else:
                    self.ctrl.adicionar_registro(dados)
                    novos += 1

                # Garante cadastro do veículo e destino
                if placa and not self.veiculo_ctrl.obter_veiculo_por_placa(placa):
                    self.veiculo_ctrl.adicionar_veiculo(veiculo_txt or 'FROTA', placa, 'Importado da Planilha', km)
                if destino_txt:
                    self.destino_ctrl.adicionar_destino(destino_txt)

            self.carregar_dados()
            win = self.window()
            if hasattr(win, 'veiculos_view'):
                win.veiculos_view.carregar_dados()

            InfoBar.success(
                "Importação Concluída",
                f"{novos} novo(s) registro(s) adicionado(s) e {atualizados} atualizado(s)!",
                parent=self.window()
            )
        except Exception as e:
            InfoBar.error("Erro na Importação", f"Falha ao importar planilha: {e}", parent=self.window())

    def _abrir_relatorio(self):
        if self.df_atual is None or self.df_atual.empty:
            InfoBar.warning("Atenção", "Não há registros na tabela para gerar relatório.", parent=self.window())
            return
            
        caminho, _ = QFileDialog.getSaveFileName(
            self.window(), "Salvar Relatório PDF", "relatorio_manutencoes.pdf", "PDF Files (*.pdf)"
        )
        if caminho:
            try:
                from src.services.export_service import ExportService
                service = ExportService()
                service.gerar_pdf(self.df_atual, self.ctrl.obter_estatisticas(), caminho)
                InfoBar.success("Sucesso", "Relatório PDF gerado com sucesso!", parent=self.window())
                try:
                    os.startfile(caminho)
                except Exception:
                    pass
            except Exception as e:
                InfoBar.error("Erro", f"Falha ao gerar relatório: {e}", parent=self.window())
