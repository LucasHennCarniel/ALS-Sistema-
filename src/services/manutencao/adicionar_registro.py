"""Regra: criar um registro de manutenção a partir dos dados da interface"""
import logging
from src.services.manutencao.mapear_dados_interface import mapear_dados_interface
from src.services.manutencao.recalcular_campos import recalcular_campos


def adicionar_registro(model, dados_ui):
    """Recebe dados da interface, mapeia, calcula e insere no banco"""
    try:
        dados_db = mapear_dados_interface(dados_ui)
        dados_db = recalcular_campos(dados_db)

        id_novo = model.inserir(dados_db)
        if id_novo:
            return True, "Registro adicionado com sucesso!"
        return False, "Erro ao inserir no banco."
    except Exception as e:
        logging.error(f"Erro adicionar registro: {e}")
        return False, f"Erro interno: {e}"
