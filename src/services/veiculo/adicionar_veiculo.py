"""Regra: validar e cadastrar um novo veículo"""
import logging


def adicionar_veiculo(model, tipo, placa, descricao='', km_inicial=0):
    placa = placa.upper().strip()
    tipo = tipo.upper().strip() if tipo else 'OUTRO'
    if not placa:
        return False, "A Placa é obrigatória!"

    try:
        if model.obter_por_placa(placa):
            return False, "Placa já cadastrada!"

        km_inicial = float(km_inicial) if km_inicial else 0
        model.inserir(tipo, placa, descricao, km_inicial)
        return True, "Veículo cadastrado com sucesso!"
    except Exception as e:
        logging.error(f"Erro ao cadastrar veiculo: {e}")
        return False, f"Erro ao cadastrar veículo: {e}"
