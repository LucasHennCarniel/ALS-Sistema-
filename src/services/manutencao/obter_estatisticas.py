"""Regra: indicadores do painel superior a partir do DataFrame de manutenções"""
from src.services.manutencao.status import (
    STATUS_AGENDADO, STATUS_EM_MANUTENCAO, STATUS_FINALIZADO, STATUS_SINISTRO
)


def obter_estatisticas(df):
    if df.empty:
        return {
            'total': 0, 'agendados': 0, 'em_manutencao': 0, 'sinistros': 0,
            'finalizados': 0, 'tempo_medio': 0, 'placas_unicas': 0
        }

    return {
        'total': len(df),
        'agendados': len(df[df['STATUS'] == STATUS_AGENDADO]),
        'em_manutencao': len(df[df['STATUS'] == STATUS_EM_MANUTENCAO]),
        'sinistros': len(df[df['STATUS'] == STATUS_SINISTRO]),
        'finalizados': len(df[df['STATUS'] == STATUS_FINALIZADO]),
        'tempo_medio': round(float(df['TOTAL DE DIAS EM MANUTENÇÃO'].mean()), 1) if 'TOTAL DE DIAS EM MANUTENÇÃO' in df.columns else 0,
        'placas_unicas': df['PLACA'].nunique() if 'PLACA' in df.columns else 0
    }
