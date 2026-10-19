"""Regra: exclusão de um registro de manutenção"""
import logging


def excluir_registro(model, id_registro):
    try:
        sucesso = model.deletar(id_registro)
        if sucesso:
            return True, "Registro excluído com sucesso!"
        return False, "Registro não encontrado."
    except Exception as e:
        logging.error(f"Erro excluir registro: {e}")
        return False, f"Erro interno: {e}"
