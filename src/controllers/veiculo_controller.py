from src.models.veiculo_model import VeiculoModel
from src.services.veiculo.obter_veiculos_ativos_formatado import obter_veiculos_ativos_formatado
from src.services.veiculo.extrair_placa_da_selecao import extrair_placa_da_selecao
from src.services.veiculo.adicionar_veiculo import adicionar_veiculo
from src.services.veiculo.atualizar_veiculo import atualizar_veiculo
from src.services.veiculo.excluir_veiculo import excluir_veiculo
from src.services.veiculo.atualizar_km import atualizar_km


class VeiculoController:
    """
    Controlador de Veículos: encaminha as ações da interface para os services de regra de negócio
    """

    def __init__(self, model=None):
        self.model = model or VeiculoModel()

    def obter_todos(self):
        return self.model.obter_todos()

    def obter_veiculo_por_placa(self, placa):
        return self.model.obter_por_placa(placa)

    def obter_veiculos_ativos_formatado(self):
        return obter_veiculos_ativos_formatado(self.model)

    def extrair_placa_da_selecao(self, texto_selecao):
        return extrair_placa_da_selecao(texto_selecao)

    def adicionar_veiculo(self, tipo, placa, descricao='', km_inicial=0):
        return adicionar_veiculo(self.model, tipo, placa, descricao, km_inicial)

    def atualizar_veiculo(self, placa_antiga, tipo, nova_placa, descricao, ativo, ultima_km=None):
        return atualizar_veiculo(self.model, placa_antiga, tipo, nova_placa, descricao, ativo, ultima_km)

    def excluir_veiculo(self, placa):
        return excluir_veiculo(self.model, placa)

    def atualizar_km(self, placa, nova_km):
        return atualizar_km(self.model, placa, nova_km)

    def obter_estatisticas(self):
        return self.model.obter_estatisticas()
