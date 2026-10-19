"""Regra: validar e atualizar um veículo (inclusive troca de placa)"""
import logging


def atualizar_veiculo(model, placa_antiga, tipo, nova_placa, descricao, ativo, ultima_km=None):
    nova_placa = nova_placa.upper().strip()
    placa_antiga = placa_antiga.upper().strip()
    tipo = tipo.upper().strip() if tipo else 'OUTRO'

    if not nova_placa:
        return False, "A Placa é obrigatória!"

    try:
        if nova_placa != placa_antiga and model.obter_por_placa(nova_placa):
            return False, "A nova placa já está cadastrada em outro veículo!"

        model.atualizar(placa_antiga, tipo, nova_placa, descricao, ativo, ultima_km=ultima_km)
        return True, "Veículo atualizado com sucesso!"
    except Exception as e:
        logging.error(f"Erro ao atualizar veiculo: {e}")
        return False, f"Erro ao atualizar veículo: {e}"
