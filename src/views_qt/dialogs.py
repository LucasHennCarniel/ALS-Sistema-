"""
Diálogos corporativos com QFluentWidgets e Ícones Vetoriais Fluent
"""
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QCompleter
)
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, BodyLabel, LineEdit, 
    TextEdit, ComboBox, EditableComboBox,
    SwitchButton, RadioButton, IconWidget, FluentIcon as FIF, isDarkTheme
)
from src.services.manutencao.status import STATUS_VALIDOS, STATUS_EM_MANUTENCAO
from src.services.manutencao.normalizar_status import normalizar_status


def _configurar_mascara_data(campo: LineEdit):
    """Formata automaticamente barras (dd/mm/aaaa) ao digitar números, sem travar o Backspace."""
    estado = {"ultimo": campo.text()}

    def _ao_editar(texto: str):
        antigo = estado["ultimo"]
        if len(texto) > len(antigo):
            nums = "".join(ch for ch in texto if ch.isdigit())
            if len(texto) == 2 and len(nums) == 2:
                novo = f"{nums}/"
                estado["ultimo"] = novo
                campo.setText(novo)
                campo.setCursorPosition(len(novo))
                return
            elif len(texto) == 5 and texto[2] == "/" and len(nums) == 4:
                novo = f"{nums[:2]}/{nums[2:4]}/"
                estado["ultimo"] = novo
                campo.setText(novo)
                campo.setCursorPosition(len(novo))
                return
            elif len(nums) == 8 and "/" not in texto:
                novo = f"{nums[:2]}/{nums[2:4]}/{nums[4:8]}"
                estado["ultimo"] = novo
                campo.setText(novo)
                campo.setCursorPosition(len(novo))
                return
        estado["ultimo"] = texto

    campo.textEdited.connect(_ao_editar)


def _normalizar_data(texto: str, padrao_hoje: bool = True) -> str:
    """Normaliza uma string de data para o formato dd/mm/aaaa."""
    t = str(texto or "").strip()
    if not t or t.lower() == "none":
        return datetime.now().strftime("%d/%m/%Y") if padrao_hoje else ""
    t = t.replace("-", "/")
    apenas_nums = "".join(ch for ch in t if ch.isdigit())
    if "/" not in t and len(apenas_nums) == 8:
        return f"{apenas_nums[:2]}/{apenas_nums[2:4]}/{apenas_nums[4:8]}"
    if "/" not in t and len(apenas_nums) == 6:
        return f"{apenas_nums[:2]}/{apenas_nums[2:4]}/20{apenas_nums[4:6]}"
    partes = t.split("/")
    if len(partes) == 3:
        try:
            d = int(partes[0])
            m = int(partes[1])
            y = int(partes[2])
            if y < 100:
                y += 2000
            return f"{d:02d}/{m:02d}/{y:04d}"
        except Exception:
            pass
    return t


def _formatar_km(valor) -> str:
    """Converte valor numérico de KM em texto inteiro limpo para exibição no LineEdit."""
    try:
        v = float(valor or 0)
        return str(int(round(v)))
    except Exception:
        return "0"


def _parse_km(texto: str) -> float:
    """Converte texto digitado no campo KM para float, aceitando separador de milhar."""
    t = str(texto or "").strip()
    if not t:
        return 0.0
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif "." in t:
        partes = t.split(".")
        if len(partes) > 2 or (len(partes) == 2 and len(partes[1]) == 3):
            t = t.replace(".", "")
    try:
        return float(t)
    except Exception:
        nums = "".join(ch for ch in t if ch.isdigit())
        return float(nums) if nums else 0.0


def _aplicar_estilo_modal(dialog: MessageBoxBase):
    """Garante contraste adequado do card central do diálogo no Modo Padrão Cinza Suave."""
    if not isDarkTheme():
        dialog.widget.setStyleSheet("""
            #centerWidget {
                background-color: #D5DFE8;
                border: 1px solid #64748B;
                border-radius: 10px;
            }
            #buttonGroup {
                background-color: #C6D0DA;
                border-top: 1px solid #94A3B8;
            }
        """)


class FormRegistroDialog(MessageBoxBase):
    """Diálogo corporativo para Adicionar / Editar Registro de Manutenção"""
    
    def __init__(self, parent=None, registro=None, veiculo_ctrl=None, destino_ctrl=None):
        super().__init__(parent)
        self.registro = registro
        self.veiculo_ctrl = veiculo_ctrl
        self.destino_ctrl = destino_ctrl
        _aplicar_estilo_modal(self)
        
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        icone = FIF.EDIT if registro else FIF.ADD
        icon_w = IconWidget(icone, self.widget)
        icon_w.setFixedSize(22, 22)
        titulo_texto = "Editar Registro de Manutenção" if registro else "Novo Registro de Manutenção"
        self.titleLabel = SubtitleLabel(titulo_texto, self.widget)
        header_row.addWidget(icon_w)
        header_row.addWidget(self.titleLabel)
        header_row.addStretch()
        self.viewLayout.addLayout(header_row)
        
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(12)
        form_layout.setColumnStretch(1, 1)
        form_layout.setColumnStretch(3, 1)
        
        hoje_str = datetime.now().strftime("%d/%m/%Y")
        
        # 1. Data e Placa
        form_layout.addWidget(BodyLabel("Data:", self.widget), 0, 0)
        self.input_data = LineEdit(self.widget)
        self.input_data.setPlaceholderText("dd/mm/aaaa")
        self.input_data.setText(hoje_str)
        self.input_data.setClearButtonEnabled(True)
        self.input_data.setMinimumWidth(220)
        _configurar_mascara_data(self.input_data)
        form_layout.addWidget(self.input_data, 0, 1)
        
        form_layout.addWidget(BodyLabel("Placa:", self.widget), 0, 2)
        self.combo_placa = EditableComboBox(self.widget)
        self.combo_placa.setPlaceholderText("Selecione ou digite a placa...")
        self.combo_placa.setMaxVisibleItems(10)
        self.combo_placa.setMinimumWidth(220)
        self._carregar_placas()
        form_layout.addWidget(self.combo_placa, 0, 3)
        
        # 2. KM e Veículo
        form_layout.addWidget(BodyLabel("KM:", self.widget), 1, 0)
        self.input_km = LineEdit(self.widget)
        self.input_km.setPlaceholderText("Ex: 150000")
        self.input_km.setText("0")
        self.input_km.setClearButtonEnabled(True)
        self.input_km.setMinimumWidth(220)
        form_layout.addWidget(self.input_km, 1, 1)
        
        form_layout.addWidget(BodyLabel("Veículo / Tipo:", self.widget), 1, 2)
        self.input_veiculo = LineEdit(self.widget)
        self.input_veiculo.setPlaceholderText("Ex: CAVALO, CARRETA...")
        self.input_veiculo.setClearButtonEnabled(True)
        self.input_veiculo.setMinimumWidth(220)
        form_layout.addWidget(self.input_veiculo, 1, 3)
        
        # 3. Destino e Status
        form_layout.addWidget(BodyLabel("Destino Programado:", self.widget), 2, 0)
        self.combo_destino = EditableComboBox(self.widget)
        self.combo_destino.setPlaceholderText("Selecione ou digite...")
        self.combo_destino.setMaxVisibleItems(10)
        self.combo_destino.setMinimumWidth(230)
        self._carregar_destinos()
        form_layout.addWidget(self.combo_destino, 2, 1)
        
        form_layout.addWidget(BodyLabel("Status:", self.widget), 2, 2)
        self.combo_status = ComboBox(self.widget)
        self.combo_status.setMaxVisibleItems(10)
        self.combo_status.setMinimumWidth(220)
        self.combo_status.addItems(STATUS_VALIDOS)
        # Novo registro normalmente é um veículo que está entrando em manutenção
        self.combo_status.setCurrentText(STATUS_EM_MANUTENCAO)
        form_layout.addWidget(self.combo_status, 2, 3)
        
        # 4. Data Entrada e Saída
        form_layout.addWidget(BodyLabel("Data Entrada:", self.widget), 3, 0)
        self.input_entrada = LineEdit(self.widget)
        self.input_entrada.setPlaceholderText("dd/mm/aaaa")
        self.input_entrada.setText(hoje_str)
        self.input_entrada.setClearButtonEnabled(True)
        self.input_entrada.setMinimumWidth(220)
        _configurar_mascara_data(self.input_entrada)
        form_layout.addWidget(self.input_entrada, 3, 1)
        
        form_layout.addWidget(BodyLabel("Data Saída:", self.widget), 3, 2)
        self.input_saida = LineEdit(self.widget)
        self.input_saida.setPlaceholderText("dd/mm/aaaa (em aberto)")
        self.input_saida.setClearButtonEnabled(True)
        self.input_saida.setMinimumWidth(220)
        _configurar_mascara_data(self.input_saida)
        form_layout.addWidget(self.input_saida, 3, 3)
        
        # 5. Nº OF
        form_layout.addWidget(BodyLabel("Nº OF:", self.widget), 4, 0)
        self.input_of = LineEdit(self.widget)
        self.input_of.setPlaceholderText("Número da Ordem de Serviço")
        self.input_of.setClearButtonEnabled(True)
        form_layout.addWidget(self.input_of, 4, 1, 1, 3)
        
        # 6. Serviço a Executar
        form_layout.addWidget(BodyLabel("Serviço a Executar:", self.widget), 5, 0)
        self.input_servico = TextEdit(self.widget)
        self.input_servico.setPlaceholderText("Descrição detalhada do serviço...")
        self.input_servico.setFixedHeight(70)
        form_layout.addWidget(self.input_servico, 5, 1, 1, 3)
        
        # 7. Observações
        form_layout.addWidget(BodyLabel("Observações:", self.widget), 6, 0)
        self.input_obs = TextEdit(self.widget)
        self.input_obs.setPlaceholderText("Observações adicionais...")
        self.input_obs.setFixedHeight(60)
        form_layout.addWidget(self.input_obs, 6, 1, 1, 3)
        
        self.viewLayout.addLayout(form_layout)
        
        self.combo_placa.currentTextChanged.connect(self._ao_mudar_placa)
        
        if self.registro:
            self._preencher_dados()
        else:
            if self.combo_placa.currentText():
                self._ao_mudar_placa(self.combo_placa.currentText())
        
        self.yesButton.setText("Salvar")
        self.cancelButton.setText("Cancelar")
        self.widget.setMinimumWidth(780)

    def _carregar_placas(self):
        if self.veiculo_ctrl:
            try:
                veiculos = self.veiculo_ctrl.obter_todos()
                placas = sorted(list({v['placa'].strip().upper() for v in veiculos if v.get('placa')}))
                self.combo_placa.addItems(placas)
                completer = QCompleter(placas, self.combo_placa)
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setFilterMode(Qt.MatchContains)
                completer.setMaxVisibleItems(10)
                self.combo_placa.setCompleter(completer)
            except Exception:
                pass

    def _carregar_destinos(self):
        self.combo_destino.addItem("")
        if self.destino_ctrl:
            try:
                destinos = self.destino_ctrl.obter_todos()
                nomes = []
                for d in destinos:
                    nome = d.get('nome_destino') or d.get('nome') or d.get('destino')
                    if nome:
                        n_str = str(nome).strip()
                        nomes.append(n_str)
                        self.combo_destino.addItem(n_str)
                if nomes:
                    completer = QCompleter(nomes, self.combo_destino)
                    completer.setCaseSensitivity(Qt.CaseInsensitive)
                    completer.setFilterMode(Qt.MatchContains)
                    completer.setMaxVisibleItems(10)
                    self.combo_destino.setCompleter(completer)
            except Exception:
                pass

    def _ao_mudar_placa(self, placa):
        if not placa or not self.veiculo_ctrl:
            return
        veiculo = self.veiculo_ctrl.obter_veiculo_por_placa(placa.strip())
        if veiculo:
            tipo = (veiculo.get('tipo_veiculo') or veiculo.get('tipo') or '').strip()
            self.input_veiculo.setText(tipo)
            if not self.registro:
                km = veiculo.get('ultima_km') or 0
                self.input_km.setText(_formatar_km(km))

    def _preencher_dados(self):
        r = self.registro
        d_str = str(r.get('DATA') or r.get('data') or '').strip()
        if d_str and d_str.lower() != 'none':
            self.input_data.setText(_normalizar_data(d_str, padrao_hoje=True))
            
        placa = str(r.get('PLACA') or r.get('placa') or '').strip().upper()
        idx = self.combo_placa.findText(placa)
        if idx >= 0:
            self.combo_placa.setCurrentIndex(idx)
        self.combo_placa.setText(placa)
            
        km_val = r.get('KM') if r.get('KM') is not None else r.get('km', 0)
        self.input_km.setText(_formatar_km(km_val))
            
        self.input_veiculo.setText(str(r.get('VEÍCULO') or r.get('veiculo') or '').strip())
        
        dest = str(r.get('DESTINO PROGRAMADO') or r.get('destino_programado') or '').strip()
        if dest.lower() == 'none':
            dest = ''
        idx_d = self.combo_destino.findText(dest)
        if idx_d >= 0:
            self.combo_destino.setCurrentIndex(idx_d)
        self.combo_destino.setText(dest)
            
        # Status antigos (ex.: EM SERVIÇO, SOCORRO) aparecem como o equivalente atual
        st = normalizar_status(r.get('STATUS') or r.get('status')) or STATUS_EM_MANUTENCAO
        idx_st = self.combo_status.findText(st)
        if idx_st >= 0:
            self.combo_status.setCurrentIndex(idx_st)
        else:
            self.combo_status.addItem(st)
            self.combo_status.setCurrentText(st)
            
        ent_str = str(r.get('DATA ENTRADA') or r.get('data_entrada') or '').strip()
        if ent_str and ent_str.lower() != 'none':
            self.input_entrada.setText(_normalizar_data(ent_str, padrao_hoje=True))
            
        saida_val = r.get('DATA SAÍDA') or r.get('data_saida') or ''
        saida_str = '' if str(saida_val).strip().lower() == 'none' else str(saida_val).strip()
        self.input_saida.setText(_normalizar_data(saida_str, padrao_hoje=False) if saida_str else '')
        
        of_val = r.get('NRº OF') or r.get('NR° OF') or r.get('nr_of') or ''
        self.input_of.setText('' if str(of_val) == 'None' else str(of_val))
        
        serv_val = r.get('SERVIÇO A EXECUTAR') or r.get('servico_executar') or ''
        self.input_servico.setText('' if str(serv_val) == 'None' else str(serv_val))
        
        obs_val = r.get('OBS') or r.get('obs') or ''
        self.input_obs.setText('' if str(obs_val) == 'None' else str(obs_val))

    def obter_dados(self):
        data_str = _normalizar_data(self.input_data.text(), padrao_hoje=True)
        entrada_str = _normalizar_data(self.input_entrada.text(), padrao_hoje=True)
        saida_raw = self.input_saida.text().strip()
        saida_str = _normalizar_data(saida_raw, padrao_hoje=False) if saida_raw else ""
        
        return {
            'data': data_str,
            'placa': self.combo_placa.text().strip().upper(),
            'km': _parse_km(self.input_km.text()),
            'veiculo': self.input_veiculo.text().strip().upper(),
            'destino_programado': self.combo_destino.text().strip().upper(),
            'servico_executar': self.input_servico.toPlainText().strip(),
            'status': self.combo_status.currentText().strip(),
            'data_entrada': entrada_str,
            'data_saida': saida_str,
            'nr_of': self.input_of.text().strip(),
            'obs': self.input_obs.toPlainText().strip()
        }


class FormVeiculoDialog(MessageBoxBase):
    """Diálogo corporativo para Adicionar / Editar Veículo"""
    
    def __init__(self, parent=None, veiculo=None):
        super().__init__(parent)
        self.veiculo = veiculo
        _aplicar_estilo_modal(self)
        
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        icone = FIF.EDIT if veiculo else FIF.CAR
        icon_w = IconWidget(icone, self.widget)
        icon_w.setFixedSize(22, 22)
        titulo_texto = "Editar Veículo da Frota" if veiculo else "Novo Veículo na Frota"
        self.titleLabel = SubtitleLabel(titulo_texto, self.widget)
        header_row.addWidget(icon_w)
        header_row.addWidget(self.titleLabel)
        header_row.addStretch()
        self.viewLayout.addLayout(header_row)
        
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(12)
        form_layout.setColumnStretch(1, 1)
        
        form_layout.addWidget(BodyLabel("Placa:", self.widget), 0, 0)
        self.input_placa = LineEdit(self.widget)
        self.input_placa.setPlaceholderText("Ex: ABC1D23")
        self.input_placa.setClearButtonEnabled(True)
        self.input_placa.setMinimumWidth(260)
        form_layout.addWidget(self.input_placa, 0, 1)
        
        form_layout.addWidget(BodyLabel("Tipo / Marca:", self.widget), 1, 0)
        self.combo_tipo = EditableComboBox(self.widget)
        self.combo_tipo.setMaxVisibleItems(10)
        self.combo_tipo.setMinimumWidth(260)
        tipos_padrao = [
            "CAVALO", "CARRETA", "CARRETA 1", "CARRETA 2", "CARRETA 2 EIXOS", 
            "BUG", "BUG 1", "BUG 2", "LS", "SR", 
            "DAF", "VOLVO", "SCANIA", "MERCEDES-BENZ", "FIAT", "ROMA", "OUTRO"
        ]
        self.combo_tipo.addItems(tipos_padrao)
        completer_tipo = QCompleter(tipos_padrao, self.combo_tipo)
        completer_tipo.setCaseSensitivity(Qt.CaseInsensitive)
        completer_tipo.setFilterMode(Qt.MatchContains)
        self.combo_tipo.setCompleter(completer_tipo)
        form_layout.addWidget(self.combo_tipo, 1, 1)
        
        form_layout.addWidget(BodyLabel("Descrição / Modelo:", self.widget), 2, 0)
        self.input_desc = LineEdit(self.widget)
        self.input_desc.setPlaceholderText("Ex: XF FTT 530 - BRANCA")
        self.input_desc.setClearButtonEnabled(True)
        self.input_desc.setMinimumWidth(260)
        form_layout.addWidget(self.input_desc, 2, 1)
        
        form_layout.addWidget(BodyLabel("Última KM:", self.widget), 3, 0)
        self.input_km = LineEdit(self.widget)
        self.input_km.setPlaceholderText("Ex: 150000")
        self.input_km.setText("0")
        self.input_km.setClearButtonEnabled(True)
        self.input_km.setMinimumWidth(260)
        form_layout.addWidget(self.input_km, 3, 1)
        
        form_layout.addWidget(BodyLabel("Ativo:", self.widget), 4, 0)
        self.switch_ativo = SwitchButton(self.widget)
        self.switch_ativo.setChecked(True)
        form_layout.addWidget(self.switch_ativo, 4, 1)
        
        self.viewLayout.addLayout(form_layout)
        
        if self.veiculo:
            self._preencher_dados()
            
        self.yesButton.setText("Salvar")
        self.cancelButton.setText("Cancelar")
        self.widget.setMinimumWidth(520)

    def _preencher_dados(self):
        v = self.veiculo
        self.input_placa.setText(str(v.get('placa') or '').strip())
        
        tipo = str(v.get('tipo_veiculo') or v.get('tipo') or '').strip().upper()
        idx = self.combo_tipo.findText(tipo)
        if idx >= 0:
            self.combo_tipo.setCurrentIndex(idx)
        self.combo_tipo.setText(tipo)
            
        desc = v.get('descricao')
        self.input_desc.setText('' if desc is None or str(desc) == 'None' else str(desc))
        self.input_km.setText(_formatar_km(v.get('ultima_km') or 0))
        self.switch_ativo.setChecked(bool(v.get('ativo', 1)))

    def obter_dados(self):
        return {
            'placa': self.input_placa.text().strip().upper(),
            'tipo': self.combo_tipo.text().strip().upper(),
            'descricao': self.input_desc.text().strip().upper(),
            'km_inicial': _parse_km(self.input_km.text()),
            'ativo': 1 if self.switch_ativo.isChecked() else 0
        }


class FormNotaDialog(MessageBoxBase):
    """Diálogo corporativo para Adicionar / Editar Nota"""
    
    def __init__(self, parent=None, nota=None):
        super().__init__(parent)
        self.nota = nota
        _aplicar_estilo_modal(self)
        
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        icone = FIF.EDIT if nota else FIF.ADD
        icon_w = IconWidget(icone, self.widget)
        icon_w.setFixedSize(22, 22)
        titulo_texto = "Editar Anotação" if nota else "Nova Anotação Interna"
        self.titleLabel = SubtitleLabel(titulo_texto, self.widget)
        header_row.addWidget(icon_w)
        header_row.addWidget(self.titleLabel)
        header_row.addStretch()
        self.viewLayout.addLayout(header_row)
        
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(12)
        form_layout.setColumnStretch(1, 1)
        
        form_layout.addWidget(BodyLabel("Data Programada:", self.widget), 0, 0)
        self.input_data = LineEdit(self.widget)
        self.input_data.setPlaceholderText("dd/mm/aaaa")
        self.input_data.setText(datetime.now().strftime("%d/%m/%Y"))
        self.input_data.setClearButtonEnabled(True)
        self.input_data.setMinimumWidth(260)
        _configurar_mascara_data(self.input_data)
        form_layout.addWidget(self.input_data, 0, 1)
        
        form_layout.addWidget(BodyLabel("Placa / Assunto:", self.widget), 1, 0)
        self.input_placa = LineEdit(self.widget)
        self.input_placa.setPlaceholderText("Placa ou assunto da anotação")
        self.input_placa.setClearButtonEnabled(True)
        self.input_placa.setMinimumWidth(260)
        form_layout.addWidget(self.input_placa, 1, 1)
        
        form_layout.addWidget(BodyLabel("Status / Prioridade:", self.widget), 2, 0)
        self.combo_status = ComboBox(self.widget)
        self.combo_status.setMaxVisibleItems(10)
        self.combo_status.setMinimumWidth(260)
        self.combo_status.addItems(["PENDENTE", "EM ANDAMENTO", "CONCLUÍDO", "URGENTE"])
        form_layout.addWidget(self.combo_status, 2, 1)
        
        form_layout.addWidget(BodyLabel("Observação:", self.widget), 3, 0)
        self.input_obs = TextEdit(self.widget)
        self.input_obs.setPlaceholderText("Escreva os detalhes aqui...")
        self.input_obs.setFixedHeight(120)
        form_layout.addWidget(self.input_obs, 3, 1)
        
        self.viewLayout.addLayout(form_layout)
        
        if self.nota:
            self._preencher_dados()
            
        self.yesButton.setText("Salvar")
        self.cancelButton.setText("Cancelar")
        self.widget.setMinimumWidth(520)

    def _preencher_dados(self):
        n = self.nota
        d_str = str(n.get('data_programada') or '').strip()
        if d_str and d_str.lower() != 'none':
            self.input_data.setText(_normalizar_data(d_str, padrao_hoje=True))
            
        self.input_placa.setText(str(n.get('placa') or n.get('titulo') or ''))
        
        st = str(n.get('status') or n.get('prioridade') or 'PENDENTE')
        idx_s = self.combo_status.findText(st)
        if idx_s >= 0:
            self.combo_status.setCurrentIndex(idx_s)
            
        self.input_obs.setText(str(n.get('observacao') or n.get('conteudo') or ''))

    def obter_dados(self):
        return {
            'data_programada': _normalizar_data(self.input_data.text(), padrao_hoje=True),
            'placa': self.input_placa.text().strip().upper(),
            'status': self.combo_status.currentText().strip(),
            'observacao': self.input_obs.toPlainText().strip()
        }


class ImportarOpcoesDialog(MessageBoxBase):
    """Diálogo corporativo para escolher o modo de importação da planilha"""
    
    def __init__(self, parent=None, nome_arquivo=""):
        super().__init__(parent)
        _aplicar_estilo_modal(self)
        
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        icon_w = IconWidget(FIF.DOWNLOAD, self.widget)
        icon_w.setFixedSize(22, 22)
        self.titleLabel = SubtitleLabel("Importar Dados da Planilha", self.widget)
        header_row.addWidget(icon_w)
        header_row.addWidget(self.titleLabel)
        header_row.addStretch()
        self.viewLayout.addLayout(header_row)
        
        if nome_arquivo:
            self.viewLayout.addWidget(BodyLabel(f"Arquivo selecionado: {nome_arquivo}", self.widget))
            
        self.viewLayout.addWidget(BodyLabel("Escolha como deseja processar os registros:", self.widget))
        
        self.radio_atualizar = RadioButton("Adicionar novos e atualizar existentes (Recomendado)", self.widget)
        self.radio_novos = RadioButton("Apenas registros novos (Ignorar placas/registros já existentes)", self.widget)
        self.radio_substituir = RadioButton("Substituir tudo (Apaga os registros atuais antes de importar)", self.widget)
        
        self.radio_atualizar.setChecked(True)
        
        self.viewLayout.addWidget(self.radio_atualizar)
        self.viewLayout.addWidget(self.radio_novos)
        self.viewLayout.addWidget(self.radio_substituir)
        
        self.yesButton.setText("Iniciar Importação")
        self.cancelButton.setText("Cancelar")
        self.widget.setMinimumWidth(520)

    def obter_modo(self):
        if self.radio_novos.isChecked():
            return "novo"
        if self.radio_substituir.isChecked():
            return "substituir"
        return "atualizar"

