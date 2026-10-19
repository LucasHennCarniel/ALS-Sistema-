from src.models.manutencao_model import ManutencaoModel
from src.services.manutencao.adicionar_registro import adicionar_registro
from src.services.manutencao.atualizar_registro import atualizar_registro
from src.services.manutencao.excluir_registro import excluir_registro
from src.services.manutencao.excluir_multiplos import excluir_multiplos
from src.services.manutencao.obter_estatisticas import obter_estatisticas
from src.services.manutencao.buscar_registros import buscar_registros
from src.services.manutencao.importar_manutencoes import importar_manutencoes

class ManutencaoController:
    """
    Controlador de Manutenções: encaminha as ações da interface para os services de regra de negócio
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
        
    def adicionar_registro(self, dados_ui):
        return adicionar_registro(self.model, dados_ui)

    def atualizar_registro(self, id_registro, dados_ui):
        return atualizar_registro(self.model, id_registro, dados_ui)

    def excluir_registro(self, id_registro):
        return excluir_registro(self.model, id_registro)

    def excluir_multiplos(self, ids):
        return excluir_multiplos(self.model, ids)

    def obter_dataframe_exibicao(self):
        """Alias compatível com a interface"""
        return self.df

    def salvar_dados(self):
        """Na arquitetura SQLite WAL os dados já são persistidos automaticamente."""
        return True

    def obter_estatisticas(self):
        return obter_estatisticas(self.df)

    def buscar_registros(self, filtros):
        return buscar_registros(self.df, filtros)

    def importar_dataframe_manutencoes(self, df, modo="atualizar"):
        return importar_manutencoes(self.model, df, modo)
