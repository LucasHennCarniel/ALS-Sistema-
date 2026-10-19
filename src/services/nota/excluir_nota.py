"""Regra: exclusão de nota"""
import logging


def excluir_nota(model, id_nota):
    try:
        sucesso = model.deletar(id_nota)
        if sucesso:
            return True, "Nota excluída com sucesso!"
        return False, "Nota não encontrada."
    except Exception as e:
        logging.error(f"Erro excluir nota: {e}")
        return False, f"Erro interno: {e}"
