import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import polars as pl
from dash import Input, Output, State, dcc, html

from plots import (grafico_barras_comparativas, grafico_causas_por_año,
                   grafico_ditribucion_superficie_incendios,
                   mapa_incendios_por_provincia)
from processing import CAUSAS, COMUNIDADES, ccaa, fuegos, provincias_df
from utils import CardStyle, superficie_formateada, tendencia_incendios

año_min = fuegos.select(pl.col("año")).min().item()
año_max = fuegos.select(pl.col("año")).max().item()
ccaa_options = [
    {"label": ccaa, "value": ccaa}
    for ccaa in sorted(provincias_df.CCAA.unique().tolist())
]

# Gráfico placeholder genérico
fig_polar = px.line_polar(
    r=[1, 2, 3, 4, 1],
    theta=[0, 90, 180, 270, 0],
    line_close=True,
    template="simple_white",
)

# Márgenes en figuras para que quepan bien en las cards
fig_polar.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=150)

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap",
    ],
)

app.layout = dbc.Container(
    id="contenedor-principal",
    children=[
        # --- FILA 1: Tí­tulo y KPIs ---
        dbc.Row(
            children=[
                dbc.Col(
                    id="contenedor-titulo",
                    children=[
                        html.Div(
                            id="titulo",
                            children=[
                                html.H2(
                                    f"PANEL DE CONTROL DE INCENDIOS EN ESPAÑA",
                                    className="display-4",
                                    style={
                                        "fontSize": "3.2rem",
                                        "fontWeight": "800",
                                        "fontFamily": "Montserrat, sans-serif",
                                        "color": "#FFFFFF",
                                        "marginBottom": "0",
                                        "letterSpacing": "1px",
                                    },
                                ),
                                html.P(
                                    f"Perí­odo registrado: {año_min}-{año_max}",
                                    className="lead pt-3",
                                    style={
                                        "color": "#666",
                                        "fontWeight": "400",
                                        "fontSize": "1.5rem",
                                    },
                                ),
                            ],
                            className="h-100 d-flex flex-column justify-content-center",
                        )
                    ],
                    xs=12,
                    lg=6,
                    className="mt-3 mb-1",
                ),
                dbc.Col(
                    id="contenedor-kpis",
                    children=[
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H3(
                                                    "Total incendios",
                                                    style={
                                                        "fontSize": "1rem",
                                                        "textAlign": "center",
                                                    },
                                                ),
                                                html.H2(
                                                    id="kpi-total",
                                                    children=f"{len(fuegos)}",
                                                    style={
                                                        "fontSize": "1.4rem",
                                                        "textAlign": "center",
                                                    },
                                                ),
                                            ]
                                        )
                                    ),
                                    width=6,
                                    md=3,
                                    className="mb-2",
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H3(
                                                    "Área quemada",
                                                    style={
                                                        "fontSize": "1rem",
                                                        "textAlign": "center",
                                                    },
                                                ),
                                                html.H2(
                                                    id="kpi-area",
                                                    children=superficie_formateada(
                                                        fuegos
                                                    ),
                                                    style={
                                                        "fontSize": "1.4rem",
                                                        "textAlign": "center",
                                                    },
                                                ),
                                            ]
                                        )
                                    ),
                                    width=6,
                                    md=3,
                                    className="mb-2",
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H3(
                                                    "Año pico",
                                                    style={
                                                        "fontSize": "1rem",
                                                        "textAlign": "center",
                                                    },
                                                ),
                                                html.H2(
                                                    id="kpi-año-pico",
                                                    children=f"{fuegos.group_by("año").agg(pl.col("superficie").sum()).sort("superficie", descending=True).item(0, "año")}",
                                                    style={
                                                        "fontSize": "1.4rem",
                                                        "textAlign": "center",
                                                    },
                                                ),
                                            ]
                                        )
                                    ),
                                    width=6,
                                    md=3,
                                    className="mb-2",
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H3(
                                                    "Tendencia",
                                                    style={
                                                        "fontSize": "1rem",
                                                        "textAlign": "center",
                                                    },
                                                ),
                                                html.H2(
                                                    id="kpi-tendencia",
                                                    children=f"{tendencia_incendios(fuegos)}",
                                                    style={
                                                        "fontSize": "1.4rem",
                                                        "textAlign": "center",
                                                    },
                                                ),
                                            ]
                                        )
                                    ),
                                    width=6,
                                    md=3,
                                    className="mb-2",
                                ),
                            ]
                        )
                    ],
                    xs=12,
                    lg=6,
                ),
            ],
            className="mb-4 align-items-center",
        ),
        # --- FILA 2: Gráficos principales ---
        dbc.Row(
            id="contenedor-graficos-1",
            children=[
                dbc.Col(
                    id="grafico-mapa",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Superficie total afectada por incendios por provincia",
                                    style={
                                        "textAlign": "center",
                                        "fontWeight": "600",
                                        "fontSize": "1.4rem",
                                    },
                                ),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="graph-mapa",
                                        figure=mapa_incendios_por_provincia(
                                            data_df=fuegos,
                                            provincias_df=provincias_df,
                                            ccaa=ccaa,
                                        ),
                                    )
                                ),
                            ]
                        )
                    ],
                    xs=12,
                    lg=6,
                    className="mb-3",
                ),
                dbc.Col(
                    id="grafico-mediaanual",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Media anual de superficie afectada por incendios",
                                    style={
                                        "textAlign": "center",
                                        "fontWeight": "600",
                                        "fontSize": "1.4rem",
                                    },
                                ),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="graph-barras",
                                        figure=grafico_barras_comparativas(fuegos),
                                    )
                                ),
                            ]
                        )
                    ],
                    xs=12,
                    lg=6,
                    className="mb-3",
                ),
            ],
            className="mb-4",
        ),
        # --- FILA 3: Gráficos secundarios ---
        dbc.Row(
            id="contenedor-graficos-2",
            children=[
                dbc.Col(
                    id="grafico-causas",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Evolución de las causas de incendios",
                                    style={
                                        "textAlign": "center",
                                        "fontWeight": "600",
                                        "fontSize": "1.4rem",
                                    },
                                ),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="graph-causas",
                                        figure=grafico_causas_por_año(fuegos),
                                        style={"height": "400px"},
                                    )
                                ),  # Forzamos altura para simular tamaño
                            ],
                            className="h-100",
                        )
                    ],
                    xs=12,
                    lg=6,
                    className="mb-3",
                ),
                dbc.Col(
                    id="grafico-distribucion",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Distribución de la superficie afectada por incendios mes a mes",
                                    style={
                                        "textAlign": "center",
                                        "fontWeight": "600",
                                        "fontSize": "1.4rem",
                                    },
                                ),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="graph-distribucion",
                                        figure=grafico_ditribucion_superficie_incendios(
                                            fuegos, polar=True
                                        ),
                                        config={"displayModeBar": False},
                                    )
                                ),
                            ],
                            className="mb-3",
                        ),
                    ],
                    xs=12,
                    lg=6,
                    className="mb-3",
                ),
            ],
            className="mb-4",
        ),
        # --- FILA 4: Pie del dashboard ---
        dbc.Row(
            id="contenedor-pie",
            children=[
                dbc.Col(
                    id="selectores",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    id="seleccion-años",
                                                    children=[
                                                        html.Label("Rango de Años"),
                                                        dcc.RangeSlider(
                                                            id="slider-años",
                                                            min=año_min,
                                                            max=año_max,
                                                            step=1,
                                                            value=[año_min, año_max],
                                                            marks={
                                                                año_min: str(año_min),
                                                                año_max: str(año_max),
                                                            },
                                                            tooltip={
                                                                "placement": "bottom"
                                                            },
                                                        ),
                                                    ],
                                                    xs=12,
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    id="seleccion-ccaa",
                                                    children=[
                                                        html.Label(
                                                            "Comunidad Autónoma"
                                                        ),
                                                        dcc.Dropdown(
                                                            id="dropdown-ccaa",
                                                            options=provincias_df.CCAA.unique().tolist(),
                                                            placeholder="Selecciona CCAA",
                                                            style={
                                                                "color": "black",
                                                                "fontWeight": "500",
                                                            },
                                                        ),
                                                    ],
                                                    xs=12,
                                                    md=3,
                                                ),
                                                dbc.Col(
                                                    id="seleccion-causa",
                                                    children=[
                                                        html.Label("Causa(s)"),
                                                        dcc.Dropdown(
                                                            id="dropdown-causas",
                                                            options=[
                                                                {
                                                                    "label": causa,
                                                                    "value": label,
                                                                }
                                                                for label, causa in CAUSAS.items()
                                                            ],
                                                            placeholder="Causas posibles",
                                                            multi=True,
                                                            style={
                                                                "color": "black",
                                                                "fontWeight": "500",
                                                            },
                                                        ),
                                                    ],
                                                    xs=12,
                                                    md=3,
                                                ),
                                                dbc.Col(
                                                    id="boton-activar-filtros",
                                                    children=dbc.Row(
                                                        children=[
                                                            html.Label("Filtro"),
                                                            dbc.Button(
                                                                id="btn-filtrar",
                                                                children="Activar filtros",
                                                                color="primary",
                                                                className="w-100",
                                                            ),
                                                            # dcc.Download(
                                                            #     id="download-component"
                                                            # ),
                                                        ]
                                                    ),
                                                    xs=12,
                                                    md=2,
                                                    className="d-flex align-items-end",
                                                ),
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ],
                    xs=12,
                    lg=10,
                ),
                dbc.Col(
                    id="creditos",
                    children=[
                        html.Div(
                            [
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
                            className="h-100 d-flex flex-column justify-content-center border rounded p-2 bg-light",
                        )
                    ],
                    xs=12,
                    lg=2,
                ),
            ],
            className="mb-1",
        ),
    ],
    style={"backgroundColor": "#252222"},
    fluid=True,
)


@app.callback(
    [
        Output("graph-mapa", "figure"),
        # Output("graph-barras", "figure"),
        Output("graph-causas", "figure"),
        # Output("graph-distribucion", "figure"),
        Output("kpi-total", "children"),
        Output("kpi-area", "children"),
        Output("kpi-año-pico", "children"),
        Output("kpi-tendencia", "children"),
    ],
    [Input("btn-filtrar", "n_clicks")],
    [
        State("slider-años", "value"),
        State("dropdown-ccaa", "value"),
        State("dropdown-causas", "value"),
    ],
    prevent_initial_call=False,
)
def actualizar_dashboard(n_clicks, rango_años, ccaa_seleccionada, causas_seleccionadas):
    # Crear copia del dataframe original
    fuegos_filtrado = fuegos

    # Filtro de rango de años
    if rango_años:
        fuegos_filtrado = fuegos_filtrado.filter(
            (pl.col("año") >= min(rango_años)) & (pl.col("año") <= max(rango_años))
        )

    # Filtro de comunidad autónoma
    if ccaa_seleccionada:
        fuegos_filtrado = fuegos_filtrado.filter(
            pl.col("comunidad")==ccaa_seleccionada
        )

    # Filtro de causas
    if causas_seleccionadas and len(causas_seleccionadas) > 0:
        causas_seleccionadas = [CAUSAS[causa] for causa in causas_seleccionadas]
        fuegos_filtrado = fuegos_filtrado.filter(
            pl.col("causa").is_in(causas_seleccionadas)
        )

    # Generación de los gráficos con los datos filtrados
    fig_mapa = mapa_incendios_por_provincia(
        data_df=fuegos,
        provincias_df=provincias_df,
        ccaa=ccaa,
        focus=ccaa_seleccionada,
    )

    # fig_barras = grafico_barras_comparativas(fuegos_filtrado)

    fig_causas = grafico_causas_por_año(fuegos_filtrado)

    # fig_distribucion = grafico_ditribucion_superficie_incendios(
    #     fuegos_filtrado, polar=True
    # )

    # Cálculo de los KPIs actualizados
    total_incendios = f"{len(fuegos_filtrado)}"
    area_quemada = superficie_formateada(fuegos_filtrado)

    if len(fuegos_filtrado) > 0:
        año_pico = (
            fuegos_filtrado.group_by("año")
            .agg(pl.col("superficie").sum())
            .sort("superficie", descending=True)
            .item(0, "año")
        )
    else:
        año_pico = "N/A"

    tendencia = tendencia_incendios(fuegos_filtrado)

    return (
        fig_mapa,
        # fig_barras,
        fig_causas,
        # fig_distribucion,
        total_incendios,
        area_quemada,
        f"{año_pico}",
        f"{tendencia}",
    )


if __name__ == "__main__":
    app.run(debug=True)
