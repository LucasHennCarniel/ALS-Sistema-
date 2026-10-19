"""Regra: exclusão em lote de registros de manutenção"""
import logging


def excluir_multiplos(model, ids):
    """Exclui uma lista de IDs do banco de dados"""
    excluidos = 0
    for id_reg in ids:
        try:
            if model.deletar(id_reg):
                excluidos += 1
        except Exception as e:
            logging.error(f"Erro ao excluir ID {id_reg}: {e}")
    return excluidos > 0, f"{excluidos} registro(s) excluído(s)!"
