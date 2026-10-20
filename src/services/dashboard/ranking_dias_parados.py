"""Regra: placas que mais acumularam dias parados"""
import pandas as pd


def ranking_dias_parados(df, limite=10):
    """df: DataFrame passado por calcular_dias_corridos. Retorna (PLACA, Dias_Parados, Ocorrencias)"""
    com_placa = df[df['PLACA'] != '']
    if com_placa.empty:
        return pd.DataFrame(columns=['PLACA', 'Dias_Parados', 'Ocorrencias'])

    return (
        com_placa.groupby('PLACA')
        .agg(Dias_Parados=('DIAS_NUM', 'sum'), Ocorrencias=('PLACA', 'size'))
        .reset_index()
        .sort_values(by=['Dias_Parados', 'Ocorrencias'], ascending=False)
        .head(limite)
        .reset_index(drop=True)
    )
