"""Regra: contagem de registros por status, na ordem do fluxo operacional"""
import pandas as pd

ORDEM_STATUS = ['AGUARDANDO', 'EM TRÂNSITO', 'EM SERVIÇO', 'EM MANUTENÇÃO', 'FINALIZADO']


def contar_por_status(df):
    """Retorna DataFrame (Status, Quantidade) com os status conhecidos primeiro, na ordem do fluxo"""
    if df.empty:
        return pd.DataFrame(columns=['Status', 'Quantidade'])

    contagem = df['STATUS'].replace('', 'NÃO INFORMADO').value_counts()
    conhecidos = [s for s in ORDEM_STATUS if s in contagem.index]
    outros = sorted(s for s in contagem.index if s not in ORDEM_STATUS)
    ordem = conhecidos + outros
    return pd.DataFrame({'Status': ordem, 'Quantidade': [int(contagem[s]) for s in ordem]})
