"""Regra: traduzir as chaves da interface (espaços/acentos) para as colunas do banco"""

MAPEAMENTO_COLUNAS = {
    'DATA': 'data',
    'PLACA': 'placa',
    'KM': 'km',
    'VEÍCULO': 'veiculo',
    'DESTINO PROGRAMADO': 'destino_programado',
    'SERVIÇO A EXECUTAR': 'servico_executar',
    'STATUS': 'status',
    'DATA ENTRADA': 'data_entrada',
    'DATA SAÍDA': 'data_saida',
    'TOTAL DE DIAS EM MANUTENÇÃO': 'total_dias_manutencao',
    'DIAS': 'total_dias_manutencao',
    'NR° OF': 'nr_of',
    'NRº OF': 'nr_of',
    'OBS': 'obs'
}


def mapear_dados_interface(dados_ui):
    """Mapeia o dicionário bruto da interface (com espaços/acentos) para colunas do DB"""
    dados_db = {}
    for k, v in dados_ui.items():
        k_upper = k.upper().strip()
        if k_upper in MAPEAMENTO_COLUNAS:
            dados_db[MAPEAMENTO_COLUNAS[k_upper]] = v
        else:
            k_db = k.lower().replace(' ', '_').replace('°', '').replace('º', '').replace('ç', 'c').replace('í', 'i').replace('ã', 'a')
            dados_db[k_db] = v

    return dados_db
