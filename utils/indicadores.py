import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.tratamento import calcular_tempos
from utils.tema import aplicar_tema_grafico


def exibir_metricas_dataframe(df):
    col1, col2 = st.columns(2)

    col1.metric("Linhas", f"{len(df):,}")
    col2.metric("Colunas", len(df.columns))

    st.subheader("Pré-visualização")
    st.dataframe(df, width="stretch")


def exibir_indicadores_operacionais(df):
    st.markdown("---")
    st.header("🚀 Indicadores")

    tempo_estimado, tempo_realizado, tempo_total = calcular_tempos(df)

    # Função auxiliar para validar se a serie contem dados validos
    def possui_dados(serie):
        return serie is not None and not serie.dropna().empty

    # Cria as colunas fixas
    cols = st.columns(3)

    # 1. Tempo Médio Estimado
    if possui_dados(tempo_estimado):
        cols[0].metric("Tempo médio estimado", f"{tempo_estimado.mean():.1f} min")

    # 2. Tempo Médio Realizado
    if possui_dados(tempo_realizado):
        cols[1].metric("Tempo médio realizado", f"{tempo_realizado.mean():.1f} min")

    # 3. Tempo Médio Total
    if possui_dados(tempo_total):
        cols[2].metric("Tempo médio total", f"{tempo_total.mean():.1f} min")

    # ============================
    # Comparativo dos tempos em gráfico de barras
    # ============================

    series_tempos = [
        serie
        for serie in (tempo_estimado, tempo_realizado, tempo_total)
        if serie is not None
    ]
    if not series_tempos:
        st.info(
            "Não há colunas de tempo reconhecidas para gerar indicadores operacionais."
        )
        return

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
        title="Tempo médio de aceite",
    )

    fig.update_traces(
        textposition="outside",
        textfont_size=14,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Indicador: tempo médio da etapa<br>"
            "Valor: %{y:.1f} min<extra></extra>"
        ),
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

    st.plotly_chart(aplicar_tema_grafico(fig), width="stretch", theme=None)

    # ============================
    # Boxplot
    # ============================

    dados_box = pd.concat(
        [
            serie.rename(nome)
            for nome, serie in (
                ("Estimado", tempo_estimado),
                ("Realizado", tempo_realizado),
                ("Total", tempo_total),
            )
            if serie is not None
        ],
        axis=1,
    ).apply(pd.to_numeric, errors="coerce")

    dados_box = dados_box.melt(
        var_name="Indicador",
        value_name="Tempo",
    ).dropna(subset=["Tempo"])

    if not dados_box.empty:
        cores_indicadores = {
            "Estimado": "#00d9ff",
            "Realizado": "#2878ff",
            "Total": "#7c4dff",
        }
        resumo_box = (
            dados_box.groupby("Indicador")["Tempo"]
            .agg(Mediana="median", Média="mean", Mínimo="min", Máximo="max")
            .reindex(["Estimado", "Realizado", "Total"])
            .dropna(how="all")
        )
        st.caption("Indicadores da distribuição: mediana, média e intervalo observado por etapa.")
        cards_box = st.columns(len(resumo_box))
        for card, (indicador, valores) in zip(cards_box, resumo_box.iterrows()):
            card.metric(
                f"{indicador} · mediana",
                f"{valores['Mediana']:.1f} min",
                delta=(
                    f"Média {valores['Média']:.1f} · "
                    f"{valores['Mínimo']:.1f}–{valores['Máximo']:.1f} min"
                ),
                delta_color="off",
            )
        fig = px.box(
            dados_box,
            x="Indicador",
            y="Tempo",
            color="Indicador",
            color_discrete_map=cores_indicadores,
            points="all",
            title="Distribuição dos tempos por etapa",
            labels={"Indicador": "Etapa", "Tempo": "Tempo (minutos)"},
        )

        fig.update_traces(
            boxmean=True,
            boxpoints="all",
            jitter=0.28,
            pointpos=0,
            marker={"size": 5, "opacity": 0.42, "line": {"width": 0}},
            line={"width": 2},
            quartilemethod="exclusive",
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Indicador: tempo individual da etapa<br>"
                "Tempo observado: %{y:.1f} min<extra></extra>"
            ),
        )
        fig.add_hline(
            y=40,
            line_dash="dot",
            line_color="#00d9ff",
            line_width=1.5,
            annotation_text="Meta SLA · 40 min",
            annotation_position="top left",
            annotation_font_color="#8eeeff",
        )
        fig.update_layout(
            height=480,
            showlegend=False,
            title={"x": 0.02, "xanchor": "left", "font": {"size": 21}},
            margin={"l": 28, "r": 28, "t": 72, "b": 28},
        )
        fig.update_yaxes(rangemode="tozero", ticksuffix=" min")
        fig.add_annotation(
            x=0.5,
            y=1.12,
            xref="paper",
            yref="paper",
            showarrow=False,
            text=(
                "Estimado = previsão · Realizado = até o cliente · "
                "Total = duração da entrega"
            ),
            font={"size": 12, "color": "#91aeca"},
        )

        st.plotly_chart(aplicar_tema_grafico(fig), width="stretch", theme=None)

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
    fig.update_traces(
        hovertemplate=(
            "<b>Registro da entrega</b><br>"
            "Estimado: %{x:.1f} min<br>"
            "Realizado: %{y:.1f} min<extra></extra>"
        )
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

    st.plotly_chart(aplicar_tema_grafico(fig), width="stretch", theme=None)
