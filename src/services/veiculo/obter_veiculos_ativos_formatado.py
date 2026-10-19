"""Regra: texto 'PLACA - TIPO - DESCRICAO' dos veículos ativos"""


def obter_veiculos_ativos_formatado(model):
    """Retorna lista formatada 'PLACA - TIPO - DESCRICAO' para comboboxes"""
    lista = []
    for v in model.obter_ativos():
        texto = f"{v['placa']} - {v['tipo_veiculo']}"
        if v['descricao']:
            texto += f" - {v['descricao']}"
        lista.append(texto)
    return lista
