from dataclasses import dataclass
from typing import Optional

import polars as pl

COMUNIDADES = {
    1: "País Vasco",
    2: "Cataluña",
    3: "Galicia",
    4: "Andalucía",
    5: "Principado de Asturias",
    6: "Cantabria",
    7: "La Rioja",
    8: "Región de Murcia",
    9: "Comunitat Valenciana",
    10: "Aragón",
    11: "Castilla - La Mancha",
    12: "Canarias",
    13: "Comunidad Foral de Navarra",
    14: "Extremadura",
    15: "Illes Balears",
    16: "Comunidad de Madrid",
    17: "Castilla y León",
    18: "Ceuta",
    19: "Melilla",
}

PROVINCIAS = {
    1: "Araba",
    2: "Albacete",
    3: "Alacant",
    4: "Almería",
    5: "Ávila",
    6: "Badajoz",
    7: "Illes Balears",
    8: "Barcelona",
    9: "Burgos",
    10: "Cáceres",
    11: "Cádiz",
    12: "Castelló",
    13: "Ciudad Real",
    14: "Córdoba",
    15: "A Coruña",
    16: "Cuenca",
    17: "Girona",
    18: "Granada",
    19: "Guadalajara",
    20: "Gipuzcoa",
    21: "Huelva",
    22: "Huesca",
    23: "Jaén",
    24: "León",
    25: "Lleida",
    26: "La Rioja",
    27: "Lugo",
    28: "Madrid",
    29: "Málaga",
    30: "Murcia",
    31: "Navarra",
    32: "Ourense",
    33: "Asturias",
    34: "Palencia",
    35: "Las Palmas",
    36: "Pontevedra",
    37: "Salamanca",
    38: "Santa Cruz de Tenerife",
    39: "Cantabria",
    40: "Segovia",
    41: "Sevilla",
    42: "Soria",
    43: "Tarragona",
    44: "Teruel",
    45: "Toledo",
    46: "València",
    47: "Valladolid",
    48: "Bizkaia",
    49: "Zamora",
    50: "Zaragoza",
    51: "Ceuta",
    52: "Melilla",
}

CAUSAS = {
    1: "Por rayo",
    2: "Negligencia",
    3: "Accidente",
    4: "Intencionado",
    5: "De origen desconocido",
    6: "Reproducido",
}

CAUSA_EMOJI = {
    "Por rayo": " ⚡ ",
    "Negligencia": " 🚬 ",
    "Accidente": " 🛠️ ",
    "Intencionado": " 🔥 ",
    "De origen desconocido": " ❓ ",
    "Reproducido": " 🔁 ",
}

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
