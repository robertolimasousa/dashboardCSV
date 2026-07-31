import streamlit as st

from config import LOGO
from pathlib import Path

from utils.graficos import exibir_analise_interativa
from utils.indicadores import (
    exibir_indicadores_operacionais,
    exibir_metricas_dataframe,
)
from utils.tratamento import (
    ler_csv,
    preparar_dataframe,
    selecionar_colunas_por_categoria,
)

BASE_DIR = Path(__file__).resolve().parent


def carregar_css():
    css = BASE_DIR / "assets" / "style.css"

    if css.exists():
        with open(css, encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True,
            )
    else:
        st.warning("Arquivo CSS não encontrado em assets/style.css.")


def main():
    carregar_css()
    if LOGO.exists():
        st.image(str(LOGO), width=220)

    st.title("📊 Dashboard Operacional Zero48")
    st.caption("Análise de Tempo de Entrega")
    st.sidebar.title("📦 Zero48 Dashboard")

    arquivo = st.sidebar.file_uploader("Selecione um arquivo CSV", type=["csv"])
    if arquivo is None:
        st.info("Selecione um arquivo CSV na barra lateral.")
        return

    with st.spinner("Carregando planilha..."):
        df = ler_csv(arquivo)

    if df is None:
        st.error("Não foi possível ler este arquivo CSV.")
        return

    df = preparar_dataframe(df)

    categorias_colunas = {
        "estimativa_tempo": [
            "estimativa de tempo",
            "estimativa tempo",
            "estimate",
            "estim",
        ],
        "tempo_realizado": [
            "tempo realizado",
            "realizado até o cliente",
            "tempo até o cliente",
            "tempo de entrega",
        ],
        "tempo_total": [
            "tempo do início",
            "tempo total",
            "tempo do início da solicitação",
            "tempo do início da solicitação até o local de encerramento",
        ],
        "estimativa_distancia": [
            "estimativa de distância",
            "distância estimada",
            "distancia estimada",
            "estimativa distância",
        ],
        "momento_aceite": [
            "momento do aceite",
            "momento aceite",
            "aceite",
        ],
    }

    colunas_encontradas = selecionar_colunas_por_categoria(df, categorias_colunas)
    if not colunas_encontradas:
        st.error(
            "Não foi possível identificar as colunas esperadas no CSV. Verifique os cabeçalhos e tente novamente."
        )
        st.write("Colunas detectadas:", list(df.columns))
        return

    df_graficos = df[colunas_encontradas].copy()

    st.success("✅ Planilha carregada com sucesso!")

    exibir_metricas_dataframe(df_graficos)
    exibir_indicadores_operacionais(df_graficos)
    exibir_analise_interativa(df_graficos)


if __name__ == "__main__":
    main()
