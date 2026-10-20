import os
import tempfile

import pandas as pd
import pytest

from src.models.manutencao_model import ManutencaoModel
from src.controllers.manutencao_controller import ManutencaoController
from src.services.manutencao.normalizar_status import normalizar_status
from src.services.manutencao.obter_estatisticas import obter_estatisticas
from src.services.manutencao.calcular_dias_dinamicos import calcular_dias_dinamicos
from src.services.manutencao.recalcular_campos import recalcular_campos
from src.services.manutencao.status import STATUS_VALIDOS


def test_status_validos_sao_os_quatro_do_negocio():
    assert STATUS_VALIDOS == ['AGENDADO', 'EM MANUTENÇÃO', 'FINALIZADO', 'SINISTRO']


@pytest.mark.parametrize('antigo, atual', [
    ('EM SERVIÇO', 'EM MANUTENÇÃO'),
    ('aguardando peças', 'EM MANUTENÇÃO'),
    ('EM TRÂNSITO', 'EM MANUTENÇÃO'),
    ('PREVENTIVA', 'EM MANUTENÇÃO'),
    ('CORRETIVA', 'EM MANUTENÇÃO'),
    ('SOCORRO', 'EM MANUTENÇÃO'),
    ('AGUARDANDO', 'AGENDADO'),
])
def test_status_antigos_viram_o_equivalente_atual(antigo, atual):
    assert normalizar_status(antigo) == atual


def test_status_atuais_e_desconhecidos_sao_preservados():
    assert normalizar_status('  sinistro ') == 'SINISTRO'
    assert normalizar_status('finalizado') == 'FINALIZADO'
    assert normalizar_status('OUTRO TEXTO') == 'OUTRO TEXTO'


def test_status_vazio_ou_nulo_continua_vazio():
    assert normalizar_status(None) == ''
    assert normalizar_status('') == ''
    assert normalizar_status(float('nan')) == ''


def test_status_padrao_pelas_datas():
    assert recalcular_campos({'data_entrada': '', 'data_saida': '', 'status': ''})['status'] == 'AGENDADO'
    assert recalcular_campos({'data_entrada': '01/01/2026', 'data_saida': '', 'status': ''})['status'] == 'EM MANUTENÇÃO'
    assert recalcular_campos({'data_entrada': '01/01/2026', 'data_saida': '03/01/2026', 'status': ''})['status'] == 'FINALIZADO'


def test_agendado_nao_deixa_o_veiculo_parado_mas_sinistro_sim():
    df = pd.DataFrame([
        {'STATUS': s, 'DATA ENTRADA': '10/10/2026', 'DATA SAÍDA': '', 'TOTAL DE DIAS EM MANUTENÇÃO': 0}
        for s in STATUS_VALIDOS
    ])
    r = calcular_dias_dinamicos(df, hoje='2026-10-19')
    assert dict(zip(r['STATUS'], r['ABERTO'])) == {
        'AGENDADO': False, 'EM MANUTENÇÃO': True, 'FINALIZADO': False, 'SINISTRO': True,
    }


def test_estatisticas_por_status():
    df = pd.DataFrame({
        'STATUS': ['AGENDADO', 'EM MANUTENÇÃO', 'EM MANUTENÇÃO', 'FINALIZADO', 'SINISTRO'],
        'PLACA': ['A', 'B', 'C', 'D', 'E'],
        'TOTAL DE DIAS EM MANUTENÇÃO': [0, 4, 6, 2, 8],
    })
    e = obter_estatisticas(df)
    assert (e['total'], e['agendados'], e['em_manutencao'], e['sinistros'], e['finalizados']) == (5, 1, 2, 1, 1)
    assert e['tempo_medio'] == 4.0
    assert e['placas_unicas'] == 5


@pytest.fixture
def controller():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield ManutencaoController(model=ManutencaoModel(db_path=path))
    try:
        os.remove(path)
    except OSError:
        pass


def test_dataframe_mostra_status_antigos_como_atuais_sem_alterar_o_banco(controller):
    controller.model.inserir({'data': '01/10/2026', 'placa': 'ABC1234', 'status': 'EM SERVIÇO',
                              'data_entrada': '01/10/2026', 'data_saida': '', 'total_dias_manutencao': 0})
    controller.model.inserir({'data': '02/10/2026', 'placa': 'DEF5678', 'status': 'AGUARDANDO',
                              'data_entrada': '', 'data_saida': '', 'total_dias_manutencao': 0})
    assert sorted(controller.df['STATUS']) == ['AGENDADO', 'EM MANUTENÇÃO']
    assert sorted(r['status'] for r in controller.obter_todos()) == ['AGUARDANDO', 'EM SERVIÇO']


def test_importacao_converte_status_antigos(controller):
    planilha = pd.DataFrame([
        {'DATA': '01/10/2026', 'PLACA': 'ABC1234', 'DATA ENTRADA': '01/10/2026', 'STATUS': 'socorro'},
        {'DATA': '02/10/2026', 'PLACA': 'DEF5678', 'DATA ENTRADA': '02/10/2026', 'STATUS': 'Sinistro'},
    ])
    controller.importar_dataframe_manutencoes(planilha, 'novo')
    assert sorted(r['status'] for r in controller.obter_todos()) == ['EM MANUTENÇÃO', 'SINISTRO']
