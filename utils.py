"""Utilidades y constantes para el dashboard de incendios forestales."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

import polars as pl


class ComunidadAutonoma(IntEnum):
    """Códigos de comunidades autónomas españolas."""

    PAIS_VASCO = 1
    CATALUÑA = 2
    GALICIA = 3
    ANDALUCIA = 4
    ASTURIAS = 5
    CANTABRIA = 6
    LA_RIOJA = 7
    MURCIA = 8
    VALENCIA = 9
    ARAGON = 10
    CASTILLA_LA_MANCHA = 11
    CANARIAS = 12
    NAVARRA = 13
    EXTREMADURA = 14
    BALEARES = 15
    MADRID = 16
    CASTILLA_LEON = 17
    CEUTA = 18
    MELILLA = 19


class Provincia(IntEnum):
    """Códigos de provincias españolas."""

    ARABA = 1
    ALBACETE = 2
    ALACANT = 3
    ALMERIA = 4
    AVILA = 5
    BADAJOZ = 6
    BALEARES = 7
    BARCELONA = 8
    BURGOS = 9
    CACERES = 10
    CADIZ = 11
    CASTELLON = 12
    CIUDAD_REAL = 13
    CORDOBA = 14
    A_CORUÑA = 15
    CUENCA = 16
    GIRONA = 17
    GRANADA = 18
    GUADALAJARA = 19
    GIPUZCOA = 20
    HUELVA = 21
    HUESCA = 22
    JAEN = 23
    LEON = 24
    LLEIDA = 25
    LA_RIOJA = 26
    LUGO = 27
    MADRID = 28
    MALAGA = 29
    MURCIA = 30
    NAVARRA = 31
    OURENSE = 32
    ASTURIAS = 33
    PALENCIA = 34
    LAS_PALMAS = 35
    PONTEVEDRA = 36
    SALAMANCA = 37
    SANTA_CRUZ = 38
    CANTABRIA = 39
    SEGOVIA = 40
    SEVILLA = 41
    SORIA = 42
    TARRAGONA = 43
    TERUEL = 44
    TOLEDO = 45
    VALENCIA = 46
    VALLADOLID = 47
    BIZKAIA = 48
    ZAMORA = 49
    ZARAGOZA = 50
    CEUTA = 51
    MELILLA = 52


class CausaIncendio(IntEnum):
    """Códigos de causas de incendios."""

    RAYO = 1
    NEGLIGENCIA = 2
    ACCIDENTE = 3
    INTENCIONADO = 4
    DESCONOCIDO = 5
    REPRODUCIDO = 6


# Mapeos de códigos a nombres legibles
COMUNIDADES: dict[int, str] = {
    ComunidadAutonoma.PAIS_VASCO: "País Vasco",
    ComunidadAutonoma.CATALUÑA: "Cataluña",
    ComunidadAutonoma.GALICIA: "Galicia",
    ComunidadAutonoma.ANDALUCIA: "Andalucía",
    ComunidadAutonoma.ASTURIAS: "Principado de Asturias",
    ComunidadAutonoma.CANTABRIA: "Cantabria",
    ComunidadAutonoma.LA_RIOJA: "La Rioja",
    ComunidadAutonoma.MURCIA: "Región de Murcia",
    ComunidadAutonoma.VALENCIA: "Comunitat Valenciana",
    ComunidadAutonoma.ARAGON: "Aragón",
    ComunidadAutonoma.CASTILLA_LA_MANCHA: "Castilla - La Mancha",
    ComunidadAutonoma.CANARIAS: "Canarias",
    ComunidadAutonoma.NAVARRA: "Comunidad Foral de Navarra",
    ComunidadAutonoma.EXTREMADURA: "Extremadura",
    ComunidadAutonoma.BALEARES: "Illes Balears",
    ComunidadAutonoma.MADRID: "Comunidad de Madrid",
    ComunidadAutonoma.CASTILLA_LEON: "Castilla y León",
    ComunidadAutonoma.CEUTA: "Ceuta",
    ComunidadAutonoma.MELILLA: "Melilla",
}

PROVINCIAS: dict[int, str] = {
    Provincia.ARABA: "Araba",
    Provincia.ALBACETE: "Albacete",
    Provincia.ALACANT: "Alacant",
    Provincia.ALMERIA: "Almería",
    Provincia.AVILA: "Ávila",
    Provincia.BADAJOZ: "Badajoz",
    Provincia.BALEARES: "Illes Balears",
    Provincia.BARCELONA: "Barcelona",
    Provincia.BURGOS: "Burgos",
    Provincia.CACERES: "Cáceres",
    Provincia.CADIZ: "Cádiz",
    Provincia.CASTELLON: "Castelló",
    Provincia.CIUDAD_REAL: "Ciudad Real",
    Provincia.CORDOBA: "Córdoba",
    Provincia.A_CORUÑA: "A Coruña",
    Provincia.CUENCA: "Cuenca",
    Provincia.GIRONA: "Girona",
    Provincia.GRANADA: "Granada",
    Provincia.GUADALAJARA: "Guadalajara",
    Provincia.GIPUZCOA: "Gipuzcoa",
    Provincia.HUELVA: "Huelva",
    Provincia.HUESCA: "Huesca",
    Provincia.JAEN: "Jaén",
    Provincia.LEON: "León",
    Provincia.LLEIDA: "Lleida",
    Provincia.LA_RIOJA: "La Rioja",
    Provincia.LUGO: "Lugo",
    Provincia.MADRID: "Madrid",
    Provincia.MALAGA: "Málaga",
    Provincia.MURCIA: "Murcia",
    Provincia.NAVARRA: "Navarra",
    Provincia.OURENSE: "Ourense",
    Provincia.ASTURIAS: "Asturias",
    Provincia.PALENCIA: "Palencia",
    Provincia.LAS_PALMAS: "Las Palmas",
    Provincia.PONTEVEDRA: "Pontevedra",
    Provincia.SALAMANCA: "Salamanca",
    Provincia.SANTA_CRUZ: "Santa Cruz de Tenerife",
    Provincia.CANTABRIA: "Cantabria",
    Provincia.SEGOVIA: "Segovia",
    Provincia.SEVILLA: "Sevilla",
    Provincia.SORIA: "Soria",
    Provincia.TARRAGONA: "Tarragona",
    Provincia.TERUEL: "Teruel",
    Provincia.TOLEDO: "Toledo",
    Provincia.VALENCIA: "València",
    Provincia.VALLADOLID: "Valladolid",
    Provincia.BIZKAIA: "Bizkaia",
    Provincia.ZAMORA: "Zamora",
    Provincia.ZARAGOZA: "Zaragoza",
    Provincia.CEUTA: "Ceuta",
    Provincia.MELILLA: "Melilla",
}

CAUSAS: dict[int, str] = {
    CausaIncendio.RAYO: "Por rayo",
    CausaIncendio.NEGLIGENCIA: "Negligencia",
    CausaIncendio.ACCIDENTE: "Accidente",
    CausaIncendio.INTENCIONADO: "Intencionado",
    CausaIncendio.DESCONOCIDO: "De origen desconocido",
    CausaIncendio.REPRODUCIDO: "Reproducido",
}

CAUSA_EMOJI: dict[str, str] = {
    "Por rayo": " ⚡ ",
    "Negligencia": " 🚬 ",
    "Accidente": " 🛠️ ",
    "Intencionado": " 🔥 ",
    "De origen desconocido": " ❓ ",
    "Reproducido": " 🔁 ",
}

MESES: list[str] = [
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
]


class UnidadSuperficie:
    """Umbrales para formateo de superficie."""

    MILLON = 1_000_000
    MIL = 1_000


class TendenciaConfig:
    """Configuración para cálculo de tendencias."""

    UMBRAL_CAMBIO = 0.05
    MESES_COMPARACION = 6


@dataclass
class CardStyle:
    """
    Estilo configurable para tarjetas del dashboard.

    :param font_size: Tamaño de fuente
    :param font_color: Color de fuente
    :param bg_color: Color de fondo
    :param text_align: Alineación del texto
    :param font_weight: Peso de la fuente
    :param border_radius: Radio del borde
    :param padding: Espaciado interno
    :param shadow: Sombra de la caja
    """

    font_size: str = "2rem"
    font_color: str = "#ffffff"
    bg_color: str = "#2c3e50"
    text_align: str = "center"
    font_weight: str = "bold"
    border_radius: str = "10px"
    padding: str = "1rem"
    shadow: str = "0 4px 6px rgba(0,0,0,0.1)"

    def to_dict(self) -> dict[str, str]:
        """
        Convierte el estilo a un diccionario compatible con Dash.

        :return: Diccionario con las propiedades CSS
        """
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

    def to_dash(self) -> dict[str, str]:
        """
        Alias de to_dict() para compatibilidad.

        :return: Diccionario con las propiedades CSS
        """
        return self.to_dict()


def superficie_formateada(df: pl.DataFrame) -> str:
    """
    Formatea la superficie total en formato legible (Millones o Miles).

    :param df: DataFrame con columna 'superficie'
    :return: String formateado (e.g., ">1.5M ha" o ">234.5K ha")

    ## Ejemplos:
    ```
        >>> superficie_formateada(df_con_2_millones)
        ">2.0M ha"
        >>> superficie_formateada(df_con_500_mil)
        ">500.0K ha"
    ```
    """
    total_ha = df.select(pl.col("superficie").sum()).item()

    if total_ha >= UnidadSuperficie.MILLON:
        return f">{total_ha / UnidadSuperficie.MILLON:.1f}M ha"

    return f">{total_ha / UnidadSuperficie.MIL:.1f}K ha"


def tendencia_incendios(df: pl.DataFrame) -> str:
    """
    Calcula la tendencia de incendios (Ascendente, Descendente, Estable).

    Compara el último año con el anterior si hay múltiples años,
    o los últimos 6 meses con los 6 anteriores si solo hay un año.

    :param df: DataFrame con columnas 'año', 'mes'

    :return: Una de las siguientes cadenas:

        - "Ascendente": Incremento > 5%
        - "Descendente": Decremento > 5%
        - "Estable": Cambio entre -5% y +5%
        - "Sin datos previos": No hay datos suficientes para comparar

    ## Ejemplos:
    ```
        >>> tendencia_incendios(df_creciente)
        "Ascendente"
        >>> tendencia_incendios(df_estable)
        "Estable"
    ```
    """
    df_counts = (
        df.group_by(["año", "mes"]).agg(pl.len().alias("n")).sort(["año", "mes"])
    )

    años_unicos = df_counts["año"].unique().sort()

    # Determinar valores actual y previo según disponibilidad de datos
    if len(años_unicos) >= 2:
        val_actual, val_previo = _comparar_ultimos_años(df_counts, años_unicos)
    else:
        val_actual, val_previo = _comparar_ultimos_meses(df_counts)

    # Calcular tendencia
    return _calcular_tendencia(val_actual, val_previo)


def _comparar_ultimos_años(
    df_counts: pl.DataFrame,
    años_unicos: pl.Series,
) -> tuple[int, int]:
    """
    Compara el último año completo con el anterior.

    :param df_counts: DataFrame con conteos por año y mes
    :param años_unicos: Serie con años únicos ordenados

    :return: Tupla (valor_actual, valor_previo)
    """
    val_actual = df_counts.filter(pl.col("año") == años_unicos[-1])["n"].sum()
    val_previo = df_counts.filter(pl.col("año") == años_unicos[-2])["n"].sum()

    return val_actual, val_previo


def _comparar_ultimos_meses(
    df_counts: pl.DataFrame,
    meses: int = TendenciaConfig.MESES_COMPARACION,
) -> tuple[int, int]:
    """
    Compara los últimos N meses con los N anteriores.

    :param df_counts: DataFrame con conteos por año y mes
    :param meses: Número de meses a comparar

    :return: Tupla (valor_actual, valor_previo)
    """
    datos_recientes = df_counts.tail(meses * 2)
    val_actual = datos_recientes.tail(meses)["n"].sum()
    val_previo = datos_recientes.head(meses)["n"].sum()

    return val_actual, val_previo


def _calcular_tendencia(val_actual: int, val_previo: int) -> str:
    """
    Calcula la tendencia basándose en el cambio porcentual.

    :param val_actual: Valor del período actual
    :param val_previo: Valor del período previo

    :return: Tendencia calculada
    """
    if val_previo == 0:
        return "Sin datos previos"

    diff_pct = (val_actual - val_previo) / val_previo

    if diff_pct > TendenciaConfig.UMBRAL_CAMBIO:
        return "Ascendente"
    elif diff_pct < -TendenciaConfig.UMBRAL_CAMBIO:
        return "Descendente"

    return "Estable"


# Funciones de utilidad para acceso rápido
def obtener_nombre_comunidad(codigo: int) -> str | None:
    """Obtiene el nombre de una comunidad autónoma por su código."""
    return COMUNIDADES.get(codigo)


def obtener_nombre_provincia(codigo: int) -> str | None:
    """Obtiene el nombre de una provincia por su código."""
    return PROVINCIAS.get(codigo)


def obtener_nombre_causa(codigo: int) -> str | None:
    """Obtiene el nombre de una causa de incendio por su código."""
    return CAUSAS.get(codigo)
