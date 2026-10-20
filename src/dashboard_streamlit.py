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
import plotly.graph_objects as go

# Garante que o diretório raiz está no sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.controllers.manutencao_controller import ManutencaoController
from src.controllers.veiculo_controller import VeiculoController
from src.controllers.destino_controller import DestinoController
from src.controllers.nota_controller import NotaController
from src.services.manutencao.status import (
    STATUS_AGENDADO, STATUS_EM_MANUTENCAO, STATUS_FINALIZADO, STATUS_SINISTRO
)
from src.services.dashboard.calcular_dias_corridos import calcular_dias_corridos
from src.services.dashboard.contar_por_status import contar_por_status
from src.services.dashboard.calcular_kpis_manutencao import calcular_kpis_manutencao
from src.services.dashboard.agrupar_por_faixa_aging import agrupar_por_faixa_aging
from src.services.dashboard.ranking_dias_parados import ranking_dias_parados

# Configuração da página Streamlit
st.set_page_config(
    page_title="Dashboard Analítico ALS",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta Oficial ALS
PALETA_ALS = [
    '#4CAF50', '#607D8B', '#789DAB', '#90E74A', 
    '#2E7D32', '#455A64', '#0284C7', '#26A69A',
    '#5C6BC0', '#8D6E63', '#78909C', '#66BB6A'
]

# Estilo CSS Corporativo
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
        padding: 12px;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=20)
def carregar_dados():
    """Carrega dados atualizados diretamente dos Controllers MVC (com cache de 20s)"""
    manut_ctrl = ManutencaoController()
    veic_ctrl = VeiculoController()
    dest_ctrl = DestinoController()
    nota_ctrl = NotaController()

    df_manut = manut_ctrl.obter_dataframe_exibicao()
    veiculos = veic_ctrl.obter_todos() or []
    destinos = dest_ctrl.obter_todos() or []
    notas = nota_ctrl.obter_todas() or []

    return df_manut, veiculos, destinos, notas


LAYOUT_BASE = dict(
    paper_bgcolor='#EAEFF5',
    plot_bgcolor='#EAEFF5',
    font=dict(family="Segoe UI, sans-serif", size=12, color='#0F172A'),
)

# Cores com significado operacional (atenção = quente, ok = verde)
STATUS_CORES = {
    STATUS_AGENDADO: '#0284C7',
    STATUS_EM_MANUTENCAO: '#F59E0B',
    STATUS_FINALIZADO: '#4CAF50',
    STATUS_SINISTRO: '#DC2626',
}
COR_STATUS_OUTROS = '#78909C'
FAIXA_CORES = {
    '0–3 dias': '#4CAF50',
    '4–7 dias': '#F59E0B',
    '8–15 dias': '#EA580C',
    '16+ dias': '#DC2626',
}


def estilizar_barras_horizontais(fig, altura=340):
    """Barras horizontais com valor na ponta; a 1ª linha do DataFrame fica no topo"""
    maior = max((max(t.x) for t in fig.data if t.x is not None and len(t.x)), default=0)
    fig.update_traces(
        marker_line_color='#1E293B',
        marker_line_width=1.2,
        textposition='outside',
        cliponaxis=False
    )
    fig.update_layout(
        **LAYOUT_BASE,
        showlegend=False,
        height=altura,
        margin=dict(t=15, b=15, l=10, r=50),
        xaxis=dict(gridcolor='#CBD5E1', zerolinecolor='#94A3B8', title=None, rangemode='tozero',
                   dtick=1 if maior <= 8 else None),
        yaxis=dict(title=None, autorange='reversed'),
    )
    return fig


def grafico_distribuicao_status(contagem):
    """Barra única empilhada com a proporção por status (substitui a pizza)"""
    fig = go.Figure()
    for _, linha in contagem.iterrows():
        fig.add_trace(go.Bar(
            x=[linha['Quantidade']], y=[''], orientation='h', name=linha['Status'],
            text=[linha['Quantidade']], textposition='inside',
            marker=dict(color=STATUS_CORES.get(linha['Status'], COR_STATUS_OUTROS),
                        line=dict(color='#1E293B', width=1.2)),
            hovertemplate=f"{linha['Status']}: %{{x}}<extra></extra>",
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        barmode='stack',
        height=120,
        margin=dict(t=5, b=5, l=5, r=5),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        legend=dict(orientation='h', yanchor='top', y=0.0, xanchor='left', x=0, font=dict(size=11), traceorder='normal'),
    )
    return fig


def renderizar_aba_frota(veiculos, notas):
    """Panorama da frota cadastrada: volume por categoria e situação (ativo/inativo)"""
    if not veiculos:
        st.warning("Nenhum veículo cadastrado no banco de dados.")
        return

    df_v = pd.DataFrame(veiculos)
    for col in ['placa', 'tipo_veiculo', 'descricao']:
        if col not in df_v.columns:
            df_v[col] = ''
        df_v[col] = df_v[col].fillna('').astype(str).str.strip().str.upper()

    df_v['ultima_km_num'] = pd.to_numeric(df_v.get('ultima_km', 0), errors='coerce').fillna(0)
    df_v['STATUS_TXT'] = df_v.get('ativo', 1).apply(lambda x: 'ATIVO' if x else 'INATIVO')

    # Filtros na barra lateral para a Frota
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

    df_vf = df_vf.assign(tipo_veiculo=df_vf['tipo_veiculo'].replace('', 'OUTROS'))
    contagem_tipo = df_vf['tipo_veiculo'].value_counts().reset_index()
    contagem_tipo.columns = ['Tipo de Veículo', 'Quantidade']

    col_esq, col_dir = st.columns(2)

    with col_esq:
        with st.container(border=True):
            st.subheader(":material/bar_chart: Veículos por Categoria")
            fig1 = px.bar(
                contagem_tipo, x='Quantidade', y='Tipo de Veículo', orientation='h',
                text='Quantidade', color_discrete_sequence=['#607D8B']
            )
            st.plotly_chart(estilizar_barras_horizontais(fig1, altura=360), use_container_width=True)

    with col_dir:
        with st.container(border=True):
            st.subheader(":material/toggle_on: Situação por Categoria")
            situacao = (
                df_vf.groupby(['tipo_veiculo', 'STATUS_TXT']).size().reset_index(name='Quantidade')
            )
            ordem = contagem_tipo['Tipo de Veículo'].tolist()
            fig2 = px.bar(
                situacao, x='Quantidade', y='tipo_veiculo', color='STATUS_TXT', orientation='h',
                color_discrete_map={'ATIVO': '#4CAF50', 'INATIVO': '#94A3B8'},
                category_orders={'tipo_veiculo': ordem}, text='Quantidade'
            )
            fig2.update_traces(marker_line_color='#1E293B', marker_line_width=1.2, textposition='inside')
            fig2.update_layout(
                **LAYOUT_BASE, barmode='stack', height=360, margin=dict(t=15, b=15, l=10, r=10),
                xaxis=dict(gridcolor='#CBD5E1', title=None),
                yaxis=dict(title=None, autorange='reversed'),
                legend=dict(title=None, orientation='h', yanchor='bottom', y=1.0, xanchor='left', x=0),
            )
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
    """Indicadores de manutenção: status como filtro, fila por tempo parado e ranking de dias parados"""
    if df is None or df.empty:
        st.info(
            "Nenhum registro de manutenção lançado no banco até o momento. "
            "Utilize a guia 'Panorama da Frota' para visualizar a distribuição dos veículos cadastrados."
        )
        return

    for col in ['PLACA', 'VEÍCULO', 'STATUS', 'DESTINO PROGRAMADO', 'SERVIÇO A EXECUTAR', 'NRº OF', 'OBS', 'DATA SAÍDA']:
        if col not in df.columns:
            df[col] = ''
        df[col] = df[col].fillna('').astype(str).str.strip()
    df['STATUS'] = df['STATUS'].replace('', 'NÃO INFORMADO')

    # Dias parados recalculados na hora (o valor gravado só é atualizado ao salvar o registro)
    df = calcular_dias_corridos(df)

    # Filtros na Barra Lateral (o status fica em destaque na área principal)
    st.sidebar.subheader(":material/filter_alt: Filtros de Manutenção")
    busca_texto = st.sidebar.text_input("Busca Rápida (Placa, Serviço, OF)", placeholder="Digite para filtrar...")

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

    # Aplicação dos filtros (exceto status)
    df_base = df.copy()
    if busca_texto.strip():
        t = busca_texto.strip().lower()
        mascara = (
            df_base['PLACA'].str.lower().str.contains(t, na=False) |
            df_base['VEÍCULO'].str.lower().str.contains(t, na=False) |
            df_base['SERVIÇO A EXECUTAR'].str.lower().str.contains(t, na=False) |
            df_base['DESTINO PROGRAMADO'].str.lower().str.contains(t, na=False) |
            df_base['NRº OF'].str.lower().str.contains(t, na=False)
        )
        df_base = df_base[mascara]
    if filtro_placas:
        df_base = df_base[df_base['PLACA'].isin(filtro_placas)]
    if filtro_veiculos:
        df_base = df_base[df_base['VEÍCULO'].isin(filtro_veiculos)]
    if filtro_destinos:
        df_base = df_base[df_base['DESTINO PROGRAMADO'].isin(filtro_destinos)]
    if usar_filtro_data and data_ini and data_fim:
        df_base = df_base[(df_base['DATA_ENTRADA_DT'].dt.date >= data_ini) & (df_base['DATA_ENTRADA_DT'].dt.date <= data_fim)]

    # Status como filtro principal: botões com a contagem de cada status
    contagem = contar_por_status(df_base)
    qtd_por_status = dict(zip(contagem['Status'], contagem['Quantidade']))
    selecionados = st.pills(
        "Filtrar por status",
        options=contagem['Status'].tolist(),
        selection_mode="multi",
        format_func=lambda s: f"{s} · {qtd_por_status.get(s, 0)}",
        key="manut_status",
    )
    df_f = df_base[df_base['STATUS'].isin(selecionados)] if selecionados else df_base

    if not contagem.empty:
        st.plotly_chart(grafico_distribuicao_status(contagem), use_container_width=True)

    # KPIs: parados e disponibilidade olham a frota inteira; o restante respeita os filtros
    frota_ativa = sum(1 for v in (veiculos or []) if v.get('ativo', 1))
    kpi_frota = calcular_kpis_manutencao(df, frota_ativa)
    kpi = calcular_kpis_manutencao(df_f, frota_ativa)

    n_finalizados = int(df_f['FINALIZADO'].sum())
    disp = kpi_frota['disponibilidade']
    mttr = kpi['tempo_medio_reparo']
    antigo = kpi['mais_antigo_dias']

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Veículos Parados", f"{kpi_frota['parados']}",
              delta=f"de {frota_ativa} ativos", delta_color="off", delta_arrow="off",
              help="Placas com registro EM MANUTENÇÃO ou SINISTRO. Agendados e finalizados não contam. Considera toda a frota.")
    k2.metric("Disponibilidade", f"{disp:.0f}%" if disp is not None else "—",
              delta=f"{max(frota_ativa - kpi_frota['parados'], 0)} operando", delta_color="off", delta_arrow="off",
              help="1 − (veículos parados ÷ veículos ativos cadastrados). Considera toda a frota.")
    k3.metric("Reparo Médio", f"{mttr:.1f} dias" if mttr is not None else "—",
              delta=f"{n_finalizados} finalizados", delta_color="off", delta_arrow="off",
              help="Tempo médio de reparo: média de dias dos registros finalizados no filtro atual.")
    k4.metric("Mais Antigo", f"{antigo} dias" if antigo is not None else "—",
              delta=(kpi['mais_antigo_placa'] if antigo is not None else "sem abertos"),
              delta_color="off", delta_arrow="off",
              help="Registro em aberto há mais tempo no filtro atual.")
    k5.metric("Reincidentes", f"{kpi['reincidentes']}",
              delta="3+ entradas em 90 dias", delta_color="off", delta_arrow="off",
              help="Placas com 3 ou mais entradas na manutenção nos últimos 90 dias.")

    st.markdown("")

    g1, g2 = st.columns(2)

    with g1:
        with st.container(border=True):
            st.subheader(":material/hourglass_top: Em Aberto por Tempo Parado")
            fila = agrupar_por_faixa_aging(df_f)
            if fila['Quantidade'].sum() == 0:
                st.success("Nenhum veículo em aberto neste filtro.")
            else:
                fig_fila = go.Figure(go.Bar(
                    x=fila['Quantidade'], y=fila['Faixa'], orientation='h',
                    text=fila['Quantidade'], marker_color=[FAIXA_CORES[f] for f in fila['Faixa']]
                ))
                st.plotly_chart(estilizar_barras_horizontais(fig_fila, altura=340), use_container_width=True)

    with g2:
        with st.container(border=True):
            st.subheader(":material/local_shipping: Top 10 Placas por Dias Parados")
            ranking = ranking_dias_parados(df_f)
            if ranking.empty:
                st.info("Sem registros para o filtro atual.")
            else:
                fig_rank = px.bar(
                    ranking, x='Dias_Parados', y='PLACA', orientation='h', text='Dias_Parados',
                    hover_data=['Ocorrencias'], color_discrete_sequence=['#607D8B']
                )
                st.plotly_chart(estilizar_barras_horizontais(fig_rank, altura=340), use_container_width=True)

    g3, g4 = st.columns(2)

    with g3:
        with st.container(border=True):
            st.subheader(":material/directions_bus: Manutenções por Tipo de Veículo")
            por_tipo = df_f['VEÍCULO'].replace('', 'OUTROS').value_counts().head(10).reset_index()
            por_tipo.columns = ['Tipo', 'Quantidade']
            fig_tipo = px.bar(
                por_tipo, x='Quantidade', y='Tipo', orientation='h', text='Quantidade',
                color_discrete_sequence=['#789DAB']
            )
            st.plotly_chart(estilizar_barras_horizontais(fig_tipo, altura=300), use_container_width=True)

    with g4:
        with st.container(border=True):
            st.subheader(":material/priority_high: Maiores Tempos em Aberto")
            abertos = df_f[df_f['ABERTO']].sort_values('DIAS_NUM', ascending=False).head(8)
            if abertos.empty:
                st.success("Nenhum veículo em aberto neste filtro.")
            else:
                st.dataframe(
                    abertos[['PLACA', 'VEÍCULO', 'STATUS', 'DIAS_NUM', 'SERVIÇO A EXECUTAR']].rename(
                        columns={'DIAS_NUM': 'DIAS PARADO'}
                    ),
                    use_container_width=True, hide_index=True, height=min(300, 40 + 35 * len(abertos))
                )

    # Tabela Detalhada (dias já atualizados)
    with st.container(border=True):
        st.subheader(":material/table_chart: Registros Filtrados")
        tabela = df_f.assign(DIAS=df_f['DIAS_NUM']).drop(
            columns=['DIAS_NUM', 'DATA_ENTRADA_DT', 'DATA_SAIDA_DT', 'ABERTO', 'FINALIZADO'], errors='ignore'
        )
        st.dataframe(tabela, use_container_width=True, height=300)


def main():
    df, veiculos, destinos, notas = carregar_dados()

    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.title(":material/analytics: Painel de Indicadores e Frota - ALS")
    with col_t2:
        if st.button(":material/refresh: Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
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
