from src.models.nota_model import NotaModel
import logging
from datetime import datetime

class NotaController:
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
        try:
            data_prog = dados.get('data_programada') or datetime.now().strftime("%d/%m/%Y")
            placa = dados.get('placa') or dados.get('titulo') or 'GERAL'
            status = dados.get('status') or dados.get('prioridade') or 'PENDENTE'
            obs = dados.get('observacao') or dados.get('conteudo') or ''

            dados_db = {
                'data_programada': data_prog,
                'placa': placa,
                'status': status,
                'observacao': obs,
                'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if not dados_db['data_programada'] or not dados_db['placa']:
                return False, "Data programada e placa/título são obrigatórios"
                
            if id_nota:
                sucesso = self.model.atualizar(id_nota, dados_db)
                if sucesso:
                    return True, "Nota atualizada com sucesso!"
                return False, "Nota não encontrada."
            else:
                id_novo = self.model.inserir(dados_db)
                if id_novo:
                    return True, "Nota criada com sucesso!"
                return False, "Erro ao criar nota."
        except Exception as e:
            logging.error(f"Erro salvar nota: {e}")
            return False, f"Erro interno: {e}"
            
    def excluir_nota(self, id_nota):
        try:
            sucesso = self.model.deletar(id_nota)
            if sucesso:
                return True, "Nota excluída com sucesso!"
            return False, "Nota não encontrada."
        except Exception as e:
            logging.error(f"Erro excluir nota: {e}")
            return False, f"Erro interno: {e}"
