"""Regra: exclusão de veículo"""
import logging


def excluir_veiculo(model, placa):
    try:
        sucesso = model.deletar(placa)
        if sucesso:
            return True, "Veículo excluído com sucesso!"
        return False, "Veículo não encontrado."
    except Exception as e:
        logging.error(f"Erro ao excluir veiculo: {e}")
        return False, f"Erro ao excluir veículo: {e}"
