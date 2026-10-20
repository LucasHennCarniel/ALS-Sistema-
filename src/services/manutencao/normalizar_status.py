"""Regra: converter qualquer texto de status para um dos status atuais"""
from src.services.manutencao.status import STATUS_LEGADOS


def normalizar_status(valor):
    """
    Maiúsculas e sem espaços sobrando. Status antigos viram o equivalente atual.
    Vazio continua vazio (o status é calculado pelas datas ao salvar) e texto desconhecido é mantido.
    """
    if valor is None:
        return ''
    texto = str(valor).strip().upper()
    if texto in ('NAN', 'NONE'):
        return ''
    return STATUS_LEGADOS.get(texto, texto)
