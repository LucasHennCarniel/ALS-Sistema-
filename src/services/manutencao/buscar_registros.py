"""Regra: filtros de busca sobre o DataFrame de manutenções"""


def buscar_registros(df, filtros):
    if df.empty:
        return df

    df_filtrado = df.copy()

    if filtros.get('data_inicio'):
        try:
            import pandas as pd
            df_filtrado['DATA_DT'] = pd.to_datetime(df_filtrado['DATA ENTRADA'], format='%d/%m/%Y')
            df_filtrado = df_filtrado[df_filtrado['DATA_DT'] >= pd.to_datetime(filtros['data_inicio'], format='%d/%m/%Y')]
        except Exception:
            pass

    if filtros.get('data_fim'):
        try:
            import pandas as pd
            if 'DATA_DT' not in df_filtrado.columns:
                df_filtrado['DATA_DT'] = pd.to_datetime(df_filtrado['DATA ENTRADA'], format='%d/%m/%Y')
            df_filtrado = df_filtrado[df_filtrado['DATA_DT'] <= pd.to_datetime(filtros['data_fim'], format='%d/%m/%Y')]
        except Exception:
            pass

    if 'DATA_DT' in df_filtrado.columns:
        df_filtrado = df_filtrado.drop('DATA_DT', axis=1)

    if filtros.get('veiculo') and filtros['veiculo'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['PLACA'] == filtros['veiculo']]

    if filtros.get('destino') and filtros['destino'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['DESTINO PROGRAMADO'] == filtros['destino']]

    if filtros.get('status') and filtros['status'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['STATUS'] == filtros['status']]

    if filtros.get('placa') and filtros['placa'].strip():
        termo = filtros['placa'].upper().strip()
        df_filtrado = df_filtrado[df_filtrado['PLACA'].str.contains(termo, na=False)]

    return df_filtrado
