import geopandas as gpd
import polars as pl
from shapely.validation import make_valid

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
    2: "Accidente o negligencia",
    3: "Accidente o negligencia",
    4: "Intencionado",
    5: "De origen desconocido",
    6: "Reproducido",
}

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

fuegos = fuegos.with_columns([
    pl.when(pl.col("time_ctrl") < 0).then(0).otherwise(pl.col("time_ctrl")).alias("time_ctrl"),
    pl.when(pl.col("time_ext") < 0).then(0).otherwise(pl.col("time_ext")).alias("time_ext")
])

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