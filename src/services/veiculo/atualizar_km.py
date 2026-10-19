"""Regra: atualização da quilometragem de um veículo"""
import logging


def atualizar_km(model, placa, nova_km):
    try:
        nova_km = float(nova_km)
        return model.atualizar_km(placa, nova_km)
    except Exception as e:
        logging.error(f"Erro ao atualizar km: {e}")
        return False
