from src.models.manutencao_model import ManutencaoModel
import logging
from datetime import datetime

class ManutencaoController:
    """
    Controlador para gerenciar a lógica de negócio dos Registros de Manutenção
    """
    def __init__(self, model=None):
        self.model = model or ManutencaoModel()
        
    @property
    def df(self):
        """Retorna os dados em formato DataFrame para manter compatibilidade com as Views"""
        import pandas as pd
        dados = self.obter_todos()
        df = pd.DataFrame(dados)
        
        if not df.empty:
            df = df.rename(columns={
                'id': 'ID',
                'data': 'DATA',
                'placa': 'PLACA',
                'km': 'KM',
                'veiculo': 'VEÍCULO',
                'destino_programado': 'DESTINO PROGRAMADO',
                'servico_executar': 'SERVIÇO A EXECUTAR',
                'status': 'STATUS',
                'data_entrada': 'DATA ENTRADA',
                'data_saida': 'DATA SAÍDA',
                'total_dias_manutencao': 'TOTAL DE DIAS EM MANUTENÇÃO',
                'nr_of': 'NR° OF',
                'obs': 'OBS'
            })
            # Cria colunas alias para facilitar acesso na View Qt e Dashboard
            df['DIAS'] = df['TOTAL DE DIAS EM MANUTENÇÃO']
            df['NRº OF'] = df['NR° OF']
        return df
        
    def obter_todos(self):
        """Retorna todos os registros"""
        return self.model.obter_todos()

    def obter_por_id(self, id_registro):
        """Retorna um registro específico pelo ID"""
        return self.model.obter_por_id(id_registro)

    def obter_registro_por_id(self, id_registro):
        """Alias utilizado pela interface Qt para buscar registro por ID"""
        return self.model.obter_por_id(id_registro)
        
    def _mapear_dados_interface_para_banco(self, dados_ui):
        """Mapeia o dicionário bruto da interface (com espaços/acentos) para colunas do DB"""
        mapeamento = {
            'DATA': 'data',
            'PLACA': 'placa',
            'KM': 'km',
            'VEÍCULO': 'veiculo',
            'DESTINO PROGRAMADO': 'destino_programado',
            'SERVIÇO A EXECUTAR': 'servico_executar',
            'STATUS': 'status',
            'DATA ENTRADA': 'data_entrada',
            'DATA SAÍDA': 'data_saida',
            'TOTAL DE DIAS EM MANUTENÇÃO': 'total_dias_manutencao',
            'DIAS': 'total_dias_manutencao',
            'NR° OF': 'nr_of',
            'NRº OF': 'nr_of',
            'OBS': 'obs'
        }
        
        dados_db = {}
        for k, v in dados_ui.items():
            k_upper = k.upper().strip()
            if k_upper in mapeamento:
                dados_db[mapeamento[k_upper]] = v
            else:
                k_db = k.lower().replace(' ', '_').replace('°', '').replace('º', '').replace('ç', 'c').replace('í', 'i').replace('ã', 'a')
                dados_db[k_db] = v
                
        return dados_db
        
    def _calcular_dias_manutencao(self, data_entrada_str, data_saida_str):
        """Calcula a diferença de dias entre entrada e saída"""
        try:
            if not data_entrada_str:
                return 0
                
            fmt = "%d/%m/%Y"
            d_entrada = datetime.strptime(data_entrada_str, fmt)
            
            if data_saida_str:
                d_saida = datetime.strptime(data_saida_str, fmt)
            else:
                d_saida = datetime.now()
                
            dias = (d_saida - d_entrada).days
            return max(0, dias)
        except Exception as e:
            logging.error(f"Erro ao calcular dias: {e}")
            return 0
            
    def _recalcular_campos_logica(self, dados):
        """Aplica as regras de negócio de autocalculo de status e dias antes de salvar"""
        data_entrada = dados.get('data_entrada', '')
        data_saida = dados.get('data_saida', '')
        status = dados.get('status', '').strip().upper()
        
        if not status:
            if data_saida:
                status = 'FINALIZADO'
            elif data_entrada:
                status = 'EM MANUTENÇÃO'
            else:
                status = 'AGUARDANDO'
        dados['status'] = status
        
        if data_entrada:
            dados['total_dias_manutencao'] = self._calcular_dias_manutencao(data_entrada, data_saida)
        else:
            dados['total_dias_manutencao'] = 0
            
        return dados
        
    def adicionar_registro(self, dados_ui):
        """Recebe dados da interface, mapeia, calcula e insere no banco"""
        try:
            dados_db = self._mapear_dados_interface_para_banco(dados_ui)
            dados_db = self._recalcular_campos_logica(dados_db)
            
            id_novo = self.model.inserir(dados_db)
            if id_novo:
                return True, "Registro adicionado com sucesso!"
            return False, "Erro ao inserir no banco."
        except Exception as e:
            logging.error(f"Erro adicionar registro: {e}")
            return False, f"Erro interno: {e}"
            
    def atualizar_registro(self, id_registro, dados_ui):
        """Atualiza registro inteiro usando id"""
        try:
            dados_db = self._mapear_dados_interface_para_banco(dados_ui)
            dados_db = self._recalcular_campos_logica(dados_db)
            
            sucesso = self.model.atualizar(id_registro, dados_db)
            if sucesso:
                return True, "Registro atualizado com sucesso!"
            return False, "Registro não encontrado."
        except Exception as e:
            logging.error(f"Erro atualizar registro: {e}")
            return False, f"Erro interno: {e}"
            
    def excluir_registro(self, id_registro):
        try:
            sucesso = self.model.deletar(id_registro)
            if sucesso:
                return True, "Registro excluído com sucesso!"
            return False, "Registro não encontrado."
        except Exception as e:
            logging.error(f"Erro excluir registro: {e}")
            return False, f"Erro interno: {e}"

    def excluir_multiplos(self, ids):
        """Exclui uma lista de IDs do banco de dados"""
        excluidos = 0
        for id_reg in ids:
            try:
                if self.model.deletar(id_reg):
                    excluidos += 1
            except Exception as e:
                logging.error(f"Erro ao excluir ID {id_reg}: {e}")
        return excluidos > 0, f"{excluidos} registro(s) excluído(s)!"

    def obter_dataframe_exibicao(self):
        """Alias compatível com a interface"""
        return self.df
        
    def salvar_dados(self):
        """Na arquitetura SQLite WAL os dados já são persistidos automaticamente."""
        return True
        
    def obter_estatisticas(self):
        df = self.df
        if df.empty:
            return {
                'total': 0, 'em_manutencao': 0, 'finalizados': 0,
                'aguardando': 0, 'em_transito': 0, 'em_servico': 0,
                'tempo_medio': 0, 'placas_unicas': 0
            }
        
        em_manut = len(df[df['STATUS'] == 'EM MANUTENÇÃO'])
        em_serv = len(df[df['STATUS'] == 'EM SERVIÇO'])
        return {
            'total': len(df),
            'em_manutencao': em_manut,
            'finalizados': len(df[df['STATUS'] == 'FINALIZADO']),
            'aguardando': len(df[df['STATUS'] == 'AGUARDANDO']),
            'em_transito': len(df[df['STATUS'] == 'EM TRÂNSITO']),
            'em_servico': em_serv + em_manut,
            'tempo_medio': round(float(df['TOTAL DE DIAS EM MANUTENÇÃO'].mean()), 1) if 'TOTAL DE DIAS EM MANUTENÇÃO' in df.columns else 0,
            'placas_unicas': df['PLACA'].nunique() if 'PLACA' in df.columns else 0
        }

    def buscar_registros(self, filtros):
        df = self.df
        if df.empty:
            return df
            
        df_filtrado = df.copy()
        
        if filtros.get('data_inicio'):
            try:
                import pandas as pd
                df_filtrado['DATA_DT'] = pd.to_datetime(df_filtrado['DATA ENTRADA'], format='%d/%m/%Y')
                df_filtrado = df_filtrado[df_filtrado['DATA_DT'] >= pd.to_datetime(filtros['data_inicio'], format='%d/%m/%Y')]
            except Exception:
                pass
            
        if filtros.get('data_fim'):
            try:
                import pandas as pd
                if 'DATA_DT' not in df_filtrado.columns:
                    df_filtrado['DATA_DT'] = pd.to_datetime(df_filtrado['DATA ENTRADA'], format='%d/%m/%Y')
                df_filtrado = df_filtrado[df_filtrado['DATA_DT'] <= pd.to_datetime(filtros['data_fim'], format='%d/%m/%Y')]
            except Exception:
                pass
            
        if 'DATA_DT' in df_filtrado.columns:
            df_filtrado = df_filtrado.drop('DATA_DT', axis=1)
            
        if filtros.get('veiculo') and filtros['veiculo'] != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['PLACA'] == filtros['veiculo']]
            
        if filtros.get('destino') and filtros['destino'] != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['DESTINO PROGRAMADO'] == filtros['destino']]
            
        if filtros.get('status') and filtros['status'] != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['STATUS'] == filtros['status']]
            
        if filtros.get('placa') and filtros['placa'].strip():
            termo = filtros['placa'].upper().strip()
            df_filtrado = df_filtrado[df_filtrado['PLACA'].str.contains(termo, na=False)]
            
        return df_filtrado

    def importar_dataframe_manutencoes(self, df, modo="atualizar"):
        """
        Processa DataFrame de planilha de manutenções via ORM SQLAlchemy.
        Modos: 'novo', 'atualizar', 'substituir'.
        Retorna: (total_novos, total_atualizados)
        """
        import pandas as pd
        if modo == "substituir":
            self.model.limpar_todos()

        novos = 0
        atualizados = 0

        def _fmt_data(val):
            if pd.isna(val) or val is None:
                return ''
            if isinstance(val, (pd.Timestamp, datetime)):
                return val.strftime('%d/%m/%Y')
            s = str(val).strip()
            if not s or s.upper() in ('NAN', 'NAT', 'NONE'):
                return ''
            if ' ' in s and '-' in s:
                try:
                    return pd.to_datetime(s).strftime('%d/%m/%Y')
                except Exception:
                    pass
            return s

        for _, row in df.iterrows():
            placa = str(row.get('PLACA', '')).strip().upper()
            if not placa or placa in ('NAN', 'NONE'):
                continue

            data_str = _fmt_data(row.get('DATA'))
            data_entrada = _fmt_data(row.get('DATA ENTRADA'))
            data_saida = _fmt_data(row.get('DATA SAÍDA'))

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

            existente_id = self.model.obter_por_placa_e_datas(placa, data_str, data_entrada)
            if existente_id:
                if modo == "novo":
                    continue
                elif modo == "atualizar":
                    self.atualizar_registro(existente_id, dados)
                    atualizados += 1
            else:
                self.adicionar_registro(dados)
                novos += 1

        return novos, atualizados

