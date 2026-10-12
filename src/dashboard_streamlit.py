"""
Dashboard Analítico Interativo - Sistema de Gestão de Manutenção ALS
Desenvolvido com Streamlit + Plotly consumindo os Controllers MVC e SQLite WAL
"""
import os
import sys
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Garante que o diretório raiz está no sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.controllers.manutencao_controller import ManutencaoController
from src.controllers.veiculo_controller import VeiculoController
from src.controllers.destino_controller import DestinoController
from src.controllers.nota_controller import NotaController

# Configuração da página Streamlit
st.set_page_config(
    page_title="Dashboard ALS - Gestão de Frota",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS customizado com a paleta Cinza Suave e cores da ALS
st.markdown("""
<style>
    .stApp {
        background-color: #D5DFE8;
        color: #1E293B;
    }
    section[data-testid="stSidebar"] {
        background-color: #C6D0DA;
        border-right: 1px solid #94A3B8;
    }
    div[data-testid="stMetric"] {
        background-color: #EAEFF5;
        border: 1px solid #94A3B8;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 800 !important;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


def carregar_dados():
    """Carrega dados atualizados diretamente dos Controllers MVC"""
    manut_ctrl = ManutencaoController()
    veic_ctrl = VeiculoController()
    dest_ctrl = DestinoController()
    nota_ctrl = NotaController()

    df_manut = manut_ctrl.obter_dataframe_exibicao()
    veiculos = veic_ctrl.obter_todos() or []
    destinos = dest_ctrl.obter_todos() or []
    notas = nota_ctrl.obter_todas() or []

    return df_manut, veiculos, destinos, notas


def main():
    df, veiculos, destinos, notas = carregar_dados()

    # Cabeçalho Principal
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.title("📊 Dashboard Analítico de Manutenção - ALS")
        st.caption("Indicadores em tempo real integrados ao banco SQLite (Modo WAL)")
    with col_t2:
        if st.button("🔄 Recarregar Dados", use_container_width=True):
            st.rerun()

    # Verifica se há registros de manutenção
    if df is None or df.empty:
        st.info("ℹ️ Nenhum registro de manutenção cadastrado no momento. Abaixo estão os indicadores da frota cadastrada.")
        col1, col2, col3 = st.columns(3)
        total_v = len(veiculos)
        ativos_v = sum(1 for v in veiculos if v.get('ativo', 1))
        col1.metric("🚛 Total de Veículos Cadastrados", total_v)
        col2.metric("✅ Veículos Ativos", ativos_v)
        col3.metric("📝 Notas Internas", len(notas))

        if veiculos:
            df_v = pd.DataFrame(veiculos)
            st.subheader("Frota Cadastrada por Tipo / Marca")
            contagem_tipo = df_v['tipo_veiculo'].value_counts().reset_index()
            contagem_tipo.columns = ['Tipo de Veículo', 'Quantidade']
            fig_v = px.bar(
                contagem_tipo,
                x='Tipo de Veículo',
                y='Quantidade',
                text='Quantidade',
                color='Tipo de Veículo',
                color_discrete_sequence=['#4CAF50', '#607D8B', '#789DAB', '#90E74A', '#2E7D32']
            )
            fig_v.update_layout(
                paper_bgcolor='#EAEFF5',
                plot_bgcolor='#EAEFF5',
                font_color='#1E293B',
                showlegend=False
            )
            st.plotly_chart(fig_v, use_container_width=True)
        return

    # Padroniza colunas para evitar erros de tipo
    for col in ['PLACA', 'VEÍCULO', 'STATUS', 'DESTINO PROGRAMADO', 'SERVIÇO A EXECUTAR', 'NRº OF', 'OBS']:
        if col not in df.columns:
            df[col] = ''
        df[col] = df[col].fillna('').astype(str)

    if 'DIAS' not in df.columns:
        df['DIAS'] = 0
    df['DIAS_NUM'] = pd.to_numeric(df['DIAS'], errors='coerce').fillna(0)

    if 'KM' not in df.columns:
        df['KM'] = 0
    df['KM_NUM'] = pd.to_numeric(df['KM'], errors='coerce').fillna(0)

    # Converte DATA ENTRADA para datetime para filtro de período
    df['DATA_ENTRADA_DT'] = pd.to_datetime(df['DATA ENTRADA'], format='%d/%m/%Y', dayfirst=True, errors='coerce')

    # =========================================================================
    # BARRA LATERAL DE FILTROS (Todos os filtros do sistema)
    # =========================================================================
    st.sidebar.header("🔍 Filtros do Sistema")

    busca_texto = st.sidebar.text_input(
        "Busca Rápida (Placa, Serviço, OF, Obs)",
        placeholder="Digite para filtrar..."
    )

    opcoes_status = sorted([s for s in df['STATUS'].unique() if s.strip()])
    filtro_status = st.sidebar.multiselect(
        "Status da Manutenção",
        options=opcoes_status,
        default=[]
    )

    opcoes_placas = sorted([p for p in df['PLACA'].unique() if p.strip()])
    filtro_placas = st.sidebar.multiselect(
        "Placa(s)",
        options=opcoes_placas,
        default=[]
    )

    opcoes_veiculos = sorted([v for v in df['VEÍCULO'].unique() if v.strip()])
    filtro_veiculos = st.sidebar.multiselect(
        "Tipo de Veículo",
        options=opcoes_veiculos,
        default=[]
    )

    opcoes_destinos = sorted([d for d in df['DESTINO PROGRAMADO'].unique() if d.strip()])
    filtro_destinos = st.sidebar.multiselect(
        "Destino Programado",
        options=opcoes_destinos,
        default=[]
    )

    # Filtro de intervalo de datas (se houver datas válidas)
    datas_validas = df['DATA_ENTRADA_DT'].dropna()
    usar_filtro_data = st.sidebar.checkbox("Filtrar por Período de Entrada", value=False)
    data_ini, data_fim = None, None
    if usar_filtro_data and not datas_validas.empty:
        min_date = datas_validas.min().date()
        max_date = datas_validas.max().date()
        intervalo = st.sidebar.date_input(
            "Período (Data de Entrada)",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if isinstance(intervalo, tuple) and len(intervalo) == 2:
            data_ini, data_fim = intervalo

    if st.sidebar.button("🧹 Limpar Todos os Filtros", use_container_width=True):
        st.rerun()

    # Aplicação dos filtros no DataFrame
    df_f = df.copy()

    if busca_texto.strip():
        t = busca_texto.strip().lower()
        mascara = (
            df_f['PLACA'].str.lower().str.contains(t, na=False) |
            df_f['VEÍCULO'].str.lower().str.contains(t, na=False) |
            df_f['SERVIÇO A EXECUTAR'].str.lower().str.contains(t, na=False) |
            df_f['DESTINO PROGRAMADO'].str.lower().str.contains(t, na=False) |
            df_f['NRº OF'].str.lower().str.contains(t, na=False) |
            df_f['OBS'].str.lower().str.contains(t, na=False)
        )
        df_f = df_f[mascara]

    if filtro_status:
        df_f = df_f[df_f['STATUS'].isin(filtro_status)]

    if filtro_placas:
        df_f = df_f[df_f['PLACA'].isin(filtro_placas)]

    if filtro_veiculos:
        df_f = df_f[df_f['VEÍCULO'].isin(filtro_veiculos)]

    if filtro_destinos:
        df_f = df_f[df_f['DESTINO PROGRAMADO'].isin(filtro_destinos)]

    if usar_filtro_data and data_ini and data_fim:
        df_f = df_f[
            (df_f['DATA_ENTRADA_DT'].dt.date >= data_ini) &
            (df_f['DATA_ENTRADA_DT'].dt.date <= data_fim)
        ]

    # =========================================================================
    # KPIs PRINCIPAIS
    # =========================================================================
    total_reg = len(df_f)
    em_servico = len(df_f[df_f['STATUS'].str.upper().str.contains('MANUTENÇÃO|SERVIÇO|AGUARDANDO', na=False)])
    finalizados = len(df_f[df_f['STATUS'].str.upper().str.contains('FINALIZADO', na=False)])
    tempo_medio = df_f['DIAS_NUM'].mean() if total_reg > 0 else 0.0
    placas_atendidas = df_f['PLACA'].replace('', pd.NA).dropna().nunique()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📊 Total Filtrado", f"{total_reg}")
    k2.metric("⚙️ Em Serviço / Aberto", f"{em_servico}")
    k3.metric("✅ Finalizados", f"{finalizados}")
    k4.metric("⏱️ Tempo Médio", f"{tempo_medio:.1f} dias")
    k5.metric("🚛 Placas Únicas", f"{placas_atendidas} / {len(veiculos)}")

    st.markdown("---")

    # =========================================================================
    # GRÁFICOS INTERATIVOS (Linha 1)
    # =========================================================================
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📌 Manutenções por Status")
        df_status = df_f['STATUS'].replace('', 'NÃO INFORMADO').value_counts().reset_index()
        df_status.columns = ['Status', 'Quantidade']
        fig_status = px.pie(
            df_status,
            names='Status',
            values='Quantidade',
            hole=0.45,
            color_discrete_sequence=['#4CAF50', '#607D8B', '#FFA726', '#EF5350', '#789DAB']
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        fig_status.update_layout(
            paper_bgcolor='#EAEFF5',
            plot_bgcolor='#EAEFF5',
            font_color='#1E293B',
            margin=dict(t=20, b=20, l=20, r=20),
            height=340
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with g2:
        st.subheader("🚛 Top 10 Placas com Mais Ocorrências")
        df_top_placas = (
            df_f[df_f['PLACA'] != '']
            .groupby('PLACA')
            .agg(Ocorrencias=('ID', 'count'), Dias_Parados=('DIAS_NUM', 'sum'))
            .reset_index()
            .sort_values(by='Ocorrencias', ascending=True)
            .tail(10)
        )
        fig_placas = px.bar(
            df_top_placas,
            x='Ocorrencias',
            y='PLACA',
            orientation='h',
            text='Ocorrencias',
            hover_data=['Dias_Parados'],
            color='Dias_Parados',
            color_continuous_scale=['#789DAB', '#4CAF50']
        )
        fig_placas.update_layout(
            paper_bgcolor='#EAEFF5',
            plot_bgcolor='#EAEFF5',
            font_color='#1E293B',
            margin=dict(t=20, b=20, l=20, r=20),
            height=340
        )
        st.plotly_chart(fig_placas, use_container_width=True)

    # =========================================================================
    # GRÁFICOS INTERATIVOS (Linha 2)
    # =========================================================================
    g3, g4 = st.columns(2)

    with g3:
        st.subheader("🛠️ Manutenções por Tipo de Veículo")
        df_veic = df_f['VEÍCULO'].replace('', 'NÃO ESPECIFICADO').value_counts().head(10).reset_index()
        df_veic.columns = ['Veículo', 'Quantidade']
        fig_veic = px.bar(
            df_veic,
            x='Veículo',
            y='Quantidade',
            text='Quantidade',
            color='Veículo',
            color_discrete_sequence=['#607D8B', '#4CAF50', '#789DAB', '#90E74A', '#455A64']
        )
        fig_veic.update_layout(
            paper_bgcolor='#EAEFF5',
            plot_bgcolor='#EAEFF5',
            font_color='#1E293B',
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=340
        )
        st.plotly_chart(fig_veic, use_container_width=True)

    with g4:
        st.subheader("📅 Evolução de Entradas por Mês")
        df_datas = df_f.dropna(subset=['DATA_ENTRADA_DT']).copy()
        if not df_datas.empty:
            df_datas['MES_ANO'] = df_datas['DATA_ENTRADA_DT'].dt.to_period('M').astype(str)
            df_mes = df_datas.groupby('MES_ANO').size().reset_index(name='Registros')
            fig_mes = px.area(
                df_mes,
                x='MES_ANO',
                y='Registros',
                markers=True,
                color_discrete_sequence=['#4CAF50']
            )
            fig_mes.update_layout(
                paper_bgcolor='#EAEFF5',
                plot_bgcolor='#EAEFF5',
                font_color='#1E293B',
                margin=dict(t=20, b=20, l=20, r=20),
                height=340
            )
            st.plotly_chart(fig_mes, use_container_width=True)
        else:
            st.info("Sem datas de entrada válidas para exibir a linha do tempo.")

    # =========================================================================
    # TABELA DE DADOS FILTRADOS
    # =========================================================================
    st.subheader("📋 Dados Detalhados (Conforme Filtros)")
    colunas_exibir = [
        c for c in [
            "ID", "DATA", "PLACA", "KM", "VEÍCULO", "DESTINO PROGRAMADO",
            "SERVIÇO A EXECUTAR", "STATUS", "DATA ENTRADA", "DATA SAÍDA", "DIAS", "NRº OF", "OBS"
        ] if c in df_f.columns
    ]
    st.dataframe(df_f[colunas_exibir], use_container_width=True, height=320)


if __name__ == "__main__":
    main()
