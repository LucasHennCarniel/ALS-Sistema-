"""Regra: validar e cadastrar um novo destino"""
import logging


def adicionar_destino(model, nome):
    """
    Valida e adiciona um novo destino
    Retorna: (bool_sucesso, str_mensagem)
    """
    nome = nome.strip().upper()
    if not nome:
        return False, "O nome do destino não pode ser vazio."

    try:
        if model.obter_por_nome(nome):
            return False, "Destino já cadastrado!"

        model.inserir(nome)
        return True, "Destino cadastrado com sucesso!"
    except Exception as e:
        logging.error(f"Erro no controller ao adicionar destino: {e}")
        return False, "Erro interno ao cadastrar destino."
