import dash_bootstrap_components as dbc
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def mapa_incendios_por_provincia(
    data_df: pl.DataFrame, provincias_df: gpd.GeoDataFrame, focus: str = None, ccaa: gpd.GeoDataFrame = None
):
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
            title="<b>Superficie Total Afectada por Incendios por Provincia</b>",
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
            text="🔥",
            textposition="middle center",
            textfont=dict(size=grandes_incendios["marker_size"]),
            marker=dict(
                size=0, color="blue", opacity=1, line=dict(width=1, color="black")
            ),
            hoverinfo="text",
            hovertext=grandes_incendios["hover_text"],
            showlegend=False,
        )
    else:
        fig.update_geos(fitbounds="locations", visible=False, projection_type="times")

    fig.update_layout(
        margin=dict(r=0, t=50, l=0, b=0),
        coloraxis_colorbar=dict(
            title="Superficie (ha)",
            thicknessmode="pixels",
            thickness=20,
            lenmode="pixels",
            len=500,
            yanchor="top",
            y=0.95,
            xanchor="center",
            x=0.5,
            orientation="h",
        ),
        geo_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def grafico_causas_por_año(fuegos_df: pl.DataFrame):

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
        title="<b>Evolución de las causas de incendios</b>",
        title_font=dict(size=18, color="white"),
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
            # title="Año",
            type="category",
            showgrid=False,
            tickmode="array",
            ticks="outside",
            tickvals=[a for a in agg.get_column("año").unique().sort().to_list()][::3],
            title_font=dict(size=10, color="white"),
            tickfont=dict(color="white"),
            ticklen=5,
            tickcolor="white",
            tickwidth=1,
        ),
        yaxis=dict(
            # title="Porcentaje de incendios",
            range=[0, 100],
            ticksuffix="%",
            title_font=dict(size=14, color="white"),
            tickfont=dict(color="white"),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.1)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            t=40,
        ),
    )

    return fig


def grafico_barras_comparativas(fuegos_df: pl.DataFrame):
    n_years = fuegos_df.select(pl.col("año").n_unique().alias("n")).get_column("n")[0]
    agg = fuegos_df.group_by("comunidad").agg(
        [
            pl.len().alias("cantidad"),
            pl.col("superficie").sum().alias("superficie_total"),
        ]
    )

    total_superficie_nacional = agg.select(
        pl.col("superficie_total").sum().alias("total")
    ).get_column("total")[0]

    agg = agg.with_columns(
        (pl.col("cantidad") / n_years).alias("media_anual_cantidad"),
        (pl.col("superficie_total") / n_years).alias("media_anual_superficie"),
        (pl.col("superficie_total") / total_superficie_nacional * 100).alias(
            "pct_sobre_nacional"
        ),
    ).sort("media_anual_superficie", descending=True)

    comunidades = agg.get_column("comunidad").to_list()
    x_superficie = agg.get_column("media_anual_superficie").to_list()
    media_cantidad = agg.get_column("media_anual_cantidad").to_list()
    pct_nacional = agg.get_column("pct_sobre_nacional").to_list()
    superficie_tot = agg.get_column("superficie_total").to_list()
    cantidad_tot = agg.get_column("cantidad").to_list()
    media_nacional = sum(x_superficie) / len(x_superficie)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=x_superficie,
            y=list(range(len(comunidades))),
            orientation="h",
            marker=dict(
                color=x_superficie,
                colorscale="Hot_r",
                # showscale=True,
                # colorbar=dict(title="Ha/año"),
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
                    comunidades,
                    media_cantidad,
                    superficie_tot,
                    cantidad_tot,
                    pct_nacional,
                )
            ),
        )
    ).add_vline(
        x=media_nacional,
        line=dict(color="white", dash="dash"),
        annotation_text=f"Media nacional: {media_nacional:.1f} ha/año",
        annotation_position="bottom left",
        annotation_font=dict(color="white", size=10),
    )

    for i, comunidad in enumerate(comunidades):
        fig.add_annotation(
            xref="paper",
            x=0.85,
            y=i,
            text=comunidad,
            showarrow=False,
            xanchor="left",
            xshift=10,
            font=dict(size=10, color="white"),
            align="left",
        )

    for i, (xi, comunidad, mc, pct) in enumerate(
        zip(x_superficie, comunidades, media_cantidad, pct_nacional)
    ):
        fig.add_annotation(
            x=xi + 7.5e3,
            y=i,
            text=f"{mc:.1f} / {pct:.1f}%",
            showarrow=False,
            xanchor="left",
            # xshift=6,
            font=dict(size=9, color="white"),
            valign="middle",
        )

    fig.update_layout(
        title="<b>Media anual de superficie afectada por incendios</b>",
        xaxis=dict(autorange="reversed"),
        yaxis=dict(autorange="reversed", showticklabels=False),
        showlegend=False,
        margin=dict(l=0, r=30, t=70, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        # autosize=True,
        # height=900,
    )

    return fig