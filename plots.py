"""Módulo de generación de gráficos para el dashboard de incendios."""

from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from scipy.stats import gaussian_kde

from utils import CAUSA_EMOJI, MESES

if TYPE_CHECKING:
    from typing import Any


# Constantes de configuración
class PlotConfig:
    """Configuración de estilos para los gráficos."""

    # Colores para causas
    COLORES_CAUSAS = ["#8B0000", "#FF4500", "#FF8C00", "#FFD700", "#FFFACD", "#708090"]

    # Configuración de layout común
    BASE_LAYOUT = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "white"},
    }

    # Configuración de ejes
    AXIS_CONFIG = {
        "title_font": {"color": "white"},
        "tickfont": {"color": "white"},
        "showgrid": False,
    }

    # Umbral para grandes incendios
    UMBRAL_GRANDE_INCENDIO = 500
    UMBRAL_KDE_SUPERFICIE = 20


def mapa_incendios_por_provincia(
    data_df: pl.DataFrame,
    provincias_df: gpd.GeoDataFrame,
    focus: str | None = None,
    ccaa: gpd.GeoDataFrame | None = None,
) -> go.Figure:
    """
    Genera un mapa coroplético de España mostrando la superficie afectada por incendios.

    :param data_df: DataFrame con los datos de incendios
    :param provincias_df: GeoDataFrame con las geometrías de las provincias
    :param focus: Nombre de la CCAA para hacer zoom (opcional)
    :param ccaa: GeoDataFrame con las geometrías de las comunidades autónomas (opcional)
    :return: Figura de Plotly con el mapa coroplético
    :raises ValueError: Si focus no existe en los datos
    """
    # Agregar datos por provincia
    agg_df = data_df.group_by("provincia").agg(
        pl.sum("superficie").alias("superficie_total")
    )

    # Crear mapa base
    fig = px.choropleth(
        agg_df,
        locations="provincia",
        geojson=provincias_df,
        featureidkey="properties.Texto_Alt",
        color="superficie_total",
        scope="europe",
        color_continuous_scale="Hot_r",
    )

    # Añadir líneas de CCAA si están disponibles
    if ccaa is not None:
        _add_ccaa_borders(fig, ccaa)

    # Configurar zoom y marcadores según focus
    if focus:
        _configure_focus_view(fig, focus, data_df, provincias_df)
    else:
        _configure_default_view(fig)

    # Aplicar configuración estética
    _configure_map_layout(fig)

    return fig


def _add_ccaa_borders(fig: go.Figure, ccaa: gpd.GeoDataFrame) -> None:
    """
    Añade las líneas de frontera de las CCAA al mapa.

    :param fig: Figura de Plotly donde añadir las fronteras
    :param ccaa: GeoDataFrame con las geometrías de las comunidades autónomas
    """
    ccaa_wgs84 = ccaa.to_crs(epsg=4326)

    for _, row in ccaa_wgs84.iterrows():
        geometry = row.geometry
        geoms = geometry.geoms if geometry.geom_type == "MultiPolygon" else [geometry]

        for geom in geoms:
            lon, lat = geom.exterior.xy
            fig.add_trace(
                go.Scattergeo(
                    lon=list(lon),
                    lat=list(lat),
                    mode="lines",
                    line={"color": "black", "width": 1.5},
                    name=row["CCAA"],
                    showlegend=False,
                )
            )


def _configure_focus_view(
    fig: go.Figure,
    focus: str,
    data_df: pl.DataFrame,
    provincias_df: gpd.GeoDataFrame,
) -> None:
    """
    Configura la vista con zoom en una CCAA específica.

    :param fig: Figura de Plotly a configurar
    :param focus: Nombre de la CCAA para hacer zoom
    :param data_df: DataFrame con los datos de incendios
    :param provincias_df: GeoDataFrame con las geometrías de las provincias
    """
    ccaa_data = provincias_df[provincias_df.CCAA == focus]
    centro_lon = float(ccaa_data.centro_ccaa_lon.iloc[0])
    centro_lat = float(ccaa_data.centro_ccaa_lat.iloc[0])

    fig.update_geos(
        projection_type="times",
        center={"lat": centro_lat, "lon": centro_lon},
        projection_scale=15,
        visible=False,
    )

    _add_fire_markers(fig, data_df, focus)


def _add_fire_markers(fig: go.Figure, data_df: pl.DataFrame, ccaa: str) -> None:
    """
    Añade marcadores para grandes incendios en una CCAA.

    :param fig: Figura de Plotly donde añadir los marcadores
    :param data_df: DataFrame con los datos de incendios
    :param ccaa: Nombre de la CCAA para filtrar los incendios
    """
    grandes_incendios = data_df.filter(
        (pl.col("superficie") >= PlotConfig.UMBRAL_GRANDE_INCENDIO)
        & (pl.col("comunidad") == ccaa)
    ).with_columns(
        marker_size=pl.col("superficie").log1p() ** 1.2,
        hover_text=pl.format(
            "<b>Incendio:</b><br>Fecha: {}<br>Municipio: {}<br>Superficie: {} ha",
            pl.col("fecha").cast(pl.Utf8),
            pl.col("municipio"),
            pl.col("superficie"),
        ),
    )

    if grandes_incendios.height == 0:
        return

    fig.add_scattergeo(
        lon=grandes_incendios["lng"],
        lat=grandes_incendios["lat"],
        mode="text",
        text=[CAUSA_EMOJI[causa] for causa in grandes_incendios["causa"].to_list()],
        textposition="middle center",
        textfont={"size": grandes_incendios["marker_size"]},
        marker={
            "size": 0,
            "color": "blue",
            "opacity": 1,
            "line": {"width": 1, "color": "black"},
        },
        hoverinfo="text",
        hovertext=grandes_incendios["hover_text"],
        showlegend=False,
    )

    _add_fire_markers_legend(fig, ccaa)


def _add_fire_markers_legend(fig: go.Figure, ccaa: str) -> None:
    """
    Añade título y leyenda para los marcadores de incendios.

    :param fig: Figura de Plotly donde añadir la leyenda
    :param ccaa: Nombre de la CCAA para el título
    """
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.85,
        text=(
            f'<span style="color: white; font-weight: bold; '
            f'text-shadow: 1px 1px 0 black, -1px -1px 0 black, 1px -1px 0 black, -1px 1px 0 black;">'
            f"Grandes incendios en «{ccaa}» (≥ {PlotConfig.UMBRAL_GRANDE_INCENDIO} ha)</span>"
        ),
        showarrow=False,
        font={"size": 14, "family": "sans-serif", "color": "white"},
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
        text=f"<b>Causa del incendio</b><br><br>{leyenda_causas}",
        showarrow=False,
        font={"size": 12, "color": "white"},
        bgcolor="rgba(0, 0, 0, 0.6)",
        bordercolor="white",
        borderwidth=1,
    )


def _configure_default_view(fig: go.Figure) -> None:
    """
    Configura la vista por defecto centrada en España.

    :param fig: Figura de Plotly a configurar
    """
    fig.update_geos(
        center={"lat": 40.4167, "lon": -3.7033},
        projection_scale=6.4,
        visible=False,
        projection_type="times",
    )


def _configure_map_layout(fig: go.Figure) -> None:
    """
    Aplica la configuración de layout al mapa.

    :param fig: Figura de Plotly a configurar
    """
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar={
            "title": "Superficie<br>quemada",
            "title_font_color": "white",
            "tickfont_color": "white",
            "ticks": "outside",
            "ticklen": 5,
            "thicknessmode": "pixels",
            "thickness": 20,
            "lenmode": "fraction",
            "len": 0.9,
            "yanchor": "middle",
            "y": 0.45,
            "xanchor": "left",
            "x": 0,
            "orientation": "v",
            "bgcolor": "rgba(0,0,0,0.3)",
        },
        geo_bgcolor="rgba(0,0,0,0)",
        **PlotConfig.BASE_LAYOUT,
    )


def grafico_causas_por_año(fuegos_df: pl.DataFrame) -> go.Figure:
    """
    Genera un gráfico de áreas apiladas mostrando la evolución de causas de incendios.
    Para un solo año, muestra barras horizontales apiladas.

    :param fuegos_df: DataFrame con los datos de incendios
    :return: Figura de Plotly con el gráfico
    """
    if fuegos_df.height == 0:
        return _crear_grafico_vacio("No hay datos para mostrar")

    agg = _calcular_porcentajes_causas(fuegos_df)

    causas_ordenadas = (
        agg.group_by("causa")
        .agg(pl.mean("porcentaje").alias("media"))
        .sort("media", descending=True)
        .get_column("causa")
        .to_list()
    )

    años_unicos = agg.get_column("año").unique().sort().to_list()

    # Caso especial: un solo año
    if len(años_unicos) == 1:
        return _grafico_causas_un_año(
            agg, causas_ordenadas, PlotConfig.COLORES_CAUSAS, años_unicos[0]
        )

    return _grafico_causas_multiples_años(agg, causas_ordenadas, años_unicos)


def _calcular_porcentajes_causas(fuegos_df: pl.DataFrame) -> pl.DataFrame:
    """
    Calcula los porcentajes de cada causa por año.

    :param fuegos_df: DataFrame con los datos de incendios
    :return: DataFrame con columnas 'año', 'causa', 'num_incendios', 'porcentaje'
    """
    agg = (
        fuegos_df.group_by(["año", "causa"])
        .agg(pl.len().alias("num_incendios"))
        .sort(["año", "causa"])
    )

    return agg.join(
        agg.group_by("año").agg(pl.sum("num_incendios").alias("total_anual")),
        on="año",
    ).with_columns(
        (pl.col("num_incendios") / pl.col("total_anual") * 100).alias("porcentaje")
    )


def _grafico_causas_multiples_años(
    agg: pl.DataFrame,
    causas_ordenadas: list[str],
    años_unicos: list[int],
) -> go.Figure:
    """
    Crea el gráfico de áreas apiladas para múltiples años.

    :param agg: DataFrame con los datos agregados
    :param causas_ordenadas: Lista de causas ordenadas
    :param años_unicos: Lista de años únicos
    :return: Figura de Plotly con el gráfico
    """
    fig = go.Figure()
    ultimo_año = agg.get_column("año").max()
    etiquetas_data = []

    for i, causa in enumerate(causas_ordenadas):
        df_causa = agg.filter(pl.col("causa") == causa)
        color_causa = PlotConfig.COLORES_CAUSAS[i % len(PlotConfig.COLORES_CAUSAS)]

        fig.add_trace(
            go.Scatter(
                x=df_causa.get_column("año").to_list(),
                y=df_causa.get_column("porcentaje").to_list(),
                mode="lines+markers",
                line={"width": 0.6, "color": color_causa},
                marker={"size": 2, "symbol": "circle", "color": color_causa},
                stackgroup="one",
                name=str(causa),
                hovertemplate="<b>%{x}</b><br>%{y:.2f}% (%{text} incendios)",
                text=df_causa.get_column("num_incendios").to_list(),
            )
        )

        # Posición para etiqueta
        ultimo_y = etiquetas_data[-1]["y_max"] if etiquetas_data else 0
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
            textangle=60,
            font={"color": etiqueta["color"], "size": 8},
        )

    fig.update_layout(
        showlegend=False,
        xaxis={
            "type": "category",
            "tickmode": "array",
            "tickvals": años_unicos[::3],
            "ticks": "outside",
            "ticklen": 5,
            "tickcolor": "white",
            "tickwidth": 1,
            **PlotConfig.AXIS_CONFIG,
        },
        yaxis={
            "range": [0, 100],
            "ticksuffix": "%",
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.1)",
            **PlotConfig.AXIS_CONFIG,
        },
        **PlotConfig.BASE_LAYOUT,
        margin={"t": 40},
        autosize=True,
    )

    return fig


def _grafico_causas_un_año(
    agg: pl.DataFrame,
    causas_ordenadas: list[str],
    colores: list[str],
    año: int,
) -> go.Figure:
    """
    Crea un gráfico de barras horizontales para un solo año.

    :param agg: DataFrame con los datos agregados
    :param causas_ordenadas: Lista de causas ordenadas
    :param colores: Lista de colores para las causas
    :param año: Año específico
    :return: Figura de Plotly con el gráfico
    """
    fig = go.Figure()

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
                marker={
                    "color": color_causa,
                    "line": {"color": "rgba(0,0,0,0.3)", "width": 1},
                },
                hovertemplate=(
                    f"<b>{causa}</b><br>{porcentaje:.1f}% "
                    f"({num_incendios} incendios)<extra></extra>"
                ),
                text=f"{causa}<br>{porcentaje:.1f}%",
                textposition="inside",
                textfont={"color": "white", "size": 10, "family": "Arial Black"},
                insidetextanchor="middle",
            )
        )

    fig.update_layout(
        barmode="stack",
        showlegend=False,
        xaxis={
            "range": [0, 100],
            "ticksuffix": "%",
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.1)",
            **PlotConfig.AXIS_CONFIG,
        },
        yaxis={"title": "Año", **PlotConfig.AXIS_CONFIG},
        **PlotConfig.BASE_LAYOUT,
        margin={"l": 80, "r": 40, "t": 40, "b": 60},
        height=200,
    )

    return fig


def grafico_barras_comparativas(fuegos_df: pl.DataFrame) -> go.Figure:
    """
    Genera un gráfico de barras horizontales comparando regiones.
    Muestra top 10 CCAA si hay múltiples, o todas las provincias si solo hay una CCAA.

    :param fuegos_df: DataFrame con los datos de incendios
    :return: Figura de Plotly con el gráfico de barras
    """
    if fuegos_df.height == 0:
        return _crear_grafico_vacio("No hay datos para mostrar")

    n_years = fuegos_df.select(pl.col("año").n_unique().alias("n")).item(0, "n")

    # Se muestran comunidades o provincias
    if fuegos_df.get_column("comunidad").n_unique() == 1:
        comunidad_nombre = fuegos_df.get_column("comunidad").unique()[0]
        return _grafico_provincias(fuegos_df, n_years, comunidad_nombre)

    return _grafico_comunidades(fuegos_df, n_years)


def _crear_grafico_vacio(mensaje: str) -> go.Figure:
    """
    Crea un gráfico vacío con un mensaje.

    :param mensaje: Mensaje a mostrar en el gráfico
    :return: Figura de Plotly con el mensaje
    """
    fig = go.Figure()

    fig.add_annotation(
        text=mensaje,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 14, "color": "white"},
    )

    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        **PlotConfig.BASE_LAYOUT,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=400,
    )

    return fig


def _grafico_comunidades(fuegos_df: pl.DataFrame, n_years: int) -> go.Figure:
    """
    Genera gráfico de barras para el top 10 de comunidades autónomas.

    :param fuegos_df: DataFrame con los datos de incendios
    :param n_years: Número de años en el periodo
    :return: Figura de Plotly con el gráfico
    """
    agg = _agregar_datos_regionales(fuegos_df, "comunidad", n_years)

    if agg.height == 0:
        return _crear_grafico_vacio("No hay datos para mostrar")

    # Limitar a top 10
    agg = agg.head(10)

    return _crear_grafico_barras_horizontal(
        agg,
        campo_region="comunidad",
        titulo_porcentaje="nacional",
    )


def _grafico_provincias(
    fuegos_df: pl.DataFrame,
    n_years: int,
    comunidad_nombre: str,
) -> go.Figure:
    """
    Genera gráfico de barras para las provincias de una comunidad.

    :param fuegos_df: DataFrame con los datos de incendios
    :param n_years: Número de años en el periodo
    :param comunidad_nombre: Nombre de la comunidad autónoma
    :return: Figura de Plotly con el gráfico
    """
    agg = _agregar_datos_regionales(fuegos_df, "provincia", n_years)

    if agg.height == 0:
        return _crear_grafico_vacio(f"No hay datos para {comunidad_nombre}")

    return _crear_grafico_barras_horizontal(
        agg,
        campo_region="provincia",
        titulo_porcentaje=comunidad_nombre,
    )


def _agregar_datos_regionales(
    fuegos_df: pl.DataFrame,
    campo: str,
    n_years: int,
) -> pl.DataFrame:
    """
    Agrega datos por región calculando medias anuales.

    :param fuegos_df: DataFrame con los datos de incendios
    :param campo: Campo por el que agregar ('comunidad' o 'provincia')
    :param n_years: Número de años en el periodo
    :return: DataFrame con columnas agregadas
    """
    agg = fuegos_df.group_by(campo).agg(
        [
            pl.len().alias("cantidad"),
            pl.col("superficie").sum().alias("superficie_total"),
        ]
    )

    if agg.height == 0:
        return agg

    total_superficie = agg.select(pl.col("superficie_total").sum().alias("total")).item(
        0, "total"
    )

    return agg.with_columns(
        (pl.col("cantidad") / n_years).alias("media_anual_cantidad"),
        (pl.col("superficie_total") / n_years).alias("media_anual_superficie"),
        (pl.col("superficie_total") / total_superficie * 100).alias("pct_sobre_total"),
    ).sort("media_anual_superficie", descending=True)


def _crear_grafico_barras_horizontal(
    agg: pl.DataFrame,
    campo_region: str,
    titulo_porcentaje: str,
) -> go.Figure:
    """
    Crea el gráfico de barras horizontales con los datos agregados.

    :param agg: DataFrame con los datos agregados
    :param campo_region: Nombre del campo de región ('comunidad' o 'provincia')
    :param titulo_porcentaje: Texto para el título del porcentaje
    :return: Figura de Plotly con el gráfico
    """
    regiones = agg.get_column(campo_region).to_list()
    x_superficie = agg.get_column("media_anual_superficie").to_list()
    media_cantidad = agg.get_column("media_anual_cantidad").to_list()
    pct_total = agg.get_column("pct_sobre_total").to_list()
    superficie_tot = agg.get_column("superficie_total").to_list()
    cantidad_tot = agg.get_column("cantidad").to_list()

    media_regional = sum(x_superficie) / len(x_superficie) if x_superficie else 0

    fig = go.Figure()

    # Barras
    fig.add_trace(
        go.Bar(
            x=x_superficie,
            y=list(range(len(regiones))),
            orientation="h",
            marker={"color": x_superficie, "colorscale": "Hot_r"},
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Media anual de superficie quemada: %{x:.1f} ha<br>"
                "Media anual de cantidad de incendios: %{customdata[1]:.2f} incendios/año<br>"
                "Total del periodo: %{customdata[2]:.0f} ha en %{customdata[3]:.0f} incendios<br>"
                f"Porcentaje sobre superficie {titulo_porcentaje}: %{{customdata[4]:.2f}}%<extra></extra>"
            ),
            customdata=list(
                zip(regiones, media_cantidad, superficie_tot, cantidad_tot, pct_total)
            ),
        )
    )

    # Línea de media
    if len(x_superficie) > 1 and media_regional > 0:
        fig.add_vline(
            x=media_regional,
            line={"color": "white", "dash": "dash"},
            annotation_text=f"Media: {media_regional:.1f} ha/año",
            annotation_position="bottom left",
            annotation_font={"color": "white", "size": 10},
        )

    # Etiquetas de regiones
    for i, region in enumerate(regiones):
        fig.add_annotation(
            xref="paper",
            x=1.02,
            y=i,
            text=region,
            showarrow=False,
            xanchor="left",
            xshift=-10,
            font={"size": 8, "color": "white"},
            align="right",
        )

    # Estadísticas adicionales
    for i, (xi, mc, pct) in enumerate(zip(x_superficie, media_cantidad, pct_total)):
        fig.add_annotation(
            x=max(100, xi * 1.2),
            y=i,
            text=f"{mc:.1f} / {pct:.1f}%",
            showarrow=False,
            xanchor="left",
            font={"size": 8, "color": "#AAAAAA"},
            valign="middle",
        )

    fig.update_layout(
        xaxis={"autorange": "reversed", "range": [0, max(x_superficie)]},
        yaxis={"autorange": "reversed", "showticklabels": False},
        showlegend=False,
        margin={"l": 0, "r": 100, "t": 70, "b": 40},
        **PlotConfig.BASE_LAYOUT,
        autosize=True,
    )

    return fig


def grafico_distribucion_superficie_incendios(
    fuegos_df: pl.DataFrame,
    polar: bool = False,
) -> go.Figure:
    """
    Genera un gráfico de distribución de superficie de incendios por semana usando KDE.
    Solo considera incendios > 20 ha para la visualización.

    :param fuegos_df: DataFrame con los datos de incendios
    :param polar: Si True, crea gráfico polar; si False, cartesiano
    :return: Figura de Plotly con el gráfico de distribución
    """
    if fuegos_df.height == 0:
        return _crear_grafico_vacio("No hay datos de incendios disponibles")

    fuegos_df = fuegos_df.filter(
        pl.col("superficie") > PlotConfig.UMBRAL_KDE_SUPERFICIE
    )

    if fuegos_df.height == 0:
        return _crear_grafico_vacio(
            f"No hay incendios con superficie > {PlotConfig.UMBRAL_KDE_SUPERFICIE} ha"
        )

    kde_matrix, x_grid, semanas = _calcular_kde(fuegos_df)

    if kde_matrix is None:
        return _crear_grafico_vacio("Datos insuficientes para generar la distribución")

    if polar:
        return _crear_grafico_polar_kde(kde_matrix, x_grid, semanas)

    return _crear_grafico_cartesiano_kde(kde_matrix, x_grid, semanas)


def _calcular_kde(
    fuegos_df: pl.DataFrame,
) -> tuple[np.ndarray | None, np.ndarray, np.ndarray]:
    """
    Calcula la matriz KDE para cada semana del año.

    :param fuegos_df: DataFrame con los datos de incendios
    :return: Tupla con (kde_matrix, x_grid, semanas)
    """
    # Se agrega por semana
    agg = fuegos_df.group_by("semana").agg(pl.col("superficie")).sort("semana")

    semanas = agg["semana"].to_numpy()
    n_semanas = len(semanas)

    if n_semanas < 3:
        return None, np.array([]), semanas

    # Se crea grid de superficie
    todas_superficies = fuegos_df["superficie"].to_numpy()
    superficie_max = min(np.percentile(todas_superficies, 99), 1000)
    superficie_max = max(superficie_max, 100)

    x_grid = np.linspace(0, superficie_max, 500)
    kde_matrix = np.zeros((2 * n_semanas, len(x_grid)))

    # Se calcula KDE para cada semana
    for i, vals in enumerate(agg["superficie"]):
        data = np.asanyarray(vals)

        if data.size == 0:
            continue

        media = np.mean(data)

        if data.size > 1:
            try:
                kde = gaussian_kde(data)
                kde_matrix[i * 2, :] = kde(x_grid) * media
            except Exception:
                kde_matrix[i * 2, :] = np.zeros_like(x_grid)
        else:
            # Un solo punto: pico en ese valor
            idx_cercano = np.argmin(np.abs(x_grid - data.item()))
            kde_matrix[i * 2, idx_cercano] = media

    # Se interpola entre semanas
    kde_matrix[1::2, :] = (
        kde_matrix[0::2, :] + np.vstack([kde_matrix[2::2, :], kde_matrix[0:1, :]])
    ) / 2

    # Se aplica una transformación de raíz cuadrada para mejorar visibilidad
    if np.any(kde_matrix > 0):
        np.sqrt(kde_matrix, out=kde_matrix)

    return kde_matrix, x_grid, semanas


def _crear_grafico_cartesiano_kde(
    kde_matrix: np.ndarray,
    x_grid: np.ndarray,
    semanas: np.ndarray,
) -> go.Figure:
    """
    Crea el gráfico cartesiano de la distribución KDE.

    :param kde_matrix: Matriz KDE
    :param x_grid: Grid de superficies
    :param semanas: Array de semanas
    :return: Figura de Plotly con el gráfico
    """
    fig = go.Figure(
        data=go.Heatmap(
            z=kde_matrix,
            x=x_grid,
            y=np.repeat(semanas, 2),
            colorscale="Hot",
            colorbar={
                "title": "Densidad KDE",
                "title_font": {"color": "white"},
                "tickfont": {"color": "white"},
                "thickness": 20,
            },
            hovertemplate=(
                "<b>Semana:</b> %{y:.0f}<br>"
                "<b>Superficie:</b> %{x:.0f} ha<br>"
                "<b>Densidad:</b> %{z:.4f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **PlotConfig.BASE_LAYOUT,
        margin={"t": 30, "b": 30, "l": 40, "r": 30},
        autosize=True,
    )
    fig.update_xaxes(
        title_text="Superficie (ha)",
        **PlotConfig.AXIS_CONFIG,
    )
    fig.update_yaxes(
        title_text="Semana",
        **PlotConfig.AXIS_CONFIG,
        range=[min(semanas) - 1, max(semanas) + 1],
    )

    return fig


def _crear_grafico_polar_kde(
    kde_matrix: np.ndarray,
    x_grid: np.ndarray,
    semanas: np.ndarray,
) -> go.Figure:
    """
    Crea el gráfico polar de la distribución KDE.

    :param kde_matrix: Matriz KDE
    :param x_grid: Grid de superficies
    :param semanas: Array de semanas
    :return: Figura de Plotly con el gráfico
    """
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

    sizes = _calcular_tamaños_marcadores(radius)

    fig = go.Figure(
        go.Scatterpolar(
            r=radius,
            theta=thetas,
            mode="markers",
            marker={
                "size": sizes,
                "color": intensities,
                "colorscale": "Hot",
                "line_width": 0,
                "opacity": 0.8,
            },
            customdata=hover,
            hovertemplate=(
                "<b>Semana:</b> %{customdata}<br>"
                "<b>Superficie:</b> %{r:.0f} ha<br>"
                "<b>Densidad:</b> %{marker.color:.4f}<extra></extra>"
            ),
        )
    )

    # Configuración de ejes polares
    meses_angles = np.linspace(0, 360, 12, endpoint=False)
    superficie_max = max(x_grid)

    fig.update_layout(
        **PlotConfig.BASE_LAYOUT,
        margin={"t": 30, "b": 30, "l": 40, "r": 30},
        height=400,
        width=None,
        autosize=True,
        showlegend=False,
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "angularaxis": {
                "tickmode": "array",
                "tickvals": meses_angles,
                "ticktext": MESES,
                "direction": "clockwise",
                "rotation": 90,
                "gridcolor": "rgba(255,255,255,0.1)",
                "tickfont": {"size": 12, "color": "white"},
            },
            "radialaxis": {
                "title": "Superficie (ha)",
                "title_font": {"size": 10},
                "tickfont": {"size": 9, "color": "rgba(255,255,255,0.6)"},
                "gridcolor": "rgba(255,255,255,0.05)",
                "angle": 45,
                "showline": False,
                "range": [0, superficie_max],
            },
        },
    )

    return fig


def _calcular_tamaños_marcadores(
    radius: list[float],
    max_size: float = 8,
    min_size: float = 0.1,
) -> np.ndarray:
    """
    Calcula los tamaños de los marcadores de forma dinámica.

    :param radius: Lista de valores de radio
    :param max_size: Tamaño máximo del marcador
    :param min_size: Tamaño mínimo del marcador
    :return: Array con los tamaños calculados
    """
    r_array = np.array(radius)
    r_min, r_max = r_array.min(), r_array.max()

    if r_max > r_min:
        return ((r_array - r_min) / (r_max - r_min)) ** 2 * (
            max_size - min_size
        ) + min_size

    return np.full_like(r_array, (max_size + min_size) / 2)
