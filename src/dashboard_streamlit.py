"""
Dashboard Analítico Corporativo - Sistema de Gestão de Manutenção ALS
Desenvolvido com Streamlit + Plotly consumindo os Controllers MVC e SQLite WAL
Visual Executivo com Ícones Vetoriais Material Design (Zero Emojis)
"""
import os
import sys
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px

# Garante que o diretório raiz está no sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.controllers.manutencao_controller import ManutencaoController
from src.controllers.veiculo_controller import VeiculoController
from src.controllers.destino_controller import DestinoController
from src.controllers.nota_controller import NotaController

# Configuração da página Streamlit (Sem emojis informais)
st.set_page_config(
    page_title="Dashboard Analítico ALS",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta Oficial ALS
PALETA_ALS = ['#4CAF50', '#607D8B', '#789DAB', '#90E74A', '#2E7D32', '#455A64', '#0284C7', '#26A69A']

# Estilo CSS Corporativo (Estilo Power BI com barra de acento lateral e cinza suave)
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
        border-left: 4px solid #4CAF50;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 0.78rem !important;
        letter-spacing: 0.04em;
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 800 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #EAEFF5;
        border: 1px solid #94A3B8 !important;
        border-radius: 8px !important;
        padding: 10px;
    }
    .block-container {
        padding-top: 1.2rem;
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


def estilizar_grafico_pizza(fig, furo=0.0):
    """Aplica borda nítida nas fatias da pizza/rosca e fundo cinza suave"""
    fig.update_traces(
        hole=furo,
        textposition='inside',
        textinfo='percent+label',
        marker=dict(
            line=dict(color='#1E293B', width=2)
        ),
        pull=[0.03] * 15
    )
    fig.update_layout(
        paper_bgcolor='#EAEFF5',
        plot_bgcolor='#EAEFF5',
        font=dict(family="Segoe UI, sans-serif", size=13, color='#0F172A'),
        margin=dict(t=20, b=20, l=20, r=20),
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig


def estilizar_grafico_colunas(fig):
    """Aplica borda nas colunas/barras e rótulos de valor no topo"""
    fig.update_traces(
        marker_line_color='#1E293B',
        marker_line_width=1.5,
        textposition='outside',
        cliponaxis=False
    )
    fig.update_layout(
        paper_bgcolor='#EAEFF5',
        plot_bgcolor='#EAEFF5',
        font=dict(family="Segoe UI, sans-serif", size=13, color='#0F172A'),
        margin=dict(t=35, b=20, l=20, r=20),
        height=360,
        xaxis=dict(showgrid=False, linecolor='#94A3B8'),
        yaxis=dict(gridcolor='#CBD5E1', zerolinecolor='#94A3B8')
    )
    return fig


def renderizar_aba_frota(veiculos, notas):
    """Renderiza os gráficos de Pizza com borda e Colunas da Frota Cadastrada"""
    if not veiculos:
        st.warning("Nenhum veículo cadastrado no banco de dados.")
        return

    df_v = pd.DataFrame(veiculos)
    for col in ['placa', 'tipo_veiculo', 'descricao']:
        if col not in df_v.columns:
            df_v[col] = ''
        df_v[col] = df_v[col].fillna('').astype(str)

    df_v['ultima_km_num'] = pd.to_numeric(df_v.get('ultima_km', 0), errors='coerce').fillna(0)
    df_v['STATUS_TXT'] = df_v.get('ativo', 1).apply(lambda x: 'ATIVO' if x else 'INATIVO')

    # Filtros na barra lateral para a Frota (Com ícone vetorial Material)
    st.sidebar.subheader(":material/filter_alt: Filtros da Frota")
    busca_v = st.sidebar.text_input("Buscar Placa ou Descrição", key="busca_frota")
    tipos_disp = sorted([t for t in df_v['tipo_veiculo'].unique() if t.strip()])
    filtro_tipo_v = st.sidebar.multiselect("Tipo / Marca do Veículo", options=tipos_disp, default=[], key="tipo_frota")
    filtro_status_v = st.sidebar.multiselect("Status Operacional", options=['ATIVO', 'INATIVO'], default=[], key="status_frota")

    df_vf = df_v.copy()
    if busca_v.strip():
        termo = busca_v.strip().lower()
        df_vf = df_vf[
            df_vf['placa'].str.lower().str.contains(termo, na=False) |
            df_vf['descricao'].str.lower().str.contains(termo, na=False) |
            df_vf['tipo_veiculo'].str.lower().str.contains(termo, na=False)
        ]
    if filtro_tipo_v:
        df_vf = df_vf[df_vf['tipo_veiculo'].isin(filtro_tipo_v)]
    if filtro_status_v:
        df_vf = df_vf[df_vf['STATUS_TXT'].isin(filtro_status_v)]

    # KPIs Corporativos da Frota
    total_v = len(df_vf)
    ativos_v = len(df_vf[df_vf['STATUS_TXT'] == 'ATIVO'])
    inativos_v = total_v - ativos_v
    tipos_unicos = df_vf['tipo_veiculo'].nunique()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de Veículos", f"{total_v}")
    k2.metric("Veículos Ativos", f"{ativos_v}")
    k3.metric("Veículos Inativos", f"{inativos_v}")
    k4.metric("Categorias / Marcas", f"{tipos_unicos}")

    st.markdown("")

    # Linha de Gráficos: Esquerda = Pizza com Borda | Direita = Colunas com Borda
    col_esq, col_dir = st.columns(2)

    contagem_tipo = df_vf['tipo_veiculo'].replace('', 'OUTROS').value_counts().reset_index()
    contagem_tipo.columns = ['Tipo de Veículo', 'Quantidade']

    with col_esq:
        with st.container(border=True):
            c_head1, c_head2 = st.columns([2, 1])
            c_head1.subheader(":material/pie_chart: Proporção por Categoria")
            estilo_g1 = c_head2.selectbox(
                "Estilo",
                ["Pizza com Borda", "Rosca com Borda", "Colunas"],
                key="est_frota_1",
                label_visibility="collapsed"
            )

            if estilo_g1 == "Colunas":
                fig1 = px.bar(
                    contagem_tipo,
                    x='Tipo de Veículo',
                    y='Quantidade',
                    text='Quantidade',
                    color='Tipo de Veículo',
                    color_discrete_sequence=PALETA_ALS
                )
                fig1 = estilizar_grafico_colunas(fig1)
                fig1.update_layout(showlegend=False)
            else:
                furo = 0.42 if estilo_g1 == "Rosca com Borda" else 0.0
                fig1 = px.pie(
                    contagem_tipo,
                    names='Tipo de Veículo',
                    values='Quantidade',
                    color_discrete_sequence=PALETA_ALS
                )
                fig1 = estilizar_grafico_pizza(fig1, furo=furo)

            st.plotly_chart(fig1, use_container_width=True)

    with col_dir:
        with st.container(border=True):
            c_head3, c_head4 = st.columns([2, 1])
            c_head3.subheader(":material/bar_chart: Volume por Categoria (Colunas)")
            estilo_g2 = c_head4.selectbox(
                "Estilo",
                ["Colunas Verticais", "Barras Horizontais", "Pizza com Borda"],
                key="est_frota_2",
                label_visibility="collapsed"
            )

            if estilo_g2 == "Pizza com Borda":
                fig2 = px.pie(
                    contagem_tipo,
                    names='Tipo de Veículo',
                    values='Quantidade',
                    color_discrete_sequence=PALETA_ALS
                )
                fig2 = estilizar_grafico_pizza(fig2, furo=0.0)
            elif estilo_g2 == "Barras Horizontais":
                fig2 = px.bar(
                    contagem_tipo.sort_values('Quantidade', ascending=True),
                    x='Quantidade',
                    y='Tipo de Veículo',
                    orientation='h',
                    text='Quantidade',
                    color='Tipo de Veículo',
                    color_discrete_sequence=PALETA_ALS
                )
                fig2.update_traces(marker_line_color='#1E293B', marker_line_width=1.5, textposition='outside')
                fig2.update_layout(
                    paper_bgcolor='#EAEFF5',
                    plot_bgcolor='#EAEFF5',
                    font=dict(family="Segoe UI, sans-serif", size=13, color='#0F172A'),
                    showlegend=False,
                    margin=dict(t=20, b=20, l=20, r=30),
                    height=360
                )
            else:
                fig2 = px.bar(
                    contagem_tipo,
                    x='Tipo de Veículo',
                    y='Quantidade',
                    text='Quantidade',
                    color='Tipo de Veículo',
                    color_discrete_sequence=PALETA_ALS
                )
                fig2 = estilizar_grafico_colunas(fig2)
                fig2.update_layout(showlegend=False)

            st.plotly_chart(fig2, use_container_width=True)

    # Tabela da Frota Filtrada
    with st.container(border=True):
        st.subheader(":material/table_chart: Relação de Veículos da Frota")
        st.dataframe(
            df_vf[['placa', 'tipo_veiculo', 'descricao', 'ultima_km', 'data_cadastro', 'STATUS_TXT']].rename(columns={
                'placa': 'PLACA',
                'tipo_veiculo': 'TIPO / MARCA',
                'descricao': 'DESCRIÇÃO',
                'ultima_km': 'ÚLTIMA KM',
                'data_cadastro': 'DATA CADASTRO',
                'STATUS_TXT': 'STATUS'
            }),
            use_container_width=True,
            height=280
        )


def renderizar_aba_manutencoes(df, veiculos):
    """Renderiza os gráficos de Manutenção com filtros completos e seletores de estilo"""
    if df is None or df.empty:
        st.info(
            "Nenhum registro de manutenção lançado no banco até o momento. "
            "Utilize a guia 'Panorama da Frota' para visualizar a distribuição dos veículos cadastrados."
        )
        return

    for col in ['PLACA', 'VEÍCULO', 'STATUS', 'DESTINO PROGRAMADO', 'SERVIÇO A EXECUTAR', 'NRº OF', 'OBS']:
        if col not in df.columns:
            df[col] = ''
        df[col] = df[col].fillna('').astype(str)

    df['DIAS_NUM'] = pd.to_numeric(df.get('DIAS', 0), errors='coerce').fillna(0)
    df['DATA_ENTRADA_DT'] = pd.to_datetime(df['DATA ENTRADA'], format='%d/%m/%Y', dayfirst=True, errors='coerce')

    # Filtros na Barra Lateral
    st.sidebar.subheader(":material/filter_alt: Filtros de Manutenção")
    busca_texto = st.sidebar.text_input("Busca Rápida (Placa, Serviço, OF)", placeholder="Digite para filtrar...")

    opcoes_status = sorted([s for s in df['STATUS'].unique() if s.strip()])
    filtro_status = st.sidebar.multiselect("Status da Manutenção", options=opcoes_status, default=[])

    opcoes_placas = sorted([p for p in df['PLACA'].unique() if p.strip()])
    filtro_placas = st.sidebar.multiselect("Placa(s)", options=opcoes_placas, default=[])

    opcoes_veiculos = sorted([v for v in df['VEÍCULO'].unique() if v.strip()])
    filtro_veiculos = st.sidebar.multiselect("Tipo de Veículo", options=opcoes_veiculos, default=[])

    opcoes_destinos = sorted([d for d in df['DESTINO PROGRAMADO'].unique() if d.strip()])
    filtro_destinos = st.sidebar.multiselect("Destino Programado", options=opcoes_destinos, default=[])

    datas_validas = df['DATA_ENTRADA_DT'].dropna()
    usar_filtro_data = st.sidebar.checkbox("Filtrar por Período de Entrada", value=False)
    data_ini, data_fim = None, None
    if usar_filtro_data and not datas_validas.empty:
        min_date = datas_validas.min().date()
        max_date = datas_validas.max().date()
        intervalo = st.sidebar.date_input("Período", value=(min_date, max_date))
        if isinstance(intervalo, tuple) and len(intervalo) == 2:
            data_ini, data_fim = intervalo

    # Aplicação dos filtros
    df_f = df.copy()
    if busca_texto.strip():
        t = busca_texto.strip().lower()
        mascara = (
            df_f['PLACA'].str.lower().str.contains(t, na=False) |
            df_f['VEÍCULO'].str.lower().str.contains(t, na=False) |
            df_f['SERVIÇO A EXECUTAR'].str.lower().str.contains(t, na=False) |
            df_f['DESTINO PROGRAMADO'].str.lower().str.contains(t, na=False) |
            df_f['NRº OF'].str.lower().str.contains(t, na=False)
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
        df_f = df_f[(df_f['DATA_ENTRADA_DT'].dt.date >= data_ini) & (df_f['DATA_ENTRADA_DT'].dt.date <= data_fim)]

    # KPIs Corporativos
    total_reg = len(df_f)
    em_servico = len(df_f[df_f['STATUS'].str.upper().str.contains('MANUTENÇÃO|SERVIÇO|AGUARDANDO', na=False)])
    finalizados = len(df_f[df_f['STATUS'].str.upper().str.contains('FINALIZADO', na=False)])
    tempo_medio = df_f['DIAS_NUM'].mean() if total_reg > 0 else 0.0
    placas_atendidas = df_f['PLACA'].replace('', pd.NA).dropna().nunique()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Filtrado", f"{total_reg}")
    k2.metric("Em Serviço", f"{em_servico}")
    k3.metric("Finalizados", f"{finalizados}")
    k4.metric("Tempo Médio", f"{tempo_medio:.1f} dias")
    k5.metric("Placas Atendidas", f"{placas_atendidas}")

    st.markdown("")

    # Linha 1 de Gráficos: Pizza com Borda vs Colunas com Borda
    g1, g2 = st.columns(2)

    with g1:
        with st.container(border=True):
            ch1, ch2 = st.columns([2, 1])
            ch1.subheader(":material/pie_chart: Distribuição por Status")
            tipo_g1 = ch2.selectbox(
                "Tipo",
                ["Pizza com Borda", "Rosca com Borda", "Colunas"],
                key="manut_g1",
                label_visibility="collapsed"
            )
            df_status = df_f['STATUS'].replace('', 'NÃO INFORMADO').value_counts().reset_index()
            df_status.columns = ['Status', 'Quantidade']

            if tipo_g1 == "Colunas":
                fig_st = px.bar(
                    df_status, x='Status', y='Quantidade', text='Quantidade',
                    color='Status', color_discrete_sequence=PALETA_ALS
                )
                fig_st = estilizar_grafico_colunas(fig_st)
                fig_st.update_layout(showlegend=False)
            else:
                furo = 0.42 if tipo_g1 == "Rosca com Borda" else 0.0
                fig_st = px.pie(
                    df_status, names='Status', values='Quantidade',
                    color_discrete_sequence=PALETA_ALS
                )
                fig_st = estilizar_grafico_pizza(fig_st, furo=furo)

            st.plotly_chart(fig_st, use_container_width=True)

    with g2:
        with st.container(border=True):
            ch3, ch4 = st.columns([2, 1])
            ch3.subheader(":material/bar_chart: Manutenções por Veículo")
            tipo_g2 = ch4.selectbox(
                "Tipo",
                ["Colunas Verticais", "Barras Horizontais", "Pizza com Borda"],
                key="manut_g2",
                label_visibility="collapsed"
            )
            df_veic = df_f['VEÍCULO'].replace('', 'OUTROS').value_counts().head(10).reset_index()
            df_veic.columns = ['Veículo', 'Quantidade']

            if tipo_g2 == "Pizza com Borda":
                fig_v = px.pie(
                    df_veic, names='Veículo', values='Quantidade',
                    color_discrete_sequence=PALETA_ALS
                )
                fig_v = estilizar_grafico_pizza(fig_v, furo=0.0)
            elif tipo_g2 == "Barras Horizontais":
                fig_v = px.bar(
                    df_veic.sort_values('Quantidade', ascending=True),
                    x='Quantidade', y='Veículo', orientation='h', text='Quantidade',
                    color='Veículo', color_discrete_sequence=PALETA_ALS
                )
                fig_v.update_traces(marker_line_color='#1E293B', marker_line_width=1.5, textposition='outside')
                fig_v.update_layout(
                    paper_bgcolor='#EAEFF5', plot_bgcolor='#EAEFF5',
                    font=dict(family="Segoe UI, sans-serif", size=13, color='#0F172A'),
                    showlegend=False, height=360
                )
            else:
                fig_v = px.bar(
                    df_veic, x='Veículo', y='Quantidade', text='Quantidade',
                    color='Veículo', color_discrete_sequence=PALETA_ALS
                )
                fig_v = estilizar_grafico_colunas(fig_v)
                fig_v.update_layout(showlegend=False)

            st.plotly_chart(fig_v, use_container_width=True)

    # Linha 2: Top 10 Placas em Colunas
    with st.container(border=True):
        st.subheader(":material/local_shipping: Top 10 Placas por Ocorrências e Dias Parados")
        df_top_placas = (
            df_f[df_f['PLACA'] != '']
            .groupby('PLACA')
            .agg(Ocorrencias=('ID', 'count'), Dias_Parados=('DIAS_NUM', 'sum'))
            .reset_index()
            .sort_values(by='Ocorrencias', ascending=False)
            .head(10)
        )
        fig_placas = px.bar(
            df_top_placas,
            x='PLACA',
            y='Ocorrencias',
            text='Ocorrencias',
            hover_data=['Dias_Parados'],
            color='Dias_Parados',
            color_continuous_scale=['#607D8B', '#4CAF50']
        )
        fig_placas = estilizar_grafico_colunas(fig_placas)
        st.plotly_chart(fig_placas, use_container_width=True)

    # Tabela Detalhada
    with st.container(border=True):
        st.subheader(":material/table_chart: Registros Filtrados")
        st.dataframe(df_f.drop(columns=['DIAS_NUM', 'DATA_ENTRADA_DT'], errors='ignore'), use_container_width=True, height=300)


def main():
    df, veiculos, destinos, notas = carregar_dados()

    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.title(":material/analytics: Painel de Indicadores e Frota - ALS")
    with col_t2:
        if st.button(":material/refresh: Atualizar Dados", use_container_width=True):
            st.rerun()

    if df is None or df.empty:
        aba_frota, aba_manut = st.tabs([
            ":material/local_shipping: Panorama da Frota",
            ":material/build: Indicadores de Manutenção"
        ])
        with aba_frota:
            renderizar_aba_frota(veiculos, notas)
        with aba_manut:
            renderizar_aba_manutencoes(df, veiculos)
    else:
        aba_manut, aba_frota = st.tabs([
            ":material/build: Indicadores de Manutenção",
            ":material/local_shipping: Panorama da Frota"
        ])
        with aba_manut:
            renderizar_aba_manutencoes(df, veiculos)
        with aba_frota:
            renderizar_aba_frota(veiculos, notas)


if __name__ == "__main__":
    main()
