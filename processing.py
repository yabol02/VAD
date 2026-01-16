import geopandas as gpd
import polars as pl
from shapely.validation import make_valid

from utils import CAUSAS, COMUNIDADES, PROVINCIAS

fuegos = pl.read_csv("./data/fires_all.csv")

fuegos = fuegos.with_columns(
    [
        pl.col("fecha").str.to_date("%Y-%m-%d"),
        pl.col("lat").str.replace_all('"', "").cast(pl.Float64, strict=False),
        pl.col("lng").str.replace_all('"', "").cast(pl.Float64, strict=False),
        pl.col("latlng_explicit").str.replace_all('"', "").cast(pl.Int8, strict=False),
        pl.col("superficie").cast(pl.Float64, strict=False),
        pl.col("muertos").cast(pl.Int64, strict=False),
        pl.col("heridos").cast(pl.Int64, strict=False),
        pl.col("time_ctrl").cast(pl.Int64, strict=False),
        pl.col("time_ext").cast(pl.Int64, strict=False),
        pl.col("personal").cast(pl.Int64, strict=False),
        pl.col("medios").cast(pl.Int64, strict=False),
        pl.col("gastos").cast(pl.Float64, strict=False),
        pl.col("perdidas").cast(pl.Float64, strict=False),
    ]
)

fuegos = fuegos.filter(pl.col("fecha").dt.year() >= 1983)

fuegos = fuegos.filter(
    pl.col("lat").is_not_null() & pl.col("lng").is_not_null()
)  # Sitios fuera de España (Francia y Portugal) pero que afectaron al territorio español

fuegos = fuegos.with_columns(
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

fuegos = fuegos.with_columns(
    [
        pl.col("idcomunidad")
        .cast(pl.String, strict=False)
        .replace(COMUNIDADES)
        .alias("comunidad"),
        pl.col("idprovincia")
        .cast(pl.String, strict=False)
        .replace(PROVINCIAS)
        .alias("provincia"),
        pl.when(pl.col("superficie") <= 1)
        .then(pl.lit("Conato (<1 ha)"))
        .when(pl.col("superficie") < 500)
        .then(pl.lit("Incendio (1–500 ha)"))
        .otherwise(pl.lit("Gran incendio (>500 ha)"))
        .alias("tipo_incendio"),
        pl.col("causa").cast(pl.String, strict=False).replace(CAUSAS).alias("causa"),
        pl.col("fecha").dt.year().alias("año"),
        pl.col("fecha").dt.month().alias("mes"),
        pl.col("fecha").dt.week().alias("semana"),
    ]
)

provincias_df = gpd.read_file("./data/provincias_espana.geojson")
provincias_df["geometry"] = provincias_df["geometry"].apply(make_valid)
provincias_df = provincias_df.set_crs("EPSG:4326")
centros = provincias_df.to_crs(epsg=25830).geometry.centroid.to_crs(epsg=4326)
provincias_df["centro_prov_lon"] = centros.x
provincias_df["centro_prov_lat"] = centros.y

ccaa = provincias_df.dissolve(by="CCAA", as_index=False).to_crs(epsg=25830)
centros_ccaa = ccaa.geometry.centroid.to_crs(epsg=4326)
ccaa["centro_ccaa_lon"] = centros_ccaa.x
ccaa["centro_ccaa_lat"] = centros_ccaa.y
provincias_df = provincias_df.merge(
    ccaa[["CCAA", "centro_ccaa_lon", "centro_ccaa_lat"]], on="CCAA", how="left"
)
