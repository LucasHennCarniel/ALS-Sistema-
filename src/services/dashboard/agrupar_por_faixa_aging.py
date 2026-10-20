"""Regra: fila de registros em aberto agrupada por tempo parado"""
import pandas as pd

FAIXAS = [
    ('0–3 dias', 0, 3),
    ('4–7 dias', 4, 7),
    ('8–15 dias', 8, 15),
    ('16+ dias', 16, None),
]


def agrupar_por_faixa_aging(df):
    """df: DataFrame passado por calcular_dias_corridos. Retorna as 4 faixas, mesmo vazias"""
    abertos = df[df['ABERTO']]
    linhas = []
    for nome, minimo, maximo in FAIXAS:
        dentro = abertos['DIAS_NUM'] >= minimo
        if maximo is not None:
            dentro &= abertos['DIAS_NUM'] <= maximo
        linhas.append({'Faixa': nome, 'Quantidade': int(dentro.sum())})
    return pd.DataFrame(linhas)
