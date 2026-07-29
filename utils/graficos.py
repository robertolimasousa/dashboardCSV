import pandas as pd
import plotly.express as px
import streamlit as st


def criar_grafico_coluna(df, coluna, tipo):
    serie = df[coluna]

    if pd.api.types.is_object_dtype(serie) or pd.api.types.is_string_dtype(serie):
        dados = serie.fillna("Sem informação").astype(str).value_counts().head(20)
        return px.bar(
            x=dados.index,
            y=dados.values,
            title=f"Distribuição de {coluna}",
            labels={"x": coluna, "y": "Quantidade"},
        )

    if tipo == "📈 Histograma":
        coluna_lower = coluna.strip().lower()
        is_date_column = coluna_lower in {
            "data",
            "hora",
            "data_hora",
        } or pd.api.types.is_datetime64_any_dtype(df[coluna])

        if is_date_column and "data_hora" in df.columns:
            daily_counts = df.groupby(df["data_hora"].dt.date).size()
            return px.bar(
                x=daily_counts.index,
                y=daily_counts.values,
                title="Quantidade de entregas por dia",
                labels={"x": "Dia", "y": "Quantidade de entregas"},
            )
        if is_date_column:
            daily_counts = (
                pd.to_datetime(df[coluna], errors="coerce")
                .dt.date.value_counts()
                .sort_index()
            )
            return px.bar(
                x=daily_counts.index,
                y=daily_counts.values,
                title="Quantidade de entregas por dia",
                labels={"x": "Dia", "y": "Quantidade de entregas"},
            )
        return px.histogram(df, x=coluna, nbins=30, title=f"Distribuição de {coluna}")

    dados = df[coluna].value_counts().sort_index()
    return px.bar(
        x=dados.index,
        y=dados.values,
        title=f"Distribuição de {coluna}",
        labels={"x": coluna, "y": "Quantidade"},
    )


def exibir_estatisticas(df, coluna):
    st.markdown("---")
    st.subheader("📋 Estatísticas")

    if pd.api.types.is_numeric_dtype(df[coluna]):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média", round(df[coluna].mean(), 2))
        c2.metric("Mediana", round(df[coluna].median(), 2))
        c3.metric("Mínimo", round(df[coluna].min(), 2))
        c4.metric("Máximo", round(df[coluna].max(), 2))
    else:
        st.write(df[coluna].value_counts().head(20))


def exibir_analise_interativa(df):
    st.markdown("---")
    st.header("📊 Análise Interativa")

    estimate_columns = [
        coluna
        for coluna in df.columns
        if "estim" in coluna.lower() or "estimate" in coluna.lower()
    ]

    if estimate_columns:
        st.markdown("#### 📈 Colunas de estimativa detectadas")
        st.write(estimate_columns)
        selected_estimate = st.selectbox(
            "Escolha uma coluna de estimativa:", estimate_columns
        )
    else:
        selected_estimate = None
        st.info(
            "Nenhuma coluna de estimativa encontrada pelo nome. Escolha outra coluna para análise."
        )

    colunas_grafico = [
        "comercio",
        "bairro",
        "motoboy",
        "status",
        "dia_semana",
    ]

    colunas_disponiveis = [c for c in colunas_grafico if c in df.columns]
    if not colunas_disponiveis:
        st.warning(
            "Nenhuma das colunas de análise esperadas foi encontrada no arquivo CSV. "
            "Selecione outra coluna disponível para a análise."
        )
        colunas_disponiveis = [
            c for c in df.columns if c != "data_hora" and c not in estimate_columns
        ]

    if not colunas_disponiveis:
        st.warning("Não há colunas disponíveis para criar a análise interativa.")
        return

    coluna = st.selectbox("Escolha uma análise:", colunas_disponiveis)
    tipo = st.radio("Tipo de gráfico:", ["📊 Barras", "📈 Histograma"], horizontal=True)

    fig = criar_grafico_coluna(df, coluna, tipo)
    st.plotly_chart(fig, use_container_width=True)

    if selected_estimate is not None and "data_hora" in df.columns:
        st.markdown("---")
        st.subheader("📅 Análise Temporal de Estimativa")
        temporal_fig = px.line(
            df,
            x="data_hora",
            y=selected_estimate,
            title=f"Evolução de {selected_estimate} ao longo do tempo",
        )
        st.plotly_chart(temporal_fig, use_container_width=True)

    exibir_estatisticas(df, coluna)
