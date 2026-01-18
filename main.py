"""Dashboard de análisis de incendios forestales en España."""

from __future__ import annotations

from typing import Optional

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import polars as pl
from dash import Input, Output, State, dcc, html

from plots import (grafico_barras_comparativas, grafico_causas_por_año,
                   grafico_distribucion_superficie_incendios,
                   mapa_incendios_por_provincia)
from processing import CAUSAS, ccaa, fuegos, provincias_df
from utils import superficie_formateada, tendencia_incendios


class DashboardConfig:
    """Configuración centralizada del dashboard."""

    # Años de datos
    AÑO_MIN = fuegos.select("año").min().item()
    AÑO_MAX = fuegos.select("año").max().item()

    # Opciones de comunidades autónomas
    CCAA_OPTIONS = sorted(provincias_df.CCAA.unique().tolist())

    # Estilos
    TITLE_STYLE = {
        "fontSize": "3.2rem",
        "fontWeight": "800",
        "fontFamily": "Montserrat, sans-serif",
        "color": "#FFFFFF",
        "marginBottom": "0",
        "letterSpacing": "1px",
    }

    SUBTITLE_STYLE = {
        "color": "#666",
        "fontWeight": "400",
        "fontSize": "1.5rem",
    }

    KPI_TITLE_STYLE = {"fontSize": "1rem", "textAlign": "center"}
    KPI_VALUE_STYLE = {"fontSize": "1.4rem", "textAlign": "center"}
    CARD_HEADER_STYLE = {
        "textAlign": "center",
        "fontWeight": "600",
        "fontSize": "1.4rem",
    }

    # Temas externos
    EXTERNAL_STYLESHEETS = [
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap",
    ]


def create_kpi_card(title: str, value: str, kpi_id: str) -> dbc.Col:
    """
    Crea una tarjeta KPI reutilizable.

    :param title: Título del KPI
    :param value: Valor inicial del KPI
    :param kpi_id: ID único para el componente
    :return: Columna de Dash con la tarjeta KPI
    """
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.H3(title, style=DashboardConfig.KPI_TITLE_STYLE),
                    html.H2(
                        id=kpi_id,
                        children=value,
                        style=DashboardConfig.KPI_VALUE_STYLE,
                    ),
                ]
            )
        ),
        width=6,
        md=3,
        className="mb-2",
    )


def create_graph_card(
    card_id: str,
    header_text: str,
    graph_id: str,
    figure: Optional[go.Figure] = None,
    graph_config: Optional[dict] = None,
    graph_style: Optional[dict] = None,
    header_extra: Optional[list] = None,
) -> dbc.Card:
    """
    Crea una tarjeta con gráfico reutilizable.

    :param card_id: ID del contenedor de la tarjeta
    :param header_text: Texto del encabezado
    :param graph_id: ID del componente Graph
    :param figure: Figura de Plotly inicial
    :param graph_config: Configuración adicional del gráfico
    :param graph_style: Estilos CSS del gráfico
    :param header_extra: Componentes adicionales en el header
    :return: Tarjeta de Dash con el gráfico
    """
    header_content = [
        html.Span(header_text, style={"fontWeight": "600", "fontSize": "1.4rem"})
    ]

    if header_extra:
        header_content.extend(header_extra)

    header = dbc.CardHeader(
        html.Div(
            header_content,
            style={
                "textAlign": "center",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
            },
        )
        if header_extra
        else header_content[0]
    )

    return dbc.Card(
        [
            header,
            dbc.CardBody(
                dcc.Graph(
                    id=graph_id,
                    figure=figure,
                    config=graph_config or {},
                    style=graph_style or {},
                )
            ),
        ]
    )


def build_layout() -> dbc.Container:
    """
    Construye el layout completo del dashboard.

    :return: Contenedor principal de Dash
    """

    # KPIs calculados
    año_pico = (
        fuegos.group_by("año")
        .agg(pl.col("superficie").sum())
        .sort("superficie", descending=True)
        .item(0, "año")
    )

    return dbc.Container(
        id="contenedor-principal",
        fluid=True,
        style={"backgroundColor": "#252222"},
        children=[
            # Fila 1: Título y KPIs
            _build_header_and_kpis(año_pico),
            # Fila 2: Gráficos principales
            _build_main_charts(),
            # Fila 3: Gráficos secundarios
            _build_secondary_charts(),
            # Fila 4: Controles y créditos
            _build_controls_and_footer(),
        ],
    )


def _build_header_and_kpis(año_pico: int) -> dbc.Row:
    """
    Construye la fila de título y KPIs.

    :param año_pico: Año con mayor superficie afectada por incendios
    :return: Fila de Dash con título y KPIs
    """
    return dbc.Row(
        className="mb-4 align-items-center",
        children=[
            # Título
            dbc.Col(
                html.Div(
                    className="h-100 d-flex flex-column justify-content-center",
                    children=[
                        html.H2(
                            "PANEL DE CONTROL DE INCENDIOS EN ESPAÑA",
                            className="display-4",
                            style=DashboardConfig.TITLE_STYLE,
                        ),
                        html.P(
                            f"Período registrado: {DashboardConfig.AÑO_MIN}-{DashboardConfig.AÑO_MAX}",
                            className="lead pt-3",
                            style=DashboardConfig.SUBTITLE_STYLE,
                        ),
                    ],
                ),
                xs=12,
                lg=6,
                className="mt-3 mb-1",
            ),
            # KPIs
            dbc.Col(
                dbc.Row(
                    [
                        create_kpi_card(
                            "Total incendios", f"{len(fuegos)}", "kpi-total"
                        ),
                        create_kpi_card(
                            "Área quemada", superficie_formateada(fuegos), "kpi-area"
                        ),
                        create_kpi_card("Año pico", f"{año_pico}", "kpi-año-pico"),
                        create_kpi_card(
                            "Tendencia", tendencia_incendios(fuegos), "kpi-tendencia"
                        ),
                    ]
                ),
                xs=12,
                lg=6,
            ),
        ],
    )


def _build_main_charts() -> dbc.Row:
    """
    Construye la fila de gráficos principales.

    :return: Fila de Dash con gráficos principales
    """
    return dbc.Row(
        className="mb-4",
        children=[
            dbc.Col(
                create_graph_card(
                    card_id="grafico-mapa",
                    header_text="Superficie total afectada por incendios por provincia",
                    graph_id="graph-mapa",
                    figure=mapa_incendios_por_provincia(
                        data_df=fuegos,
                        provincias_df=provincias_df,
                        ccaa=ccaa,
                    ),
                ),
                xs=12,
                lg=6,
                className="mb-3",
            ),
            dbc.Col(
                create_graph_card(
                    card_id="grafico-mediaanual",
                    header_text="Media anual de superficie afectada por incendios",
                    graph_id="graph-barras",
                    figure=grafico_barras_comparativas(fuegos),
                ),
                xs=12,
                lg=6,
                className="mb-3",
            ),
        ],
    )


def _build_secondary_charts() -> dbc.Row:
    """
    Construye la fila de gráficos secundarios.

    :return: Fila de Dash con gráficos secundarios
    """
    polar_switch = dbc.Switch(
        id="toggle-polar-distribucion",
        label="Vista Polar",
        value=True,
        className="mt-2",
        style={"fontSize": "0.9rem"},
    )

    return dbc.Row(
        className="mb-4",
        children=[
            dbc.Col(
                create_graph_card(
                    card_id="grafico-causas",
                    header_text="Evolución de las causas de incendios",
                    graph_id="graph-causas",
                    figure=grafico_causas_por_año(fuegos),
                    graph_style={"height": "400px"},
                ),
                xs=12,
                lg=6,
                className="mb-3",
            ),
            dbc.Col(
                create_graph_card(
                    card_id="grafico-distribucion",
                    header_text="Distribución de la superficie afectada por incendios mes a mes",
                    graph_id="graph-distribucion",
                    figure=grafico_distribucion_superficie_incendios(
                        fuegos, polar=True
                    ),
                    graph_config={"displayModeBar": False},
                    header_extra=[polar_switch],
                ),
                xs=12,
                lg=6,
                className="mb-3",
            ),
        ],
    )


def _build_controls_and_footer() -> dbc.Row:
    """
    Construye la fila de controles y créditos.

    :return: Fila de Dash con controles y créditos
    """
    return dbc.Row(
        className="mb-1",
        children=[
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        dbc.Row(
                            [
                                _build_year_slider(),
                                _build_ccaa_dropdown(),
                                _build_causa_dropdown(),
                                _build_filter_button(),
                            ]
                        )
                    )
                ),
                xs=12,
                lg=10,
            ),
            dbc.Col(
                html.Div(
                    className="h-100 d-flex flex-column justify-content-center border rounded p-2 bg-light",
                    children=[
                        html.P(
                            "Visualización Avanzada de Datos\n(MAADM-ETSISI/UPM)",
                            className="mb-0 fw-bold",
                            style={"fontSize": "0.9rem", "textAlign": "right"},
                        ),
                        html.P(
                            "👨🏻‍💻 Yago Boleas Francisco",
                            className="mb-0 text-muted",
                            style={"fontSize": "0.6rem", "textAlign": "right"},
                        ),
                    ],
                ),
                xs=12,
                lg=2,
            ),
        ],
    )


def _build_year_slider() -> dbc.Col:
    """
    Construye el control de rango de años.

    :return: Columna de Dash con el slider de años
    """
    return dbc.Col(
        children=[
            html.Label("Rango de Años"),
            dcc.RangeSlider(
                id="slider-años",
                min=DashboardConfig.AÑO_MIN,
                max=DashboardConfig.AÑO_MAX,
                step=1,
                value=[DashboardConfig.AÑO_MIN, DashboardConfig.AÑO_MAX],
                marks={
                    DashboardConfig.AÑO_MIN: str(DashboardConfig.AÑO_MIN),
                    DashboardConfig.AÑO_MAX: str(DashboardConfig.AÑO_MAX),
                },
                tooltip={"placement": "bottom"},
            ),
        ],
        xs=12,
        md=4,
    )


def _build_ccaa_dropdown() -> dbc.Col:
    """
    Construye el dropdown de comunidades autónomas.

    :return: Columna de Dash con el dropdown de CCAA
    """
    return dbc.Col(
        children=[
            html.Label("Comunidad Autónoma"),
            dcc.Dropdown(
                id="dropdown-ccaa",
                options=DashboardConfig.CCAA_OPTIONS,
                placeholder="Selecciona CCAA",
                style={"color": "black", "fontWeight": "500"},
            ),
        ],
        xs=12,
        md=3,
    )


def _build_causa_dropdown() -> dbc.Col:
    """
    Construye el dropdown de causas.

    :return: Columna de Dash con el dropdown de causas
    """
    return dbc.Col(
        children=[
            html.Label("Causa(s)"),
            dcc.Dropdown(
                id="dropdown-causas",
                options=[
                    {"label": causa, "value": label} for label, causa in CAUSAS.items()
                ],
                placeholder="Causas posibles",
                multi=True,
                style={"color": "black", "fontWeight": "500"},
            ),
        ],
        xs=12,
        md=3,
    )


def _build_filter_button() -> dbc.Col:
    """
    Construye el botón de filtros.

    :return: Columna de Dash con el botón de filtrar
    """
    return dbc.Col(
        dbc.Row(
            [
                html.Label("Filtro"),
                dbc.Button(
                    id="btn-filtrar",
                    children="Activar filtros",
                    color="primary",
                    className="w-100",
                ),
            ]
        ),
        xs=12,
        md=2,
        className="d-flex align-items-end",
    )


# Inicialización de la app
app = dash.Dash(
    __name__,
    external_stylesheets=DashboardConfig.EXTERNAL_STYLESHEETS,
)

app.layout = build_layout()


@app.callback(
    [
        Output("graph-mapa", "figure"),
        Output("graph-barras", "figure"),
        Output("graph-causas", "figure"),
        Output("graph-distribucion", "figure"),
        Output("kpi-total", "children"),
        Output("kpi-area", "children"),
        Output("kpi-año-pico", "children"),
        Output("kpi-tendencia", "children"),
    ],
    [
        Input("btn-filtrar", "n_clicks"),
        Input("toggle-polar-distribucion", "value"),
    ],
    [
        State("slider-años", "value"),
        State("dropdown-ccaa", "value"),
        State("dropdown-causas", "value"),
    ],
    prevent_initial_call=False,
)
def actualizar_dashboard(
    n_clicks: int | None,
    polar: bool,
    rango_años: list[int],
    ccaa_seleccionada: str | None,
    causas_seleccionadas: list[int] | None,
) -> tuple:
    """
    Actualiza todos los gráficos y KPIs basándose en los filtros seleccionados.

    :param n_clicks: Número de veces que se ha pulsado el botón de filtrar
    :param polar: Si el gráfico de distribución debe ser polar
    :param rango_años: Rango de años seleccionado
    :param ccaa_seleccionada: Comunidad autónoma seleccionada
    :param causas_seleccionadas: Lista de causas seleccionadas
    :return: Tupla con todas las figuras actualizadas y valores de KPIs
    """
    fuegos_filtrado = fuegos

    if rango_años:
        fuegos_filtrado = fuegos_filtrado.filter(
            pl.col("año").is_between(min(rango_años), max(rango_años))
        )

    if ccaa_seleccionada:
        fuegos_filtrado = fuegos_filtrado.filter(
            pl.col("comunidad") == ccaa_seleccionada
        )

    if causas_seleccionadas:
        causas_texto = [CAUSAS[causa] for causa in causas_seleccionadas]
        fuegos_filtrado = fuegos_filtrado.filter(pl.col("causa").is_in(causas_texto))

    fig_mapa = mapa_incendios_por_provincia(
        data_df=fuegos,
        provincias_df=provincias_df,
        ccaa=ccaa,
        focus=ccaa_seleccionada,
    )

    fig_barras = grafico_barras_comparativas(fuegos_filtrado)
    fig_causas = grafico_causas_por_año(fuegos_filtrado)
    fig_distribucion = grafico_distribucion_superficie_incendios(
        fuegos_filtrado, polar=polar
    )

    total_incendios = f"{len(fuegos_filtrado)}"
    area_quemada = superficie_formateada(fuegos_filtrado)

    año_pico = "N/A"
    if len(fuegos_filtrado) > 0:
        año_pico = (
            fuegos_filtrado.group_by("año")
            .agg(pl.col("superficie").sum())
            .sort("superficie", descending=True)
            .item(0, "año")
        )

    tendencia = tendencia_incendios(fuegos_filtrado)

    return (
        fig_mapa,
        fig_barras,
        fig_causas,
        fig_distribucion,
        total_incendios,
        area_quemada,
        f"{año_pico}",
        f"{tendencia}",
    )


if __name__ == "__main__":
    app.run(debug=True)
