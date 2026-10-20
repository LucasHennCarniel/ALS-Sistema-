import os
import tempfile
from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.models.manutencao_model import ManutencaoModel
from src.controllers.manutencao_controller import ManutencaoController
from src.services.manutencao.calcular_dias_dinamicos import calcular_dias_dinamicos

HOJE = '2026-10-19'


def _linha(status, entrada, saida='', gravado=0):
    return {'STATUS': status, 'DATA ENTRADA': entrada, 'DATA SAÍDA': saida, 'TOTAL DE DIAS EM MANUTENÇÃO': gravado}


def test_aberto_conta_ate_hoje_ignorando_valor_gravado():
    df = pd.DataFrame([_linha('EM MANUTENÇÃO', '13/10/2026', gravado=0)])
    assert calcular_dias_dinamicos(df, hoje=HOJE)['DIAS_CALCULADOS'].tolist() == [6]


def test_dia_seguinte_soma_mais_um():
    df = pd.DataFrame([_linha('EM SERVIÇO', '13/10/2026')])
    assert calcular_dias_dinamicos(df, hoje='2026-10-20')['DIAS_CALCULADOS'].tolist() == [7]


def test_finalizado_com_saida_fixa_o_periodo():
    df = pd.DataFrame([_linha('FINALIZADO', '01/10/2026', '05/10/2026', gravado=99)])
    # nem o valor gravado nem o dia de hoje mudam o período fechado
    assert calcular_dias_dinamicos(df, hoje=HOJE)['DIAS_CALCULADOS'].tolist() == [4]
    assert calcular_dias_dinamicos(df, hoje='2027-01-01')['DIAS_CALCULADOS'].tolist() == [4]


def test_finalizado_sem_saida_ou_sem_entrada_mantem_gravado():
    df = pd.DataFrame([
        _linha('FINALIZADO', '01/09/2026', '', gravado=7),
        _linha('AGUARDANDO', '', '', gravado=3),
    ])
    assert calcular_dias_dinamicos(df, hoje=HOJE)['DIAS_CALCULADOS'].tolist() == [7, 3]


def test_entrada_no_futuro_nao_gera_dias_negativos():
    df = pd.DataFrame([_linha('EM SERVIÇO', '25/10/2026')])
    assert calcular_dias_dinamicos(df, hoje=HOJE)['DIAS_CALCULADOS'].tolist() == [0]


def test_aceita_valores_nulos():
    df = pd.DataFrame([{'STATUS': None, 'DATA ENTRADA': None, 'DATA SAÍDA': None, 'TOTAL DE DIAS EM MANUTENÇÃO': None}])
    assert calcular_dias_dinamicos(df, hoje=HOJE)['DIAS_CALCULADOS'].tolist() == [0]


@pytest.fixture
def controller():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield ManutencaoController(model=ManutencaoModel(db_path=path))
    try:
        os.remove(path)
    except OSError:
        pass


def test_dataframe_do_controller_ignora_valor_desatualizado_do_banco(controller):
    entrada = (datetime.now() - timedelta(days=10)).strftime('%d/%m/%Y')
    # registro gravado há dias com contador zerado (como acontecia antes da correção)
    controller.model.inserir({
        'data': entrada, 'placa': 'ABC1234', 'status': 'EM MANUTENÇÃO',
        'data_entrada': entrada, 'data_saida': '', 'total_dias_manutencao': 0,
    })
    df = controller.df
    assert df.loc[0, 'DIAS'] == 10
    assert df.loc[0, 'TOTAL DE DIAS EM MANUTENÇÃO'] == 10
    # o tempo médio dos cards usa o mesmo valor atualizado
    assert controller.obter_estatisticas()['tempo_medio'] == 10.0
