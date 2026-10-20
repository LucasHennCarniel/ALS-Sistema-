"""Regra: dias parados sempre atualizados (não dependem do valor gravado no banco)"""
from datetime import datetime
import pandas as pd

STATUS_FINALIZADO = 'FINALIZADO'


def calcular_dias_dinamicos(df, hoje=None):
    """
    Devolve uma cópia do DataFrame com as colunas auxiliares:
    DATA_ENTRADA_DT, DATA_SAIDA_DT, ABERTO (bool) e DIAS_CALCULADOS (int).

    - Em aberto (status diferente de FINALIZADO): da entrada até a saída, ou até hoje se ainda não saiu.
    - Finalizado com data de saída: da entrada até a saída.
    - Sem data de entrada, ou finalizado sem data de saída: mantém os dias gravados no banco.
    """
    hoje = pd.Timestamp(hoje or datetime.now()).normalize()
    out = df.copy()

    saida = out['DATA SAÍDA'] if 'DATA SAÍDA' in out.columns else pd.Series('', index=out.index)
    status = out['STATUS'] if 'STATUS' in out.columns else pd.Series('', index=out.index)
    coluna_gravada = 'TOTAL DE DIAS EM MANUTENÇÃO' if 'TOTAL DE DIAS EM MANUTENÇÃO' in out.columns else 'DIAS'
    gravados = pd.to_numeric(out[coluna_gravada], errors='coerce').fillna(0) if coluna_gravada in out.columns \
        else pd.Series(0, index=out.index)

    out['DATA_ENTRADA_DT'] = pd.to_datetime(out['DATA ENTRADA'], format='%d/%m/%Y', errors='coerce')
    out['DATA_SAIDA_DT'] = pd.to_datetime(saida, format='%d/%m/%Y', errors='coerce')
    out['ABERTO'] = status.fillna('').astype(str).str.strip().str.upper() != STATUS_FINALIZADO

    fim = out['DATA_SAIDA_DT'].where(out['DATA_SAIDA_DT'].notna(), hoje)
    calculados = (fim - out['DATA_ENTRADA_DT']).dt.days.clip(lower=0)

    usar_gravado = out['DATA_ENTRADA_DT'].isna() | (~out['ABERTO'] & out['DATA_SAIDA_DT'].isna())
    out['DIAS_CALCULADOS'] = calculados.where(~usar_gravado, gravados).fillna(0).astype(int)
    return out
