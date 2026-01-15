import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

from plots import *
from processing import ccaa, fuegos, provincias_df

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container(
    fluid=True,
    style={
        "backgroundColor": "#352e2c",
        "color": "white",
        "minHeight": "100vh",
        "padding": "1rem",
    },
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label(
                                        "Seleccionar comunidad autónoma para ver sus grandes incendios"
                                    ),
                                    dcc.Dropdown(
                                        id="desplegable-ccaa",
                                        options=provincias_df.CCAA.unique().tolist(),
                                        value=None,
                                        style={
                                            "color": "black",
                                        },
                                    ),
                                ],
                            ),
                            className="mb-3",
                            style={"border": "1px solid #FF4500"},
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                dcc.Graph(
                                    id="mapa-incendios",
                                    figure=mapa_incendios_por_provincia(
                                        data_df=fuegos,
                                        provincias_df=provincias_df,
                                        ccaa=ccaa,
                                    ),
                                    config={"displayModeBar": False},
                                ),
                            ),
                            style={
                                "height": "calc(90vh - 120px)",
                                "border": "1px solid #FF4500",
                            },
                        ),
                    ],
                    width=4,
                    className="h-100",
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            dcc.Graph(
                                                id="grafico1",
                                                figure=grafico_causas_por_año(fuegos),
                                            ),
                                        ),
                                        style={"border": "1px dashed #FFD700"},
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            dcc.Graph(
                                                id="grafico2",
                                                figure=grafico_barras_comparativas(
                                                    fuegos
                                                ),
                                            ),
                                        ),
                                        style={"border": "1px dashed #FFD700"},
                                    ),
                                    width=6,
                                ),
                            ],
                            className="mb-3",
                            style={"height": "50%"},
                        ),
                        # dbc.Row(
                        #     [
                        #         dbc.Col(
                        #             dbc.Card(
                        #                 dbc.CardBody(
                        #                     dcc.Graph(
                        #                         id="grafico3",
                        #                         figure=px.scatter(title="Gráfico 3"),
                        #                     ),
                        #                 ),
                        #                 style={"border": "1px dashed #FFD700"},
                        #             ),
                        #             width=6,
                        #         ),
                        #         dbc.Col(
                        #             dbc.Card(
                        #                 dbc.CardBody(
                        #                     dcc.Graph(
                        #                         id="grafico4",
                        #                         figure=px.scatter(title="Gráfico 4"),
                        #                     ),
                        #                 ),
                        #                 style={"border": "1px dashed #FFD700"},
                        #             ),
                        #             width=6,
                        #         ),
                        #     ],
                        #     style={"height": "50%"},
                        # ),
                    ],
                    width=8,
                    style={"height": "90vh"},
                ),
            ],
            style={"height": "90vh", "border": "1px solid #FFFFFF"},
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.P(
                            "Visualización Avanzada de Datos (MAADM-ETSISI/UPM)",
                            className="mb-0",
                            style={"fontSize": "0.8rem", "fontWeight": "bold"},
                        ),
                        html.P(
                            "Yago Boleas Francisco",
                            className="mb-0",
                            style={"fontSize": "0.8rem", "fontWeight": "bold"},
                        ),
                    ],
                    style={"textAlign": "right", "marginTop": "10px"},
                ),
                width=12,
            ),
            style={"alignSelf": "flex-end", "width": "100%"},
        ),
    ],
)


@app.callback(
    Output("mapa-incendios", "figure"),
    Input("desplegable-ccaa", "value"),
)
def actualizar_mapa(seleccion):
    nueva_figura = mapa_incendios_por_provincia(
        data_df=fuegos,
        provincias_df=provincias_df,
        ccaa=ccaa,
        focus=seleccion,
    )
    return nueva_figura


if __name__ == "__main__":
    app.run(debug=True)
