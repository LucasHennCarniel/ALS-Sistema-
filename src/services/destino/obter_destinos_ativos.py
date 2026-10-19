"""Regra: lista simplificada de nomes de destinos ativos"""


def obter_destinos_ativos(model):
    """
    Retorna lista simplificada apenas com os nomes dos destinos ativos
    Usado para preencher Comboboxes na interface
    """
    return [d['nome_destino'] for d in model.obter_ativos()]
