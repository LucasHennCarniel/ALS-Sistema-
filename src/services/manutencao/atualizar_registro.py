"""Regra: atualizar um registro de manutenção existente"""
import logging
from src.services.manutencao.mapear_dados_interface import mapear_dados_interface
from src.services.manutencao.recalcular_campos import recalcular_campos


def atualizar_registro(model, id_registro, dados_ui):
    """Atualiza registro inteiro usando id"""
    try:
        dados_db = mapear_dados_interface(dados_ui)
        dados_db = recalcular_campos(dados_db)

        sucesso = model.atualizar(id_registro, dados_db)
        if sucesso:
            return True, "Registro atualizado com sucesso!"
        return False, "Registro não encontrado."
    except Exception as e:
        logging.error(f"Erro atualizar registro: {e}")
        return False, f"Erro interno: {e}"
