import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.tratamento import calcular_tempos


def exibir_metricas_dataframe(df):
    col1, col2 = st.columns(2)

    col1.metric("Linhas", f"{len(df):,}")
    col2.metric("Colunas", len(df.columns))

    st.subheader("Pré-visualização")
    st.dataframe(df, use_container_width=True)


def exibir_indicadores_operacionais(df):
    st.markdown("---")
    st.header("🚀 Indicadores Operacionais")

    tempo_estimado, tempo_realizado, tempo_total = calcular_tempos(df)

    # ============================
    # KPIs
    # ============================

    k1, k2, k3 = st.columns(3)

    if tempo_estimado is not None and not tempo_estimado.dropna().empty:
        k1.metric("Tempo médio estimado", f"{tempo_estimado.mean():.1f} min")

    if tempo_realizado is not None and not tempo_realizado.dropna().empty:
        k2.metric("Tempo médio realizado", f"{tempo_realizado.mean():.1f} min")

    if tempo_total is not None and not tempo_total.dropna().empty:
        k3.metric("Tempo médio total", f"{tempo_total.mean():.1f} min")

    # ============================
    # Comparativo dos tempos
    # ============================

    comparativo = pd.DataFrame(
        {
            "Etapa": [
                "Tempo até o aceite",
                "Tempo até o cliente",
                "Tempo total",
            ],
            "Tempo Médio (min)": [
                tempo_estimado.mean() if tempo_estimado is not None else np.nan,
                tempo_realizado.mean() if tempo_realizado is not None else np.nan,
                tempo_total.mean() if tempo_total is not None else np.nan,
            ],
        }
    )

    fig = px.bar(
        comparativo,
        x="Etapa",
        y="Tempo Médio (min)",
        text_auto=".1f",
        color="Etapa",
        title="Tempo Médio por Etapa da Entrega",
    )

    fig.update_traces(
        textposition="outside",
        textfont_size=14,
    )

    fig.update_layout(
        xaxis_title="Etapas da Operação",
        yaxis_title="Tempo (minutos)",
        showlegend=False,
        height=500,
    )

    fig.add_hline(
        y=40,
        line_dash="dash",
        line_color="red",
        annotation_text="Meta SLA (40 min)",
    )

    st.plotly_chart(fig, use_container_width=True)

    # ============================
    # Boxplot
    # ============================

    dados_box = pd.DataFrame(
        {
            "Estimado": tempo_estimado,
            "Realizado": tempo_realizado,
            "Total": tempo_total,
        }
    ).apply(pd.to_numeric, errors="coerce")

    dados_box = dados_box.melt(
        var_name="Indicador",
        value_name="Tempo",
    ).dropna(subset=["Tempo"])

    if not dados_box.empty:
        fig = px.box(
            dados_box,
            x="Indicador",
            y="Tempo",
            title="Distribuição dos Tempos",
        )

        st.plotly_chart(fig, use_container_width=True)

    # ============================
    # Correlação
    # ============================

    if tempo_estimado is not None and tempo_realizado is not None:
        exibir_correlacao(
            tempo_estimado,
            tempo_realizado,
        )


def exibir_correlacao(tempo_estimado, tempo_realizado):
    correlacao = pd.DataFrame(
        {
            "Estimado": tempo_estimado,
            "Realizado": tempo_realizado,
        }
    )

    fig = px.scatter(
        correlacao,
        x="Estimado",
        y="Realizado",
        title="Tempo Estimado x Tempo Realizado",
    )

    x_series = correlacao["Estimado"].dropna()
    y_series = correlacao["Realizado"].dropna()

    if not x_series.empty and not y_series.empty:
        common_idx = x_series.index.intersection(y_series.index)

        x_vals = x_series.loc[common_idx].to_numpy()
        y_vals = y_series.loc[common_idx].to_numpy()

        if x_vals.size > 1:
            slope, intercept = np.polyfit(x_vals, y_vals, 1)

            line_x = np.linspace(
                x_vals.min(),
                x_vals.max(),
                100,
            )

            line_y = slope * line_x + intercept

            fig.add_trace(
                go.Scatter(
                    x=line_x,
                    y=line_y,
                    mode="lines",
                    name="Linha de tendência",
                    line=dict(color="red"),
                )
            )

    st.plotly_chart(fig, use_container_width=True)
