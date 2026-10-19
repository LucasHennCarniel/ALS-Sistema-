"""Regra: autocálculo de status e dias antes de salvar"""
from src.services.manutencao.calcular_dias_manutencao import calcular_dias_manutencao


def recalcular_campos(dados):
    """Aplica as regras de negócio de autocalculo de status e dias antes de salvar"""
    data_entrada = dados.get('data_entrada', '')
    data_saida = dados.get('data_saida', '')
    status = dados.get('status', '').strip().upper()

    if not status:
        if data_saida:
            status = 'FINALIZADO'
        elif data_entrada:
            status = 'EM MANUTENÇÃO'
        else:
            status = 'AGUARDANDO'
    dados['status'] = status

    if data_entrada:
        dados['total_dias_manutencao'] = calcular_dias_manutencao(data_entrada, data_saida)
    else:
        dados['total_dias_manutencao'] = 0

    return dados
