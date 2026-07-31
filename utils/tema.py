import plotly.graph_objects as go


CORES_GRAFICO = ["#00d9ff", "#2878ff", "#7c4dff", "#00a8ff", "#53f2ff"]


def aplicar_tema_grafico(fig: go.Figure) -> go.Figure:
    """Aplica o tema do dashboard ao conteúdo interno dos gráficos Plotly."""
    fig.update_layout(
        paper_bgcolor="#070b14",
        plot_bgcolor="#070b14",
        font={"family": "Inter, Arial, sans-serif", "color": "#d9f8ff"},
        colorway=CORES_GRAFICO,
        margin={"l": 24, "r": 24, "t": 64, "b": 24},
        hoverlabel={"bgcolor": "#0d1b31", "font_color": "#d9f8ff"},
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#1e3a5f",
        tickfont={"color": "#91aeca"},
        title_font={"color": "#d9f8ff"},
    )
    fig.update_yaxes(
        gridcolor="#162b47",
        zerolinecolor="#1e3a5f",
        tickfont={"color": "#91aeca"},
        title_font={"color": "#d9f8ff"},
    )
    return fig
