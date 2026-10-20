import pandas as pd
import pytest

from src.services.dashboard.calcular_dias_corridos import calcular_dias_corridos
from src.services.dashboard.contar_por_status import contar_por_status
from src.services.dashboard.calcular_kpis_manutencao import calcular_kpis_manutencao
from src.services.dashboard.agrupar_por_faixa_aging import agrupar_por_faixa_aging
from src.services.dashboard.ranking_dias_parados import ranking_dias_parados

HOJE = '2026-10-19'


@pytest.fixture
def df():
    return pd.DataFrame([
        {'PLACA': 'AAA1111', 'STATUS': 'EM MANUTENÇÃO', 'DATA ENTRADA': '10/10/2026', 'DATA SAÍDA': '', 'DIAS': 0},
        {'PLACA': 'BBB2222', 'STATUS': 'EM SERVIÇO', 'DATA ENTRADA': '18/10/2026', 'DATA SAÍDA': '', 'DIAS': 0},
        {'PLACA': 'AAA1111', 'STATUS': 'FINALIZADO', 'DATA ENTRADA': '01/10/2026', 'DATA SAÍDA': '05/10/2026', 'DIAS': 4},
        # finalizado sem data de saída: mantém os dias gravados
        {'PLACA': 'CCC3333', 'STATUS': 'FINALIZADO', 'DATA ENTRADA': '01/09/2026', 'DATA SAÍDA': '', 'DIAS': 7},
        # sem data de entrada: mantém os dias gravados
        {'PLACA': 'DDD4444', 'STATUS': 'AGUARDANDO', 'DATA ENTRADA': '', 'DATA SAÍDA': '', 'DIAS': 0},
    ])


def test_dias_em_aberto_contam_ate_hoje(df):
    r = calcular_dias_corridos(df, hoje=HOJE)
    # o registro de 10/10 estava gravado com 0 dias, mas hoje (19/10) já são 9
    assert r.loc[0, 'DIAS_NUM'] == 9
    assert r.loc[1, 'DIAS_NUM'] == 1


def test_dias_finalizado_usa_data_de_saida_ou_valor_gravado(df):
    r = calcular_dias_corridos(df, hoje=HOJE)
    assert r.loc[2, 'DIAS_NUM'] == 4
    assert r.loc[3, 'DIAS_NUM'] == 7
    assert r.loc[4, 'DIAS_NUM'] == 0


def test_aberto_e_tudo_que_nao_e_finalizado(df):
    r = calcular_dias_corridos(df, hoje=HOJE)
    assert r['ABERTO'].tolist() == [True, True, False, False, True]


def test_nao_altera_o_dataframe_original(df):
    calcular_dias_corridos(df, hoje=HOJE)
    assert 'DIAS_NUM' not in df.columns


def test_contar_por_status_segue_ordem_do_fluxo(df):
    r = contar_por_status(df)
    assert r['Status'].tolist() == ['AGUARDANDO', 'EM SERVIÇO', 'EM MANUTENÇÃO', 'FINALIZADO']
    assert r['Quantidade'].tolist() == [1, 1, 1, 2]


def test_contar_por_status_vazio():
    assert contar_por_status(pd.DataFrame(columns=['STATUS'])).empty


def test_kpis(df):
    k = calcular_kpis_manutencao(calcular_dias_corridos(df, hoje=HOJE), frota_ativa=10, hoje=HOJE)
    assert k['parados'] == 3
    assert k['disponibilidade'] == pytest.approx(70.0)
    assert k['tempo_medio_reparo'] == pytest.approx(5.5)
    assert (k['mais_antigo_dias'], k['mais_antigo_placa']) == (9, 'AAA1111')
    assert k['reincidentes'] == 0


def test_kpis_reincidencia_considera_90_dias():
    dados = pd.DataFrame([
        {'PLACA': 'XXX0001', 'STATUS': 'FINALIZADO', 'DATA ENTRADA': d, 'DATA SAÍDA': d, 'DIAS': 1}
        for d in ['01/10/2026', '10/09/2026', '01/08/2026']
    ] + [
        {'PLACA': 'YYY0002', 'STATUS': 'FINALIZADO', 'DATA ENTRADA': d, 'DATA SAÍDA': d, 'DIAS': 1}
        for d in ['01/10/2026', '10/09/2026', '01/01/2026']  # a 3a entrada está fora da janela
    ])
    k = calcular_kpis_manutencao(calcular_dias_corridos(dados, hoje=HOJE), frota_ativa=5, hoje=HOJE)
    assert k['reincidentes'] == 1


def test_kpis_sem_frota_ou_sem_registros(df):
    k = calcular_kpis_manutencao(calcular_dias_corridos(df.iloc[0:0], hoje=HOJE), frota_ativa=0, hoje=HOJE)
    assert k['disponibilidade'] is None
    assert k['tempo_medio_reparo'] is None
    assert k['mais_antigo_dias'] is None
    assert k['parados'] == 0


def test_faixas_de_aging(df):
    r = agrupar_por_faixa_aging(calcular_dias_corridos(df, hoje=HOJE))
    assert r['Faixa'].tolist() == ['0–3 dias', '4–7 dias', '8–15 dias', '16+ dias']
    assert r['Quantidade'].tolist() == [2, 0, 1, 0]


def test_ranking_ordena_por_dias_parados(df):
    r = ranking_dias_parados(calcular_dias_corridos(df, hoje=HOJE), limite=2)
    assert r['PLACA'].tolist() == ['AAA1111', 'CCC3333']
    assert r['Dias_Parados'].tolist() == [13, 7]
    assert r.loc[0, 'Ocorrencias'] == 2
