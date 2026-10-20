"""Regra: autocálculo de status e dias antes de salvar"""
from src.services.manutencao.calcular_dias_manutencao import calcular_dias_manutencao
from src.services.manutencao.status import STATUS_AGENDADO, STATUS_EM_MANUTENCAO, STATUS_FINALIZADO


def recalcular_campos(dados):
    """Aplica as regras de negócio de autocalculo de status e dias antes de salvar"""
    data_entrada = dados.get('data_entrada', '')
    data_saida = dados.get('data_saida', '')
    status = dados.get('status', '').strip().upper()

    if not status:
        if data_saida:
            status = STATUS_FINALIZADO
        elif data_entrada:
            status = STATUS_EM_MANUTENCAO
        else:
            status = STATUS_AGENDADO
    dados['status'] = status

    if data_entrada:
        dados['total_dias_manutencao'] = calcular_dias_manutencao(data_entrada, data_saida)
    else:
        dados['total_dias_manutencao'] = 0

    return dados
