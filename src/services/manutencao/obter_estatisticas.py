"""Regra: indicadores do painel superior a partir do DataFrame de manutenções"""


def obter_estatisticas(df):
    if df.empty:
        return {
            'total': 0, 'em_manutencao': 0, 'finalizados': 0,
            'aguardando': 0, 'em_transito': 0, 'em_servico': 0,
            'tempo_medio': 0, 'placas_unicas': 0
        }

    em_manut = len(df[df['STATUS'] == 'EM MANUTENÇÃO'])
    em_serv = len(df[df['STATUS'] == 'EM SERVIÇO'])
    return {
        'total': len(df),
        'em_manutencao': em_manut,
        'finalizados': len(df[df['STATUS'] == 'FINALIZADO']),
        'aguardando': len(df[df['STATUS'] == 'AGUARDANDO']),
        'em_transito': len(df[df['STATUS'] == 'EM TRÂNSITO']),
        'em_servico': em_serv + em_manut,
        'tempo_medio': round(float(df['TOTAL DE DIAS EM MANUTENÇÃO'].mean()), 1) if 'TOTAL DE DIAS EM MANUTENÇÃO' in df.columns else 0,
        'placas_unicas': df['PLACA'].nunique() if 'PLACA' in df.columns else 0
    }
