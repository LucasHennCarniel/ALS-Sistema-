"""Regra: criar ou atualizar uma nota (aceita os campos antigos titulo/prioridade/conteudo)"""
import logging
from datetime import datetime


def salvar_nota(model, dados, id_nota=None):
    try:
        data_prog = dados.get('data_programada') or datetime.now().strftime("%d/%m/%Y")
        placa = dados.get('placa') or dados.get('titulo') or 'GERAL'
        status = dados.get('status') or dados.get('prioridade') or 'PENDENTE'
        obs = dados.get('observacao') or dados.get('conteudo') or ''

        dados_db = {
            'data_programada': data_prog,
            'placa': placa,
            'status': status,
            'observacao': obs,
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if not dados_db['data_programada'] or not dados_db['placa']:
            return False, "Data programada e placa/título são obrigatórios"

        if id_nota:
            sucesso = model.atualizar(id_nota, dados_db)
            if sucesso:
                return True, "Nota atualizada com sucesso!"
            return False, "Nota não encontrada."
        else:
            id_novo = model.inserir(dados_db)
            if id_novo:
                return True, "Nota criada com sucesso!"
            return False, "Erro ao criar nota."
    except Exception as e:
        logging.error(f"Erro salvar nota: {e}")
        return False, f"Erro interno: {e}"
