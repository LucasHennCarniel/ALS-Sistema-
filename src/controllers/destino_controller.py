from src.models.destino_model import DestinoModel
from src.services.destino.garantir_destinos_padrao import garantir_destinos_padrao
from src.services.destino.adicionar_destino import adicionar_destino
from src.services.destino.atualizar_destino import atualizar_destino
from src.services.destino.excluir_destino import excluir_destino
from src.services.destino.obter_destinos_ativos import obter_destinos_ativos


class DestinoController:
    """
    Controlador de Destinos: encaminha as ações da interface para os services de regra de negócio
    """

    def __init__(self, model=None):
        self.model = model or DestinoModel()
        self.garantir_destinos_padrao()

    def garantir_destinos_padrao(self):
        return garantir_destinos_padrao(self.model)

    def adicionar_destino(self, nome):
        return adicionar_destino(self.model, nome)

    def atualizar_destino(self, id_destino, nome, ativo):
        return atualizar_destino(self.model, id_destino, nome, ativo)

    def excluir_destino(self, id_destino):
        return excluir_destino(self.model, id_destino)

    def obter_destinos_ativos(self):
        return obter_destinos_ativos(self.model)

    def obter_todos(self):
        """Retorna a lista completa de destinos (dicionários com id, nome, ativo)"""
        return self.model.obter_todos()
