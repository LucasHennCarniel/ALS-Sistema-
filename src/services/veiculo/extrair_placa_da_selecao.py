"""Regra: extrair a placa do texto selecionado no combobox"""


def extrair_placa_da_selecao(texto_selecao):
    """Extrai a placa do texto selecionado no combobox"""
    if ' - ' in texto_selecao:
        return texto_selecao.split(' - ')[0].strip()
    return texto_selecao.strip()
