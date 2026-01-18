"""Módulo de procesamiento y carga de datos de incendios forestales."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import polars as pl
from shapely.validation import make_valid

from utils import CAUSAS, COMUNIDADES, PROVINCIAS


class DataPaths:
    """Rutas de archivos de datos."""

    DATA_DIR = Path("./data")
    FIRES_CSV = DATA_DIR / "fires_all.csv"
    PROVINCIAS_GEOJSON = DATA_DIR / "provincias_espana.geojson"


class ProcessingConfig:
    """Configuración para el procesamiento de datos."""

    # Año mínimo de datos válidos
    MIN_YEAR = 1983

    # Sistema de coordenadas
    CRS_WGS84 = "EPSG:4326"
    CRS_ETRS89 = "EPSG:25830"

    # Umbrales para clasificación de incendios
    UMBRAL_CONATO = 1.0  # hectáreas
    UMBRAL_GRANDE = 500.0  # hectáreas

    # Formato de fecha esperado
    DATE_FORMAT = "%Y-%m-%d"


class TipoIncendio:
    """Clasificación de tipos de incendio por superficie."""

    CONATO = "Conato (<1 ha)"
    INCENDIO = "Incendio (1–500 ha)"
    GRAN_INCENDIO = "Gran incendio (>500 ha)"


def cargar_datos_incendios(path: Path | str | None = None) -> pl.DataFrame:
    """
    Carga y procesa los datos de incendios desde CSV.

    :param path: Ruta al archivo CSV. Si es None, usa la ruta por defecto.

    :return: DataFrame de Polars con los datos procesados

    :raises FileNotFoundError: Si el archivo no existe
    :raises ValueError: Si los datos no cumplen con el formato esperado
    """
    if path is None:
        path = DataPaths.FIRES_CSV

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de datos: {path}")

    df = pl.read_csv(path)

    df = (
        df.pipe(_limpiar_tipos_datos)
        .pipe(_filtrar_datos_invalidos)
        .pipe(_corregir_valores_negativos)
        .pipe(_agregar_columnas_derivadas)
    )

    return df


def _limpiar_tipos_datos(df: pl.DataFrame) -> pl.DataFrame:
    """
    Convierte las columnas a los tipos de datos correctos.

    :param df: DataFrame crudo
    :return: DataFrame con tipos corregidos
    """
    return df.with_columns(
        [
            # Fechas
            pl.col("fecha").str.to_date(ProcessingConfig.DATE_FORMAT),
            # Coordenadas geográficas
            pl.col("lat").str.replace_all('"', "").cast(pl.Float64, strict=False),
            pl.col("lng").str.replace_all('"', "").cast(pl.Float64, strict=False),
            pl.col("latlng_explicit")
            .str.replace_all('"', "")
            .cast(pl.Int8, strict=False),
            # Métricas del incendio
            pl.col("superficie").cast(pl.Float64, strict=False),
            pl.col("muertos").cast(pl.Int64, strict=False),
            pl.col("heridos").cast(pl.Int64, strict=False),
            # Tiempos de respuesta
            pl.col("time_ctrl").cast(pl.Int64, strict=False),
            pl.col("time_ext").cast(pl.Int64, strict=False),
            # Recursos utilizados
            pl.col("personal").cast(pl.Int64, strict=False),
            pl.col("medios").cast(pl.Int64, strict=False),
            # Costos
            pl.col("gastos").cast(pl.Float64, strict=False),
            pl.col("perdidas").cast(pl.Float64, strict=False),
        ]
    )


def _filtrar_datos_invalidos(df: pl.DataFrame) -> pl.DataFrame:
    """
    Filtra registros con datos inválidos o fuera de rango.

    :param df: DataFrame con tipos corregidos
    :return: DataFrame filtrado
    """
    return (
        df
        # Filtrar por año mínimo
        .filter(pl.col("fecha").dt.year() >= ProcessingConfig.MIN_YEAR)
        # Filtrar registros sin coordenadas (fuera de España)
        .filter(pl.col("lat").is_not_null() & pl.col("lng").is_not_null())
    )


def _corregir_valores_negativos(df: pl.DataFrame) -> pl.DataFrame:
    """
    Corrige valores negativos en columnas de tiempo.
    Los valores negativos en tiempo de control/extinción se reemplazan por 0.

    :param df: DataFrame filtrado
    :return: DataFrame con valores corregidos
    """
    return df.with_columns(
        [
            pl.when(pl.col("time_ctrl") < 0)
            .then(0)
            .otherwise(pl.col("time_ctrl"))
            .alias("time_ctrl"),
            pl.when(pl.col("time_ext") < 0)
            .then(0)
            .otherwise(pl.col("time_ext"))
            .alias("time_ext"),
        ]
    )


def _agregar_columnas_derivadas(df: pl.DataFrame) -> pl.DataFrame:
    """
    Agrega columnas derivadas de los datos existentes.

    Añade:
    - Nombres de comunidad y provincia (en lugar de códigos)
    - Clasificación del tipo de incendio por superficie
    - Nombre de la causa (en lugar de código)
    - Componentes temporales (año, mes, semana)

    :param df: DataFrame con datos corregidos
    :return: DataFrame enriquecido con columnas derivadas
    """
    return df.with_columns(
        [
            # Geografía: convertir códigos a nombres
            _crear_columna_comunidad(),
            _crear_columna_provincia(),
            # Clasificación del incendio por superficie
            _crear_columna_tipo_incendio(),
            # Causa: convertir código a nombre
            _crear_columna_causa(),
            # Componentes temporales
            pl.col("fecha").dt.year().alias("año"),
            pl.col("fecha").dt.month().alias("mes"),
            pl.col("fecha").dt.week().alias("semana"),
        ]
    )


def _crear_columna_comunidad() -> pl.Expr:
    """Crea expresión para la columna de comunidad autónoma."""
    return (
        pl.col("idcomunidad")
        .cast(pl.String, strict=False)
        .replace(COMUNIDADES)
        .alias("comunidad")
    )


def _crear_columna_provincia() -> pl.Expr:
    """Crea expresión para la columna de provincia."""
    return (
        pl.col("idprovincia")
        .cast(pl.String, strict=False)
        .replace(PROVINCIAS)
        .alias("provincia")
    )


def _crear_columna_tipo_incendio() -> pl.Expr:
    """Crea expresión para clasificar el tipo de incendio por superficie."""
    return (
        pl.when(pl.col("superficie") <= ProcessingConfig.UMBRAL_CONATO)
        .then(pl.lit(TipoIncendio.CONATO))
        .when(pl.col("superficie") < ProcessingConfig.UMBRAL_GRANDE)
        .then(pl.lit(TipoIncendio.INCENDIO))
        .otherwise(pl.lit(TipoIncendio.GRAN_INCENDIO))
        .alias("tipo_incendio")
    )


def _crear_columna_causa() -> pl.Expr:
    """Crea expresión para la columna de causa del incendio."""
    return pl.col("causa").cast(pl.String, strict=False).replace(CAUSAS).alias("causa")


def cargar_geometrias_provincias(
    path: Path | str | None = None,
) -> gpd.GeoDataFrame:
    """
    Carga y procesa las geometrías de las provincias españolas.

    :param path: Ruta al archivo GeoJSON. Si es None, usa la ruta por defecto.
    :return: GeoDataFrame con geometrías validadas y centroides calculados
    :raises FileNotFoundError: Si el archivo no existe
    """
    if path is None:
        path = DataPaths.PROVINCIAS_GEOJSON

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de geometrías: {path}")

    # Cargar GeoJSON
    gdf = gpd.read_file(path)

    # Validar y procesar geometrías
    gdf = _validar_geometrias(gdf)
    gdf = _calcular_centroides_provincias(gdf)

    return gdf


def _validar_geometrias(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Valida y corrige geometrías inválidas.

    :param gdf: GeoDataFrame con geometrías potencialmente inválidas
    :return: GeoDataFrame con geometrías validadas
    """
    gdf["geometry"] = gdf["geometry"].apply(make_valid)
    gdf = gdf.set_crs(ProcessingConfig.CRS_WGS84)
    return gdf


def _calcular_centroides_provincias(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calcula los centroides de cada provincia.

    :param gdf: GeoDataFrame de provincias
    :return: GeoDataFrame con columnas de centroides añadidas
    """
    # Calcular centroides en proyección métrica para mayor precisión
    centroides = gdf.to_crs(ProcessingConfig.CRS_ETRS89).geometry.centroid.to_crs(
        ProcessingConfig.CRS_WGS84
    )

    gdf["centro_prov_lon"] = centroides.x
    gdf["centro_prov_lat"] = centroides.y

    return gdf


def crear_geometrias_ccaa(provincias_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Crea geometrías de comunidades autónomas agrupando provincias.

    :param provincias_gdf: GeoDataFrame de provincias
    :return: GeoDataFrame de comunidades autónomas con centroides
    """
    # Disolver provincias por CCAA
    ccaa = provincias_gdf.dissolve(
        by="CCAA",
        as_index=False,
    ).to_crs(ProcessingConfig.CRS_ETRS89)

    # Calcular centroides
    ccaa = _calcular_centroides_ccaa(ccaa)

    return ccaa


def _calcular_centroides_ccaa(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calcula los centroides de cada comunidad autónoma.

    :param gdf: GeoDataFrame de CCAA
    :return: GeoDataFrame con columnas de centroides añadidas
    """
    centroides = gdf.geometry.centroid.to_crs(ProcessingConfig.CRS_WGS84)

    gdf["centro_ccaa_lon"] = centroides.x
    gdf["centro_ccaa_lat"] = centroides.y

    return gdf


def enriquecer_provincias_con_ccaa(
    provincias_gdf: gpd.GeoDataFrame,
    ccaa_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Enriquece el GeoDataFrame de provincias con información de sus CCAA.

    :param provincias_gdf: GeoDataFrame de provincias
    :param ccaa_gdf: GeoDataFrame de CCAA
    :return: GeoDataFrame de provincias con centroides de CCAA
    """
    return provincias_gdf.merge(
        ccaa_gdf[["CCAA", "centro_ccaa_lon", "centro_ccaa_lat"]],
        on="CCAA",
        how="left",
    )


def cargar_todos_los_datos() -> tuple[pl.DataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Carga y procesa todos los datos necesarios para el dashboard.

    Esta es la función principal de inicialización que debe usarse
    para cargar todos los datos del dashboard.

    :return: Tupla con (fuegos_df, provincias_gdf, ccaa_gdf)

    ## Ejemplo:
    ```
        >>> fuegos, provincias, ccaa = cargar_todos_los_datos()
        >>> print(f"Cargados {len(fuegos)} incendios")
    ```
    """
    # Cargar datos de incendios
    fuegos_df = cargar_datos_incendios()

    # Cargar geometrías de provincias
    provincias_gdf = cargar_geometrias_provincias()

    # Crear geometrías de CCAA
    ccaa_gdf = crear_geometrias_ccaa(provincias_gdf)

    # Enriquecer provincias con datos de CCAA
    provincias_gdf = enriquecer_provincias_con_ccaa(provincias_gdf, ccaa_gdf)

    return fuegos_df, provincias_gdf, ccaa_gdf


# Carga de datos al importar el módulo
fuegos, provincias_df, ccaa = cargar_todos_los_datos()


__all__ = [
    "fuegos",
    "provincias_df",
    "ccaa",
    "cargar_datos_incendios",
    "cargar_geometrias_provincias",
    "crear_geometrias_ccaa",
    "cargar_todos_los_datos",
    "DataPaths",
    "ProcessingConfig",
    "TipoIncendio",
]
