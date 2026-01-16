import dash_bootstrap_components as dbc
import geopandas as gpd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from scipy.stats import gaussian_kde

from utils import CAUSA_EMOJI, MESES


def mapa_incendios_por_provincia(
    data_df: pl.DataFrame,
    provincias_df: gpd.GeoDataFrame,
    focus: str = None,
    ccaa: gpd.GeoDataFrame = None,
) -> go.Figure:
    """
    Genera un mapa coroplético de España mostrando la superficie afectada por incendios
    en cada provincia. Si se especifica una comunidad autónoma (CCAA), el mapa se centra en esa región
    y destaca los grandes incendios (superficie >= 500 ha) con marcadores.

    Comportamiento:
        - Si focus se pasa, el mapa se centra en la CCAA indicada y marca incendios
        grandes (superficie >= 500 ha). Si focus no existe en provincias_df
        o ccaa, se produce ValueError (índice vacío).
        - Usa escala de color en hectáreas; marcas de fuego usan la columna lng/lat.
        - No modifica los DataFrames de entrada.

    :param data_df: DataFrame con los datos de incendios
    :type data_df: pl.DataFrame
    :param provincias_df: GeoDataFrame con las características geográficas de las provincias
    :type provincias_df: gpd.GeoDataFrame
    :param focus: Nombre de la comunidad autónoma para centrar el mapa
    :type focus: str
    :param ccaa: GeoDataFrame con las características geográficas de las comunidades autónomas
    :type ccaa: gpd.GeoDataFrame
    :return: Figura de Plotly con el mapa coroplético
    :rtype: go.Figure
    """
    agg_df = data_df.group_by(["provincia"]).agg(
        [pl.sum("superficie").alias("superficie_total")]
    )

    fig = (
        px.choropleth(
            agg_df,
            locations="provincia",
            geojson=provincias_df,
            featureidkey="properties.Texto_Alt",
            color="superficie_total",
            scope="europe",
            # hover_data=...,  # TODO: Añadir alguna cosilla interesante
            color_continuous_scale="Hot_r",
        )
        # .add_scattergeo(
        #     lon=provincias["centro_ccaa_lon"],
        #     lat=provincias["centro_ccaa_lat"],
        #     text=provincias["CCAA"],
        #     mode="markers+text",
        #     textposition="top center",
        #     marker=dict(size=5, color="white", line=dict(width=1, color="black")),
        #     name="Centro de provincia",
        # )
    )

    # Líneas de las CCAA
    for _, row in ccaa.to_crs(epsg=4326).iterrows():
        geometry = row.geometry
        for g in geometry.geoms if geometry.geom_type == "MultiPolygon" else [geometry]:
            lon, lat = g.exterior.xy
            fig.add_trace(
                go.Scattergeo(
                    lon=list(lon),
                    lat=list(lat),
                    mode="lines",
                    line=dict(color="black", width=1.5),
                    name=row["CCAA"],
                    showlegend=False,
                )
            )

    # Enfoque/Zoom en la CCAA seleccionada
    if focus:
        centro_lon = float(
            provincias_df[provincias_df.CCAA == focus].centro_ccaa_lon.iloc[0]
        )
        centro_lat = float(
            provincias_df[provincias_df.CCAA == focus].centro_ccaa_lat.iloc[0]
        )
        fig.update_geos(
            projection_type="times",
            center={"lat": centro_lat, "lon": centro_lon},
            projection_scale=15,
            visible=False,
        )
        grandes_incendios = data_df.filter(
            (pl.col("superficie") >= 500) & (pl.col("comunidad") == focus)
        ).with_columns(
            marker_size=pl.col("superficie").log1p() ** 1.2,
            hover_text=pl.format(
                "<b>Incendio:</b><br>Fecha: {}<br>Municipio: {}<br>Superficie: {} ha",
                pl.col("fecha").cast(pl.Utf8),
                pl.col("municipio"),
                pl.col("superficie"),
            ),
        )

        fig.add_scattergeo(
            lon=grandes_incendios["lng"],
            lat=grandes_incendios["lat"],
            mode="text",
            text=[CAUSA_EMOJI[causa] for causa in grandes_incendios["causa"].to_list()],
            textposition="middle center",
            textfont=dict(size=grandes_incendios["marker_size"]),
            marker=dict(
                size=0, color="blue", opacity=1, line=dict(width=1, color="black")
            ),
            hoverinfo="text",
            hovertext=grandes_incendios["hover_text"],
            showlegend=False,
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.85,
            text=(
                f'<span style="color: white; font-weight: bold; '
                f'text-shadow: 1px 1px 0 black, -1px -1px 0 black, 1px -1px 0 black, -1px 1px 0 black;">'
                f"Grandes incendios en «{focus}» (≥ 500 ha)</span>"
            ),
            showarrow=False,
            font=dict(size=14, family="sans-serif", color="white"),
        )
        leyenda_causas = "<br>".join(
            f"{emoji} {causa}" for causa, emoji in CAUSA_EMOJI.items()
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=1.0,
            y=0.8,
            align="left",
            text=("<b>Causa del incendio</b><br><br>" f"{leyenda_causas}"),
            showarrow=False,
            font=dict(size=12, color="white"),
            bgcolor="rgba(0, 0, 0, 0.6)",
            bordercolor="white",
            borderwidth=1,
        )

    else:
        fig.update_geos(
            center={"lat": 40.4167, "lon": -3.7033},
            projection_scale=6.4,
            visible=False,
            projection_type="times",
        )

    # Configuración de leyenda y estética de la figura
    fig.update_layout(
        margin=dict(r=0, t=0, l=0, b=0),
        coloraxis_colorbar=dict(
            # Título de la leyenda
            title="Superficie<br>quemada",
            title_font_color="white",
            # Unidades de la leyenda
            tickfont_color="white",
            ticks="outside",
            ticklen=5,
            # Grosor de la barra de la leyenda
            thicknessmode="pixels",
            thickness=20,
            # Ajuste de longitud de la barra de la leyenda
            lenmode="fraction",
            len=0.9,
            # Posicionamiento de la leyenda
            yanchor="middle",
            y=0.45,
            xanchor="left",
            x=0,
            orientation="v",  # Orientación de la leyenda
            bgcolor="rgba(0,0,0,0.3)",  # Fondo de la leyenda
        ),
        geo_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def grafico_causas_por_año(fuegos_df: pl.DataFrame) -> go.Figure:
    """
    Genera un gráfico de áreas apiladas que muestra la evolución porcentual
    de las causas de incendios a lo largo de los años.

    Si solo hay un año, muestra un gráfico de barras apiladas horizontales.

    Comportamiento:
        - Agrupa por ('año','causa'), cuenta incendios y calcula el porcentaje relativo al total anual
            (suma por año = 100% salvo datos faltantes).
        - Ordena las causas por su media porcentual y asigna colores cíclicamente desde la paleta interna.
        - Añade etiquetas junto al último año (o dentro de las barras si es un solo año).

    :param fuegos_df: DataFrame que contiene los datos de incendios
    :type fuegos_df: pl.DataFrame
    :return: Figura de Plotly con el gráfico de áreas apiladas o barras
    :rtype: go.Figure
    """
    agg = (
        fuegos_df.group_by(["año", "causa"])
        .agg(pl.len().alias("num_incendios"))
        .sort(["año", "causa"])
    )

    agg = agg.join(
        agg.group_by("año").agg(pl.sum("num_incendios").alias("total_anual")), on="año"
    ).with_columns(
        (pl.col("num_incendios") / pl.col("total_anual") * 100).alias("porcentaje")
    )

    causas_ordenadas = (
        agg.group_by("causa")
        .agg(pl.mean("porcentaje").alias("media"))
        .sort("media", descending=True)
        .get_column("causa")
        .to_list()
    )

    colores = ["#8B0000", "#FF4500", "#FF8C00", "#FFD700", "#FFFACD", "#708090"]

    años_unicos = agg.get_column("año").unique().sort().to_list()
    if len(años_unicos) == 1:
        return _grafico_causas_un_año(agg, causas_ordenadas, colores, años_unicos[0])

    ultimo_año = agg.get_column("año").max()
    etiquetas_data = []

    fig = go.Figure()

    for i, causa in enumerate(causas_ordenadas):
        df_causa = agg.filter(pl.col("causa") == causa)
        x_vals = df_causa.get_column("año").to_list()
        y_vals = df_causa.get_column("porcentaje").to_list()
        n_vals = df_causa.get_column("num_incendios").to_list()
        color_causa = colores[i % len(colores)]

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers",
                line=dict(width=0.6, color=color_causa),
                marker=dict(size=2, symbol="circle", color=color_causa),
                stackgroup="one",
                name=str(causa),
                hovertemplate="<b>%{x}</b><br>%{y:.2f}% (%{text} incendios)",
                text=n_vals,
            )
        )

        ultimo_y = etiquetas_data[-1]["y_max"] if len(etiquetas_data) else 0
        causa_y = df_causa.filter(pl.col("año") == ultimo_año).get_column("porcentaje")

        etiquetas_data.append(
            {
                "causa": str(causa),
                "y_max": ultimo_y + (causa_y.item() if not causa_y.is_empty() else 0),
                "y_pos": ultimo_y
                + (causa_y.item() / 2 if not causa_y.is_empty() else 0),
                "color": color_causa,
            }
        )

    for etiqueta in etiquetas_data:
        fig.add_annotation(
            xref="paper",
            x=1,
            y=etiqueta["y_pos"],
            text=etiqueta["causa"],
            showarrow=False,
            xanchor="left",
            xshift=0,
            textangle=60,
            font=dict(color=etiqueta["color"], size=8),
        )

    fig.update_layout(
        showlegend=False,
        legend_title_text="Causa",
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=8),
            orientation="v",
            x=1.02,
            y=1,
            xanchor="left",
            yanchor="top",
        ),
        xaxis=dict(
            type="category",
            showgrid=False,
            tickmode="array",
            ticks="outside",
            tickvals=[a for a in años_unicos][::3],
            title_font=dict(size=10, color="white"),
            tickfont=dict(color="white"),
            ticklen=5,
            tickcolor="white",
            tickwidth=1,
        ),
        yaxis=dict(
            range=[0, 100],
            ticksuffix="%",
            title_font=dict(size=14, color="white"),
            tickfont=dict(color="white"),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.1)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40),
        height=None,
        autosize=True,
    )

    return fig


def _grafico_causas_un_año(
    agg: pl.DataFrame, causas_ordenadas: list, colores: list, año: int
) -> go.Figure:
    """
    Crea un gráfico de barras horizontales apiladas para un solo año.

    Únicamente se utiliza cuando el DataFrame contiene datos de un solo año para
    representar la distribución porcentual de las causas de incendios.

    :param agg: DataFrame agregado con datos de incendios
    :type agg: pl.DataFrame
    :param causas_ordenadas: Lista de causas ordenadas por frecuencia
    :type causas_ordenadas: list
    :param colores: Lista de colores para las causas
    :type colores: list
    :param año: El año único presente en los datos
    :type año: int
    :return: Figura de Plotly con barras horizontales apiladas
    :rtype: go.Figure
    """
    fig = go.Figure()

    posicion_acumulada = 0

    for i, causa in enumerate(causas_ordenadas):
        df_causa = agg.filter(pl.col("causa") == causa)

        if df_causa.height == 0:
            continue

        porcentaje = df_causa.get_column("porcentaje").item()
        num_incendios = df_causa.get_column("num_incendios").item()
        color_causa = colores[i % len(colores)]

        fig.add_trace(
            go.Bar(
                x=[porcentaje],
                y=[str(año)],
                orientation="h",
                name=str(causa),
                marker=dict(
                    color=color_causa, line=dict(color="rgba(0,0,0,0.3)", width=1)
                ),
                hovertemplate=f"<b>{causa}</b><br>{porcentaje:.1f}% ({num_incendios} incendios)<extra></extra>",
                text=f"{causa}<br>{porcentaje:.1f}%",
                textposition="inside",
                textfont=dict(color="white", size=10, family="Arial Black"),
                insidetextanchor="middle",
            )
        )

        posicion_acumulada += porcentaje

    fig.update_layout(
        barmode="stack",
        showlegend=False,
        xaxis=dict(
            range=[0, 100],
            ticksuffix="%",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.1)",
            title_font=dict(size=12, color="white"),
            tickfont=dict(color="white", size=10),
        ),
        yaxis=dict(
            title="Año",
            showgrid=False,
            title_font=dict(size=12, color="white"),
            tickfont=dict(color="white", size=12),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=80, r=40, t=40, b=60),
        height=200,
    )

    return fig


def grafico_barras_comparativas(fuegos_df: pl.DataFrame) -> go.Figure:
    """
    Genera un gráfico de barras horizontales comparando regiones por superficie quemada.

    Comportamiento adaptativo:
      - Si hay múltiples comunidades: se muestra un top 10 de comunidades autónomas
      - Si hay una sola comunidad: se muestran todas las provincias de esa comunidad

    Calcula:
      - Número de años únicos y promedia la superficie y cantidad por año
      - Ordena por media anual de superficie
      - Añade línea vertical con la media y anotaciones

    :param fuegos_df: DataFrame que contiene los datos de incendios
    :type fuegos_df: pl.DataFrame
    :return: Figura de Plotly con el gráfico de barras
    :rtype: go.Figure
    """
    if fuegos_df.height == 0:
        return _grafico_vacio("No hay datos para mostrar")

    n_years = fuegos_df.select(pl.col("año").n_unique().alias("n")).get_column("n")[0]

    if fuegos_df.get_column("comunidad").n_unique() == 1:
        # Se muestran las provincias de la comunidad seleccionada
        comunidad_nombre = fuegos_df.get_column("comunidad").unique()[0]
        return _grafico_provincias(fuegos_df, n_years, comunidad_nombre)
    else:
        # Se muestra el top 10 de comunidades más afectadas
        return _grafico_comunidades(fuegos_df, n_years)


def _grafico_vacio(mensaje: str) -> go.Figure:
    """
    Genera un gráfico vacío con un mensaje centrado.

    :param mensaje: Mensaje a mostrar en el gráfico vacío
    :type mensaje: str
    :return: Figura de Plotly con el mensaje centrado
    :rtype: go.Figure
    """
    fig = go.Figure()

    fig.add_annotation(
        text=mensaje,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="white"),
    )

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
    )

    return fig


def _grafico_comunidades(fuegos_df: pl.DataFrame, n_years: int) -> go.Figure:
    """
    Genera gráfico de barras para el top 10 de comunidades autónomas.

    :param fuegos_df: DataFrame que contiene los datos de incendios
    :type fuegos_df: pl.DataFrame
    :param n_years: Número de años únicos en el DataFrame
    :type n_years: int
    :return: Figura de Plotly con el gráfico de barras
    :rtype: go.Figure
    """
    agg = fuegos_df.group_by("comunidad").agg(
        [
            pl.len().alias("cantidad"),
            pl.col("superficie").sum().alias("superficie_total"),
        ]
    )

    if agg.height == 0:
        return _grafico_vacio("No hay datos para mostrar")

    total_superficie_nacional = agg.select(
        pl.col("superficie_total").sum().alias("total")
    ).get_column("total")[0]

    agg = (
        agg.with_columns(
            (pl.col("cantidad") / n_years).alias("media_anual_cantidad"),
            (pl.col("superficie_total") / n_years).alias("media_anual_superficie"),
            (pl.col("superficie_total") / total_superficie_nacional * 100).alias(
                "pct_sobre_nacional"
            ),
        )
        .sort("media_anual_superficie", descending=True)
        .head(10)
    )

    regiones = agg.get_column("comunidad").to_list()
    x_superficie = agg.get_column("media_anual_superficie").to_list()
    media_cantidad = agg.get_column("media_anual_cantidad").to_list()
    pct_nacional = agg.get_column("pct_sobre_nacional").to_list()
    superficie_tot = agg.get_column("superficie_total").to_list()
    cantidad_tot = agg.get_column("cantidad").to_list()

    media_nacional = (
        sum(x_superficie) / len(x_superficie) if len(x_superficie) > 0 else 0
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=x_superficie,
            y=list(range(len(regiones))),
            orientation="h",
            marker=dict(
                color=x_superficie,
                colorscale="Hot_r",
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Media anual de superficie quemada: %{x:.1f} ha<br>"
                "Media anual de cantidad de incendios: %{customdata[1]:.2f} incendios/año<br>"
                "Total del periodo: %{customdata[2]:.0f} ha en %{customdata[3]:.0f} incendios<br>"
                "Porcentaje sobre superficie nacional: %{customdata[4]:.2f}%<extra></extra>"
            ),
            customdata=list(
                zip(
                    regiones,
                    media_cantidad,
                    superficie_tot,
                    cantidad_tot,
                    pct_nacional,
                )
            ),
        )
    )

    if len(x_superficie) > 1 and media_nacional > 0:
        fig.add_vline(
            x=media_nacional,
            line=dict(color="white", dash="dash"),
            annotation_text=f"Media del top 10: {media_nacional:.1f} ha/año",
            annotation_position="bottom left",
            annotation_font=dict(color="white", size=10),
        )

    for i, region in enumerate(regiones):
        fig.add_annotation(
            xref="paper",
            x=1.02,
            y=i,
            text=region,
            showarrow=False,
            xanchor="left",
            xshift=-10,
            font=dict(size=8, color="white"),
            align="right",
        )

    for i, (xi, mc, pct) in enumerate(zip(x_superficie, media_cantidad, pct_nacional)):
        fig.add_annotation(
            x=max(100, xi * 1.2),
            y=i,
            text=f"{mc:.1f} / {pct:.1f}%",
            showarrow=False,
            xanchor="left",
            font=dict(size=8, color="#AAAAAA"),
            valign="middle",
        )

    fig.update_layout(
        xaxis=dict(autorange="reversed"),
        yaxis=dict(autorange="reversed", showticklabels=False),
        showlegend=False,
        margin=dict(l=0, r=100, t=70, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=None,
        autosize=True,
    )

    fig.update_xaxes(range=[0, max(x_superficie)])

    return fig


def _grafico_provincias(
    fuegos_df: pl.DataFrame, n_years: int, comunidad_nombre: str
) -> go.Figure:
    """
    Genera gráfico de barras para las provincias de una comunidad autónoma.

    :param fuegos_df: DataFrame que contiene los datos de incendios
    :type fuegos_df: pl.DataFrame
    :param n_years: Número de años únicos en el DataFrame
    :type n_years: int
    :param comunidad_nombre: Nombre de la comunidad autónoma
    :type comunidad_nombre: str
    :return: Figura de Plotly con el gráfico de barras
    :rtype: go.Figure
    """
    agg = fuegos_df.group_by("provincia").agg(
        [
            pl.len().alias("cantidad"),
            pl.col("superficie").sum().alias("superficie_total"),
        ]
    )

    if agg.height == 0:
        return _grafico_vacio(f"No hay datos para {comunidad_nombre}")

    total_superficie_comunidad = agg.select(
        pl.col("superficie_total").sum().alias("total")
    ).get_column("total")[0]

    agg = agg.with_columns(
        (pl.col("cantidad") / n_years).alias("media_anual_cantidad"),
        (pl.col("superficie_total") / n_years).alias("media_anual_superficie"),
        (pl.col("superficie_total") / total_superficie_comunidad * 100).alias(
            "pct_sobre_comunidad"
        ),
    ).sort("media_anual_superficie", descending=True)

    provincias = agg.get_column("provincia").to_list()
    x_superficie = agg.get_column("media_anual_superficie").to_list()
    media_cantidad = agg.get_column("media_anual_cantidad").to_list()
    pct_comunidad = agg.get_column("pct_sobre_comunidad").to_list()
    superficie_tot = agg.get_column("superficie_total").to_list()
    cantidad_tot = agg.get_column("cantidad").to_list()

    media_comunidad = (
        sum(x_superficie) / len(x_superficie) if len(x_superficie) > 0 else 0
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=x_superficie,
            y=list(range(len(provincias))),
            orientation="h",
            marker=dict(
                color=x_superficie,
                colorscale="Hot_r",
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Media anual de superficie quemada: %{x:.1f} ha<br>"
                "Media anual de cantidad de incendios: %{customdata[1]:.2f} incendios/año<br>"
                "Total del periodo: %{customdata[2]:.0f} ha en %{customdata[3]:.0f} incendios<br>"
                f"Porcentaje sobre superficie de {comunidad_nombre}: %{{customdata[4]:.2f}}%<extra></extra>"
            ),
            customdata=list(
                zip(
                    provincias,
                    media_cantidad,
                    superficie_tot,
                    cantidad_tot,
                    pct_comunidad,
                )
            ),
        )
    )

    if len(provincias) > 1 and media_comunidad > 0:
        fig.add_vline(
            x=media_comunidad,
            line=dict(color="white", dash="dash"),
            annotation_text=f"Media de {comunidad_nombre}: {media_comunidad:.1f} ha/año",
            annotation_position="bottom left",
            annotation_font=dict(color="white", size=10),
        )

    for i, provincia in enumerate(provincias):
        fig.add_annotation(
            xref="paper",
            x=1.02,
            y=i,
            text=provincia,
            showarrow=False,
            xanchor="left",
            xshift=-10,
            font=dict(size=8, color="white"),
            align="right",
        )

    for i, (xi, mc, pct) in enumerate(zip(x_superficie, media_cantidad, pct_comunidad)):
        fig.add_annotation(
            x=max(100, xi * 1.2),
            y=i,
            text=f"{mc:.1f} / {pct:.1f}%",
            showarrow=False,
            xanchor="left",
            font=dict(size=8, color="#AAAAAA"),
            valign="middle",
        )

    fig.update_layout(
        xaxis=dict(autorange="reversed"),
        yaxis=dict(autorange="reversed", showticklabels=False),
        showlegend=False,
        margin=dict(l=0, r=100, t=70, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=None,
        autosize=True,
    )

    fig.update_xaxes(range=[0, max(x_superficie)])

    return fig


def grafico_ditribucion_superficie_incendios(
    fuegos_df: pl.DataFrame, polar: bool = False
) -> go.Figure:
    """
    Genera un gráfico que muestra la distribución de la superficie de incendios
    a lo largo de las semanas del año utilizando una estimación de densidad kernel (KDE).

    Para poder visualizar más cómodamente las distribuciones, se realiza el siguiente procesamiento de los datos:
        - Para calcular la densidad, solo se consideran incendios con superficie > 20 ha.
        - Se calcula la KDE para cada semana y se multiplica por la media de superficie de esa semana.
        - Se interpola la densidad entre semanas para suavizar la visualización.
        - Se aplica la raíz cuadrada a la matriz de densidades para mejorar la visibilidad de las áreas con baja densidad.

    Permite visualizarse en formato cartesiano o polar.

    :param fuegos_df: DataFrame que contiene los datos de incendios
    :type fuegos_df: pl.DataFrame
    :param polar: Indica si el gráfico debe ser en formato polar o cartesiano
    :type polar: bool
    :return: Figura generada
    :rtype: go.Figure
    """
    x_grid = np.linspace(0, 1000, 500)
    agg = (
        fuegos_df.filter(pl.col("superficie") > 20)
        .group_by("semana")
        .agg(pl.col("superficie"))
        .sort("semana")
    )

    semanas = agg["semana"].to_numpy()
    n_semanas = len(semanas)

    kde_matrix = np.zeros((2 * n_semanas, len(x_grid)))
    stats_list = np.empty((2 * n_semanas, 2))

    for i, vals in enumerate(agg["superficie"]):
        data = np.asanyarray(vals)
        media = np.mean(data) if data.size > 0 else data.item()
        stats_list[i * 2, 0] = media
        stats_list[i * 2, 1] = np.median(data) if data.size > 0 else data.item()
        kde = gaussian_kde(data)
        kde_matrix[i * 2, :] = kde(x_grid) * media

    kde_matrix[1::2, :] = (
        kde_matrix[0::2, :] + np.vstack([kde_matrix[2::2, :], kde_matrix[0:1, :]])
    ) / 2
    np.sqrt(kde_matrix, out=kde_matrix)

    base_layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(t=30, b=30, l=40, r=30),
        autosize=True,
    )

    if not polar:
        fig = go.Figure(
            data=go.Heatmap(
                z=kde_matrix,
                x=x_grid,
                y=semanas,
                colorscale="Hot",
                colorbar=dict(
                    title="Densidad KDE",
                    title_font=dict(color="white"),
                    tickfont=dict(color="white"),
                    thickness=20,
                ),
            )
        )

        fig.update_layout(**base_layout)
        fig.update_xaxes(
            title_text="Superficie (ha)",
            title_font=dict(color="white"),
            tickfont=dict(color="white"),
            showgrid=False,
        )
        fig.update_yaxes(
            title_text="Semana",
            title_font=dict(color="white"),
            tickfont=dict(color="white"),
            showgrid=False,
        )
    else:
        n = kde_matrix.shape[0]
        angles = np.linspace(0, 360, n, endpoint=False)

        thetas = []
        radius = []
        intensities = []
        hover = []

        for i, theta in enumerate(angles):
            sem_actual = semanas[i // 2] if i // 2 < len(semanas) else semanas[-1]
            for j, superficie in enumerate(x_grid):
                thetas.append(theta)
                radius.append(superficie)
                intensities.append(kde_matrix[i, j])
                hover.append(sem_actual)

        MAX_MARKER_SIZE = 8
        MIN_MARKER_SIZE = 0.1
        r_array = np.array(radius)
        r_min, r_max = r_array.min(), r_array.max()
        sizes = ((r_array - r_min) / (r_max - r_min + 1e-9)) ** 2 * (
            MAX_MARKER_SIZE - MIN_MARKER_SIZE
        ) + MIN_MARKER_SIZE

        fig = go.Figure(
            go.Scatterpolar(
                r=radius,
                theta=thetas,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=intensities,
                    colorscale="Hot",
                    line_width=0,
                    opacity=0.8,
                ),
                customdata=hover,
                hovertemplate=(
                    "<b>Semana:</b> %{customdata}<br>"
                    + "<b>Superficie:</b> %{r:.0f} ha<br>"
                    + "<b>Densidad:</b> %{color:.4f}<extra></extra>"
                ),
            )
        )
        meses_angles = np.linspace(0, 360, 12, endpoint=False)
        fig.update_layout(**base_layout)
        fig.update_layout(
            showlegend=False,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                angularaxis=dict(
                    tickmode="array",
                    tickvals=meses_angles,
                    ticktext=MESES,
                    direction="clockwise",
                    rotation=90,  # Enero arriba
                    gridcolor="rgba(255,255,255,0.1)",
                    tickfont=dict(size=12, color="white"),
                ),
                radialaxis=dict(
                    title="Superficie (ha)",
                    title_font=dict(size=10),
                    tickfont=dict(size=9, color="rgba(255,255,255,0.6)"),
                    gridcolor="rgba(255,255,255,0.05)",
                    angle=45,  # Inclina las etiquetas para que no se pisen con el eje N
                    showline=False,
                ),
            ),
        )

    return fig
