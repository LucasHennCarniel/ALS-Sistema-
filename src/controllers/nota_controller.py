from src.models.nota_model import NotaModel
from src.services.nota.salvar_nota import salvar_nota
from src.services.nota.excluir_nota import excluir_nota


class NotaController:
    """
    Controlador de Notas: encaminha as ações da interface para os services de regra de negócio
    """

    def __init__(self, model=None):
        self.model = model or NotaModel()

    def obter_todas(self):
        return self.model.obter_todas()

    def obter_por_id(self, id_nota):
        return self.model.obter_por_id(id_nota)

    def obter_nota_por_id(self, id_nota):
        return self.model.obter_por_id(id_nota)

    def adicionar_nota(self, dados):
        return self.salvar_nota(dados, id_nota=None)

    def atualizar_nota(self, id_nota, dados):
        return self.salvar_nota(dados, id_nota=id_nota)

    def salvar_nota(self, dados, id_nota=None):
        return salvar_nota(self.model, dados, id_nota)

    def excluir_nota(self, id_nota):
        return excluir_nota(self.model, id_nota)
