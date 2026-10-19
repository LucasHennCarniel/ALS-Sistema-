"""Regra: validar e atualizar um destino existente"""
import logging


def atualizar_destino(model, id_destino, nome, ativo):
    """
    Valida e atualiza um destino
    Retorna: (bool_sucesso, str_mensagem)
    """
    nome = nome.strip().upper()
    if not nome:
        return False, "O nome do destino não pode ser vazio."

    try:
        sucesso = model.atualizar(id_destino, nome, ativo)
        if sucesso:
            return True, "Destino atualizado com sucesso!"
        return False, "Destino não encontrado."
    except Exception as e:
        logging.error(f"Erro no controller ao atualizar destino: {e}")
        return False, "Erro interno ao atualizar destino."
