"""Regra: exclusão lógica (desativação) de destino"""
import logging


def excluir_destino(model, id_destino):
    """
    Desativa um destino logicamente
    Retorna: (bool_sucesso, str_mensagem)
    """
    try:
        sucesso = model.desativar(id_destino)
        if sucesso:
            return True, "Destino excluído com sucesso!"
        return False, "Destino não encontrado."
    except Exception as e:
        logging.error(f"Erro no controller ao excluir destino: {e}")
        return False, "Erro interno ao excluir destino."
