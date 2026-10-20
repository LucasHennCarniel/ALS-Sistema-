"""Regra: dias parados recalculados na hora, no formato usado pelo dashboard"""
from src.services.manutencao.calcular_dias_dinamicos import calcular_dias_dinamicos


def calcular_dias_corridos(df, hoje=None):
    """
    Devolve uma cópia do DataFrame com as colunas auxiliares do dashboard:
    DATA_ENTRADA_DT, DATA_SAIDA_DT, ABERTO (bool) e DIAS_NUM (dias parados atualizados).
    A regra de cálculo é a mesma do sistema (calcular_dias_dinamicos).
    """
    out = calcular_dias_dinamicos(df, hoje)
    return out.rename(columns={'DIAS_CALCULADOS': 'DIAS_NUM'})
