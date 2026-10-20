"""Regra: dias parados recalculados na hora (entrada -> saída, ou até hoje se ainda em aberto)"""
from datetime import datetime
import pandas as pd

STATUS_FINALIZADO = 'FINALIZADO'


def calcular_dias_corridos(df, hoje=None):
    """
    Devolve uma cópia do DataFrame com as colunas auxiliares:
    DATA_ENTRADA_DT, DATA_SAIDA_DT, ABERTO (bool) e DIAS_NUM (dias parados atualizados).
    Registro finalizado sem data de saída mantém os dias gravados no banco.
    """
    hoje = pd.Timestamp(hoje or datetime.now()).normalize()
    out = df.copy()

    out['DATA_ENTRADA_DT'] = pd.to_datetime(out['DATA ENTRADA'], format='%d/%m/%Y', errors='coerce')
    out['DATA_SAIDA_DT'] = pd.to_datetime(out['DATA SAÍDA'], format='%d/%m/%Y', errors='coerce')
    out['ABERTO'] = out['STATUS'].str.strip().str.upper() != STATUS_FINALIZADO

    gravados = pd.to_numeric(out.get('DIAS', 0), errors='coerce').fillna(0)
    fim = out['DATA_SAIDA_DT'].where(out['DATA_SAIDA_DT'].notna(), hoje)
    calculados = (fim - out['DATA_ENTRADA_DT']).dt.days.clip(lower=0)

    usar_gravado = out['DATA_ENTRADA_DT'].isna() | (~out['ABERTO'] & out['DATA_SAIDA_DT'].isna())
    out['DIAS_NUM'] = calculados.where(~usar_gravado, gravados).fillna(0).astype(int)
    return out
