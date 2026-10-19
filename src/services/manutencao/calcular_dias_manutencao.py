"""Regra: dias corridos entre entrada e saída (ou até hoje, se ainda sem saída)"""
import logging
from datetime import datetime


def calcular_dias_manutencao(data_entrada_str, data_saida_str):
    """Calcula a diferença de dias entre entrada e saída"""
    try:
        if not data_entrada_str:
            return 0

        fmt = "%d/%m/%Y"
        d_entrada = datetime.strptime(data_entrada_str, fmt)

        if data_saida_str:
            d_saida = datetime.strptime(data_saida_str, fmt)
        else:
            d_saida = datetime.now()

        dias = (d_saida - d_entrada).days
        return max(0, dias)
    except Exception as e:
        logging.error(f"Erro ao calcular dias: {e}")
        return 0
