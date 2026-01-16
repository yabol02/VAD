from dataclasses import dataclass
from typing import Optional

import polars as pl

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

def superficie_formateada(df: pl.DataFrame) -> str:
    """
    Calcula la suma de la superficie y devuelve un string formateado en Millones (M) o Miles (K).
    """
    total_ha = df.select(pl.col("superficie").sum()).item()

    if total_ha >= 1_000_000:
        texto = f">{total_ha / 1e6:.1f}M ha"
    else:
        texto = f">{total_ha / 1e3:.1f}K ha"

    return texto


def tendencia_incendios(df: pl.DataFrame) -> str:
    """
    Calcula la tendencia de incendios en función de los datos proporcionados.

    :param df: DataFrame con los datos de incendios
    :type df: polars.DataFrame
    :return: Tendencia de incendios ("Ascendente", "Descendente", "Estable" o "Sin datos previos")
    :rtype: str
    """
    df_counts = (
        df.group_by(["año", "mes"]).agg(pl.len().alias("n")).sort(["año", "mes"])
    )
    años_unicos = df_counts["año"].unique().sort()

    if len(años_unicos) >= 2:
        # Comparar último año completo (o actual) vs anterior
        val_actual = df_counts.filter(pl.col("año") == años_unicos[-1])["n"].sum()
        val_previo = df_counts.filter(pl.col("año") == años_unicos[-2])["n"].sum()
    else:
        # Si solo hay un año, comparar últimos 6 meses vs 6 anteriores, tomando los últimos 12 meses disponibles
        datos_recientes = df_counts.tail(12)
        val_actual = datos_recientes.tail(6)["n"].sum()
        val_previo = datos_recientes.head(6)["n"].sum()

    if val_previo == 0:
        return "Sin datos previos"

    diff_pct = (val_actual - val_previo) / val_previo

    if diff_pct > 0.05:
        return "Ascendente"
    elif diff_pct < -0.05:
        return "Descendente"
    else:
        return "Estable"


@dataclass
class CardStyle:
    font_size: str = "2rem"
    font_color: str = "#ffffff"
    bg_color: str = "#2c3e50"
    text_align: str = "center"
    font_weight: str = "bold"
    border_radius: str = "10px"
    padding: str = "1rem"
    shadow: str = "0 4px 6px rgba(0,0,0,0.1)"

    def to_dash(self):
        return {
            "fontSize": self.font_size,
            "color": self.font_color,
            "backgroundColor": self.bg_color,
            "textAlign": self.text_align,
            "fontWeight": self.font_weight,
            "borderRadius": self.border_radius,
            "padding": self.padding,
            "boxShadow": self.shadow,
        }
