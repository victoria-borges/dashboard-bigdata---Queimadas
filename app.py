import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Dashboard Big Data - Queimadas",
    page_icon="🔥",
    layout="wide"
)

# CARREGAR DADOS
df = pd.read_csv("dados_queimadas_unificado.csv")

df["data_hora_gmt"] = pd.to_datetime(df["data_hora_gmt"])
df["mes"] = df["data_hora_gmt"].dt.month
df["data"] = df["data_hora_gmt"].dt.date

# TÍTULO
st.markdown("""
# 🔥 Dashboard Big Data de Queimadas
### Análise de focos de queimadas no Brasil com dados públicos do INPE
""")

st.markdown("---")

# FILTROS
st.sidebar.title("🔎 Filtros")

estados = ["Todos"] + sorted(df["estado"].dropna().unique().tolist())
estado = st.sidebar.selectbox("Estado", estados)

satelites = ["Todos"] + sorted(df["satelite"].dropna().unique().tolist())
satelite = st.sidebar.selectbox("Satélite", satelites)

data_inicio = st.sidebar.date_input("Data inicial", df["data"].min())
data_fim = st.sidebar.date_input("Data final", df["data"].max())

df_filtrado = df.copy()

if estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["estado"] == estado]

if satelite != "Todos":
    df_filtrado = df_filtrado[df_filtrado["satelite"] == satelite]

df_filtrado = df_filtrado[
    (df_filtrado["data"] >= data_inicio) &
    (df_filtrado["data"] <= data_fim)
]

# MÉTRICAS
col1, col2, col3, col4 = st.columns(4)

total_focos = len(df_filtrado)
estado_top = df_filtrado["estado"].mode()[0] if not df_filtrado.empty else "-"
municipio_top = df_filtrado["municipio"].mode()[0] if not df_filtrado.empty else "-"
satelite_top = df_filtrado["satelite"].mode()[0] if not df_filtrado.empty else "-"

col1.metric("🔥 Total de focos", total_focos)
col2.metric("📍 Estado mais afetado", estado_top)
col3.metric("🏙️ Município mais afetado", municipio_top)
col4.metric("🛰️ Satélite principal", satelite_top)

st.markdown("---")

# GRÁFICOS
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    focos_mes = df_filtrado.groupby("mes").size().reset_index(name="quantidade")

    fig_mes = px.bar(
        focos_mes,
        x="mes",
        y="quantidade",
        title="📊 Focos de Queimadas por Mês",
        labels={"mes": "Mês", "quantidade": "Quantidade de focos"}
    )

    st.plotly_chart(fig_mes, use_container_width=True)

with col_graf2:
    focos_estado = (
        df_filtrado.groupby("estado")
        .size()
        .reset_index(name="quantidade")
        .sort_values(by="quantidade", ascending=False)
        .head(10)
    )

    fig_estado = px.bar(
        focos_estado,
        x="estado",
        y="quantidade",
        title="🔥 Top 10 Estados com Mais Focos",
        labels={"estado": "Estado", "quantidade": "Quantidade de focos"}
    )

    st.plotly_chart(fig_estado, use_container_width=True)


# MAPA
st.subheader("🗺️ Mapa Interativo dos Focos de Queimadas")

fig_mapa = px.scatter_mapbox(
    df_filtrado,
    lat="lat",
    lon="lon",
    hover_name="municipio",
    hover_data=["estado", "satelite", "data_hora_gmt"],
    zoom=3,
    height=550
)

fig_mapa.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0, "t":0, "l":0, "b":0}
)

st.plotly_chart(fig_mapa, use_container_width=True)

# =========================
# TABELA
# =========================
with st.expander("📄 Ver dados utilizados"):
    st.dataframe(df_filtrado)

st.caption("Fonte dos dados: Programa Queimadas - INPE | Projeto acadêmico de Tópicos em Big Data")
