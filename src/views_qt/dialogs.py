"""
Diálogos corporativos com QFluentWidgets e Ícones Vetoriais Fluent
"""
from datetime import datetime
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
)
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, BodyLabel, LineEdit, 
    TextEdit, ComboBox, DateEdit, DoubleSpinBox, SwitchButton,
    IconWidget, FluentIcon as FIF
)


class FormRegistroDialog(MessageBoxBase):
    """Diálogo corporativo para Adicionar / Editar Registro de Manutenção"""
    
    def __init__(self, parent=None, registro=None, veiculo_ctrl=None, destino_ctrl=None):
        super().__init__(parent)
        self.registro = registro
        self.veiculo_ctrl = veiculo_ctrl
        self.destino_ctrl = destino_ctrl
        
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        icone = FIF.EDIT if registro else FIF.ADD
        icon_w = IconWidget(icone, self)
        icon_w.setFixedSize(22, 22)
        titulo_texto = "Editar Registro de Manutenção" if registro else "Novo Registro de Manutenção"
        self.titleLabel = SubtitleLabel(titulo_texto, self)
        header_row.addWidget(icon_w)
        header_row.addWidget(self.titleLabel)
        header_row.addStretch()
        self.viewLayout.addLayout(header_row)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(12)
        
        # 1. Data e Placa
        form_layout.addWidget(BodyLabel("Data:"), 0, 0)
        self.input_data = DateEdit(self)
        self.input_data.setDisplayFormat("dd/MM/yyyy")
        self.input_data.setDate(QDate.currentDate())
        form_layout.addWidget(self.input_data, 0, 1)
        
        form_layout.addWidget(BodyLabel("Placa:"), 0, 2)
        self.combo_placa = ComboBox(self)
        self.combo_placa.setPlaceholderText("Selecione ou digite...")
        self._carregar_placas()
        form_layout.addWidget(self.combo_placa, 0, 3)
        
        # 2. KM e Veículo
        form_layout.addWidget(BodyLabel("KM:"), 1, 0)
        self.input_km = DoubleSpinBox(self)
        self.input_km.setRange(0, 9999999)
        self.input_km.setDecimals(0)
        form_layout.addWidget(self.input_km, 1, 1)
        
        form_layout.addWidget(BodyLabel("Veículo / Tipo:"), 1, 2)
        self.input_veiculo = LineEdit(self)
        self.input_veiculo.setPlaceholderText("Ex: CAVALO, CARRETA...")
        form_layout.addWidget(self.input_veiculo, 1, 3)
        
        # 3. Destino e Status
        form_layout.addWidget(BodyLabel("Destino Programado:"), 2, 0)
        self.combo_destino = ComboBox(self)
        self._carregar_destinos()
        form_layout.addWidget(self.combo_destino, 2, 1)
        
        form_layout.addWidget(BodyLabel("Status:"), 2, 2)
        self.combo_status = ComboBox(self)
        self.combo_status.addItems([
            "EM MANUTENÇÃO",
            "FINALIZADO",
            "AGUARDANDO PEÇAS",
            "PREVENTIVA",
            "CORRETIVA",
            "SOCORRO"
        ])
        form_layout.addWidget(self.combo_status, 2, 3)
        
        # 4. Data Entrada e Saída
        form_layout.addWidget(BodyLabel("Data Entrada:"), 3, 0)
        self.input_entrada = DateEdit(self)
        self.input_entrada.setDisplayFormat("dd/MM/yyyy")
        self.input_entrada.setDate(QDate.currentDate())
        form_layout.addWidget(self.input_entrada, 3, 1)
        
        form_layout.addWidget(BodyLabel("Data Saída:"), 3, 2)
        self.input_saida = LineEdit(self)
        self.input_saida.setPlaceholderText("dd/mm/aaaa (vazio se em aberto)")
        form_layout.addWidget(self.input_saida, 3, 3)
        
        # 5. Nº OF
        form_layout.addWidget(BodyLabel("Nº OF:"), 4, 0)
        self.input_of = LineEdit(self)
        self.input_of.setPlaceholderText("Número da Ordem de Serviço")
        form_layout.addWidget(self.input_of, 4, 1, 1, 3)
        
        # 6. Serviço a Executar
        form_layout.addWidget(BodyLabel("Serviço a Executar:"), 5, 0)
        self.input_servico = TextEdit(self)
        self.input_servico.setPlaceholderText("Descrição detalhada do serviço...")
        self.input_servico.setFixedHeight(70)
        form_layout.addWidget(self.input_servico, 5, 1, 1, 3)
        
        # 7. Observações
        form_layout.addWidget(BodyLabel("Observações:"), 6, 0)
        self.input_obs = TextEdit(self)
        self.input_obs.setPlaceholderText("Observações adicionais...")
        self.input_obs.setFixedHeight(60)
        form_layout.addWidget(self.input_obs, 6, 1, 1, 3)
        
        self.viewLayout.addLayout(form_layout)
        
        if self.registro:
            self._preencher_dados()
            
        self.combo_placa.currentTextChanged.connect(self._ao_mudar_placa)
        
        self.yesButton.setText("Salvar")
        self.cancelButton.setText("Cancelar")
        self.widget.setMinimumWidth(700)

    def _carregar_placas(self):
        if self.veiculo_ctrl:
            try:
                veiculos = self.veiculo_ctrl.obter_todos()
                placas = [v['placa'] for v in veiculos if v.get('placa')]
                self.combo_placa.addItems(sorted(list(set(placas))))
            except Exception:
                pass

    def _carregar_destinos(self):
        self.combo_destino.addItem("")
        if self.destino_ctrl:
            try:
                destinos = self.destino_ctrl.obter_todos()
                for d in destinos:
                    nome = d.get('nome') or d.get('destino')
                    if nome:
                        self.combo_destino.addItem(str(nome))
            except Exception:
                pass

    def _ao_mudar_placa(self, placa):
        if not placa or not self.veiculo_ctrl:
            return
        veiculo = self.veiculo_ctrl.obter_veiculo_por_placa(placa)
        if veiculo:
            tipo = veiculo.get('tipo_veiculo') or veiculo.get('tipo') or ''
            desc = veiculo.get('descricao') or ''
            self.input_veiculo.setText(f"{tipo} {desc}".strip())
            km = veiculo.get('ultima_km') or 0
            if km > 0 and self.input_km.value() == 0:
                self.input_km.setValue(float(km))

    def _preencher_dados(self):
        r = self.registro
        d_str = str(r.get('DATA') or r.get('data') or '')
        try:
            if d_str and '/' in d_str:
                p = d_str.split('/')
                self.input_data.setDate(QDate(int(p[2]), int(p[1]), int(p[0])))
        except Exception:
            pass
            
        placa = str(r.get('PLACA') or r.get('placa') or '')
        idx = self.combo_placa.findText(placa)
        if idx >= 0:
            self.combo_placa.setCurrentIndex(idx)
        else:
            self.combo_placa.addItem(placa)
            self.combo_placa.setCurrentText(placa)
            
        try:
            km = float(r.get('KM') or r.get('km') or 0)
            self.input_km.setValue(km)
        except Exception:
            pass
            
        self.input_veiculo.setText(str(r.get('VEÍCULO') or r.get('veiculo') or ''))
        
        dest = str(r.get('DESTINO PROGRAMADO') or r.get('destino_programado') or '')
        idx_d = self.combo_destino.findText(dest)
        if idx_d >= 0:
            self.combo_destino.setCurrentIndex(idx_d)
        else:
            self.combo_destino.setCurrentText(dest)
            
        st = str(r.get('STATUS') or r.get('status') or 'EM MANUTENÇÃO')
        idx_st = self.combo_status.findText(st)
        if idx_st >= 0:
            self.combo_status.setCurrentIndex(idx_st)
            
        ent_str = str(r.get('DATA ENTRADA') or r.get('data_entrada') or '')
        try:
            if ent_str and '/' in ent_str:
                p = ent_str.split('/')
                self.input_entrada.setDate(QDate(int(p[2]), int(p[1]), int(p[0])))
        except Exception:
            pass
            
        self.input_saida.setText(str(r.get('DATA SAÍDA') or r.get('data_saida') or ''))
        self.input_of.setText(str(r.get('NRº OF') or r.get('nr_of') or ''))
        self.input_servico.setText(str(r.get('SERVIÇO A EXECUTAR') or r.get('servico_executar') or ''))
        self.input_obs.setText(str(r.get('OBS') or r.get('obs') or ''))

    def obter_dados(self):
        d = self.input_data.date()
        data_str = f"{d.day():02d}/{d.month():02d}/{d.year()}"
        
        ent = self.input_entrada.date()
        entrada_str = f"{ent.day():02d}/{ent.month():02d}/{ent.year()}"
        
        return {
            'data': data_str,
            'placa': self.combo_placa.currentText().strip().upper(),
            'km': self.input_km.value(),
            'veiculo': self.input_veiculo.text().strip().upper(),
            'destino_programado': self.combo_destino.currentText().strip(),
            'servico_executar': self.input_servico.toPlainText().strip(),
            'status': self.combo_status.currentText().strip(),
            'data_entrada': entrada_str,
            'data_saida': self.input_saida.text().strip(),
            'nr_of': self.input_of.text().strip(),
            'obs': self.input_obs.toPlainText().strip()
        }


class FormVeiculoDialog(MessageBoxBase):
    """Diálogo corporativo para Adicionar / Editar Veículo"""
    
    def __init__(self, parent=None, veiculo=None):
        super().__init__(parent)
        self.veiculo = veiculo
        
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        icone = FIF.EDIT if veiculo else FIF.CAR
        icon_w = IconWidget(icone, self)
        icon_w.setFixedSize(22, 22)
        titulo_texto = "Editar Veículo da Frota" if veiculo else "Novo Veículo na Frota"
        self.titleLabel = SubtitleLabel(titulo_texto, self)
        header_row.addWidget(icon_w)
        header_row.addWidget(self.titleLabel)
        header_row.addStretch()
        self.viewLayout.addLayout(header_row)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(12)
        
        form_layout.addWidget(BodyLabel("Placa:"), 0, 0)
        self.input_placa = LineEdit(self)
        self.input_placa.setPlaceholderText("Ex: ABC1D23")
        form_layout.addWidget(self.input_placa, 0, 1)
        
        form_layout.addWidget(BodyLabel("Tipo / Marca:"), 1, 0)
        self.combo_tipo = ComboBox(self)
        self.combo_tipo.addItems([
            "CAVALO", "CARRETA", "CARRETA 2 EIXOS", 
            "BUG", "BUG 1", "BUG 2", "LS", "SR", 
            "DAF", "VOLVO", "SCANIA", "MERCEDES-BENZ", "OUTRO"
        ])
        form_layout.addWidget(self.combo_tipo, 1, 1)
        
        form_layout.addWidget(BodyLabel("Descrição / Modelo:"), 2, 0)
        self.input_desc = LineEdit(self)
        self.input_desc.setPlaceholderText("Ex: XF FTT 530 - BRANCA")
        form_layout.addWidget(self.input_desc, 2, 1)
        
        form_layout.addWidget(BodyLabel("Última KM:"), 3, 0)
        self.input_km = DoubleSpinBox(self)
        self.input_km.setRange(0, 9999999)
        self.input_km.setDecimals(0)
        form_layout.addWidget(self.input_km, 3, 1)
        
        form_layout.addWidget(BodyLabel("Ativo:"), 4, 0)
        self.switch_ativo = SwitchButton(self)
        self.switch_ativo.setChecked(True)
        form_layout.addWidget(self.switch_ativo, 4, 1)
        
        self.viewLayout.addLayout(form_layout)
        
        if self.veiculo:
            self._preencher_dados()
            
        self.yesButton.setText("Salvar")
        self.cancelButton.setText("Cancelar")
        self.widget.setMinimumWidth(500)

    def _preencher_dados(self):
        v = self.veiculo
        self.input_placa.setText(str(v.get('placa', '')))
        
        tipo = str(v.get('tipo_veiculo', '') or v.get('tipo', ''))
        idx = self.combo_tipo.findText(tipo)
        if idx >= 0:
            self.combo_tipo.setCurrentIndex(idx)
        else:
            self.combo_tipo.addItem(tipo)
            self.combo_tipo.setCurrentText(tipo)
            
        self.input_desc.setText(str(v.get('descricao', '')))
        try:
            self.input_km.setValue(float(v.get('ultima_km', 0)))
        except Exception:
            pass
        self.switch_ativo.setChecked(bool(v.get('ativo', 1)))

    def obter_dados(self):
        return {
            'placa': self.input_placa.text().strip().upper(),
            'tipo': self.combo_tipo.currentText().strip().upper(),
            'descricao': self.input_desc.text().strip().upper(),
            'km_inicial': self.input_km.value(),
            'ativo': 1 if self.switch_ativo.isChecked() else 0
        }


class FormNotaDialog(MessageBoxBase):
    """Diálogo corporativo para Adicionar / Editar Nota"""
    
    def __init__(self, parent=None, nota=None):
        super().__init__(parent)
        self.nota = nota
        
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        icone = FIF.EDIT if nota else FIF.ADD
        icon_w = IconWidget(icone, self)
        icon_w.setFixedSize(22, 22)
        titulo_texto = "Editar Anotação" if nota else "Nova Anotação Interna"
        self.titleLabel = SubtitleLabel(titulo_texto, self)
        header_row.addWidget(icon_w)
        header_row.addWidget(self.titleLabel)
        header_row.addStretch()
        self.viewLayout.addLayout(header_row)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(12)
        
        form_layout.addWidget(BodyLabel("Data Programada:"), 0, 0)
        self.input_data = DateEdit(self)
        self.input_data.setDisplayFormat("dd/MM/yyyy")
        self.input_data.setDate(QDate.currentDate())
        form_layout.addWidget(self.input_data, 0, 1)
        
        form_layout.addWidget(BodyLabel("Placa / Assunto:"), 1, 0)
        self.input_placa = LineEdit(self)
        self.input_placa.setPlaceholderText("Placa ou assunto da anotação")
        form_layout.addWidget(self.input_placa, 1, 1)
        
        form_layout.addWidget(BodyLabel("Status / Prioridade:"), 2, 0)
        self.combo_status = ComboBox(self)
        self.combo_status.addItems(["PENDENTE", "EM ANDAMENTO", "CONCLUÍDO", "URGENTE"])
        form_layout.addWidget(self.combo_status, 2, 1)
        
        form_layout.addWidget(BodyLabel("Observação:"), 3, 0)
        self.input_obs = TextEdit(self)
        self.input_obs.setPlaceholderText("Escreva os detalhes aqui...")
        self.input_obs.setFixedHeight(120)
        form_layout.addWidget(self.input_obs, 3, 1)
        
        self.viewLayout.addLayout(form_layout)
        
        if self.nota:
            self._preencher_dados()
            
        self.yesButton.setText("Salvar")
        self.cancelButton.setText("Cancelar")
        self.widget.setMinimumWidth(500)

    def _preencher_dados(self):
        n = self.nota
        d_str = str(n.get('data_programada') or '')
        try:
            if d_str and '/' in d_str:
                p = d_str.split('/')
                self.input_data.setDate(QDate(int(p[2]), int(p[1]), int(p[0])))
        except Exception:
            pass
            
        self.input_placa.setText(str(n.get('placa') or n.get('titulo') or ''))
        
        st = str(n.get('status') or n.get('prioridade') or 'PENDENTE')
        idx_s = self.combo_status.findText(st)
        if idx_s >= 0:
            self.combo_status.setCurrentIndex(idx_s)
            
        self.input_obs.setText(str(n.get('observacao') or n.get('conteudo') or ''))

    def obter_dados(self):
        d = self.input_data.date()
        data_str = f"{d.day():02d}/{d.month():02d}/{d.year()}"
        return {
            'data_programada': data_str,
            'placa': self.input_placa.text().strip().upper(),
            'status': self.combo_status.currentText().strip(),
            'observacao': self.input_obs.toPlainText().strip()
        }
