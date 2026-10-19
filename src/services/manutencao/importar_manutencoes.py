"""Regra: importação de planilha de manutenções (modos novo / atualizar / substituir)"""
from datetime import datetime
from src.services.manutencao.adicionar_registro import adicionar_registro
from src.services.manutencao.atualizar_registro import atualizar_registro


def _fmt_data(val):
    import pandas as pd
    if pd.isna(val) or val is None:
        return ''
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.strftime('%d/%m/%Y')
    s = str(val).strip()
    if not s or s.upper() in ('NAN', 'NAT', 'NONE'):
        return ''
    if ' ' in s and '-' in s:
        try:
            return pd.to_datetime(s).strftime('%d/%m/%Y')
        except Exception:
            pass
    return s


def importar_manutencoes(model, df, modo="atualizar"):
    """
    Processa DataFrame de planilha de manutenções via ORM SQLAlchemy.
    Modos: 'novo', 'atualizar', 'substituir'.
    Retorna: (total_novos, total_atualizados)
    """
    import pandas as pd
    if modo == "substituir":
        model.limpar_todos()

    novos = 0
    atualizados = 0

    for _, row in df.iterrows():
        placa = str(row.get('PLACA', '')).strip().upper()
        if not placa or placa in ('NAN', 'NONE'):
            continue

        data_str = _fmt_data(row.get('DATA'))
        data_entrada = _fmt_data(row.get('DATA ENTRADA'))
        data_saida = _fmt_data(row.get('DATA SAÍDA'))

        if not data_str and data_entrada:
            data_str = data_entrada
        elif not data_entrada and data_str:
            data_entrada = data_str

        if not data_str and not data_entrada:
            continue

        km_raw = row.get('KM', 0)
        try:
            km = float(km_raw) if pd.notna(km_raw) and str(km_raw).lower() != 'xxx' else 0.0
        except Exception:
            km = 0.0

        veiculo_txt = str(row.get('VEÍCULO', '')).strip().upper() if pd.notna(row.get('VEÍCULO')) else ''
        destino_txt = str(row.get('DESTINO PROGRAMADO', '')).strip().upper() if pd.notna(row.get('DESTINO PROGRAMADO')) else ''
        servico_txt = str(row.get('SERVIÇO A EXECUTAR', '')).strip() if pd.notna(row.get('SERVIÇO A EXECUTAR')) else ''
        status_txt = str(row.get('STATUS', '')).strip().upper() if pd.notna(row.get('STATUS')) else ''
        of_val = row.get('NR° OF') if 'NR° OF' in df.columns else row.get('NRº OF', '')
        of_txt = str(of_val).strip() if pd.notna(of_val) else ''
        obs_txt = str(row.get('OBS', '')).strip() if pd.notna(row.get('OBS')) else ''

        dados = {
            'data': data_str,
            'placa': placa,
            'km': km,
            'veiculo': veiculo_txt,
            'destino_programado': destino_txt,
            'servico_executar': servico_txt,
            'status': status_txt,
            'data_entrada': data_entrada,
            'data_saida': data_saida,
            'nr_of': of_txt,
            'obs': obs_txt
        }

        existente_id = model.obter_por_placa_e_datas(placa, data_str, data_entrada)
        if existente_id:
            if modo == "novo":
                continue
            elif modo == "atualizar":
                atualizar_registro(model, existente_id, dados)
                atualizados += 1
        else:
            adicionar_registro(model, dados)
            novos += 1

    return novos, atualizados
