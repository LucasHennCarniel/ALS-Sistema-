"""Regra: indicadores de manutenção usados no topo do dashboard"""
from datetime import datetime
import pandas as pd

JANELA_REINCIDENCIA_DIAS = 90
MIN_ENTRADAS_REINCIDENCIA = 3


def calcular_kpis_manutencao(df, frota_ativa, hoje=None):
    """
    df: DataFrame já passado por calcular_dias_corridos (colunas ABERTO, DIAS_NUM, DATA_ENTRADA_DT).
    frota_ativa: quantidade de veículos ativos cadastrados.
    """
    hoje = pd.Timestamp(hoje or datetime.now()).normalize()
    abertos = df[df['ABERTO']]
    finalizados = df[~df['ABERTO']]

    parados = int(abertos['PLACA'].replace('', pd.NA).dropna().nunique())
    disponibilidade = None
    if frota_ativa and frota_ativa > 0:
        disponibilidade = max(0.0, 1 - parados / frota_ativa) * 100

    tempo_medio_reparo = float(finalizados['DIAS_NUM'].mean()) if not finalizados.empty else None

    mais_antigo_dias, mais_antigo_placa = None, None
    if not abertos.empty:
        linha = abertos.loc[abertos['DIAS_NUM'].idxmax()]
        mais_antigo_dias, mais_antigo_placa = int(linha['DIAS_NUM']), linha['PLACA']

    recentes = df[df['DATA_ENTRADA_DT'] >= hoje - pd.Timedelta(days=JANELA_REINCIDENCIA_DIAS)]
    entradas = recentes[recentes['PLACA'] != ''].groupby('PLACA').size()
    reincidentes = int((entradas >= MIN_ENTRADAS_REINCIDENCIA).sum())

    return {
        'parados': parados,
        'disponibilidade': disponibilidade,
        'tempo_medio_reparo': tempo_medio_reparo,
        'mais_antigo_dias': mais_antigo_dias,
        'mais_antigo_placa': mais_antigo_placa,
        'reincidentes': reincidentes,
    }
