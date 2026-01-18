<div align="center">

# 🔥 Incendios Forestales en España (1983-2023)
  [![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
  [![Dependency Manager](https://img.shields.io/badge/uv-astral-purple?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
  [![Code Style Black](https://img.shields.io/badge/Code%20Style-Black-black)](https://github.com/psf/black)
  [![Imports isort](https://img.shields.io/badge/Imports-isort-blue)](https://pycqa.github.io/isort/)
  [![Dash](https://img.shields.io/badge/Dash-3.2+-008DE4?style=flat&logo=plotly&logoColor=white)](https://dash.plotly.com/)
  [![Polars](https://img.shields.io/badge/Polars-1.34+-CD792C?style=flat)](https://pola.rs/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

Dashboard interactivo para la exploración y visualización de datos históricos de incendios forestales en España. Analiza más de **40 años de datos** sobre incendios, sus causas, impacto territorial y evolución temporal.

<img src="https://img.shields.io/badge/📊-Dashboard%20Interactivo-FF6B35?style=for-the-badge" alt="Dashboard"/>
<img src="https://img.shields.io/badge/🗺️-Mapas%20Coropléticos-2E86AB?style=for-the-badge" alt="Mapas"/>
<img src="https://img.shields.io/badge/📈-Análisis%20Temporal-A23B72?style=for-the-badge" alt="Análisis"/>


---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Datos](#-datos)
- [Tecnologías](#-tecnologías)
- [Licencia](#-licencia)

---

## ✨ Características

### Visualización Geográfica
- **Mapa coroplético** de España por provincias con superficie quemada
- **Zoom interactivo** por Comunidad Autónoma
- **Marcadores de grandes incendios** (>500 ha) con información detallada

### Análisis de Causas
- **Gráfico de áreas apiladas** con evolución porcentual de causas
- Clasificación: Rayo ⚡ | Negligencia 🚬 | Accidente 🛠️ | Intencionado 🔥 | Desconocido ❓ | Reproducido 🔁

### Comparativas Regionales
- **Rankings** de comunidades y provincias por superficie afectada
- Análisis de **medias anuales** y tendencias

### Filtros Interactivos
- Selección de **rango de años** (1983-2023)
- Filtrado por **Comunidad Autónoma**
- Filtrado por **causas de incendio**
- **KPIs dinámicos**: total incendios, superficie quemada, tendencia

---

## 📸 Capturas de Pantalla

### Dashboard principal

![Dashboard](imgs\dashboard.jpg)

### Dashboard con filtros aplicados

---

## 🚀 Instalación

### Prerrequisitos
- Python 3.13 o superior
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip

> [!IMPORTANT]
> Para la gestión de dependencias y entornos virtuales se utiliza **[uv](https://docs.astral.sh/uv/)**, un gestor de paquetes extremadamente rápido escrito en Rust.
> 
> Si no dispones de `uv`, instálalo ejecutando:
> ```bash
> # En macOS/Linux
> curl -LsSf https://astral.sh/uv/install.sh | sh
>
> # En Windows
> powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
> ```

### Opción 1: Con uv (Recomendado)


```bash
# Clonar el repositorio
git clone https://github.com/yabol02/VAD.git
cd VAD

# Crear entorno virtual e instalar dependencias
uv sync
```

### Opción 2: Con pip

```bash
# Clonar el repositorio
git clone https://github.com/yabol02/VAD.git
cd VAD

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Activar entorno (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -e .
```

---

## 💻 Uso

Para ejecutar el fichero, ejecutar uno de los siguientes comandos:

```bash
# Con uv
uv run python main.py

# Con pip (entorno activado)
python main.py
```

Abre tu navegador en **http://127.0.0.1:8050**

---

## 📁 Estructura del Proyecto

```
VAD/
├── 📄 main.py              # Aplicación Dash principal
├── 📄 plots.py             # Funciones de visualización (Plotly)
├── 📄 processing.py        # Procesamiento de datos (Polars/GeoPandas)
├── 📄 utils.py             # Utilidades y constantes
├── 📓 exploracion.ipynb    # Análisis exploratorio y propuestas de gráficos
├── 📄 pyproject.toml       # Configuración del proyecto
├── 📄 README.md
├── 📄 LEEME.md
└── 📂 data/
    ├── fires_all.csv              # Dataset de incendios
    └── provincias_espana.geojson  # Geometrías provinciales
```

---

## 📊 Datos


Los datos provienen de [Civio](https://datos.civio.es/), organización dedicada al periodismo de datos:

| Dataset | Descripción | Enlace |
|---------|-------------|--------|
| **Incendios Forestales** | Todos los incendios en España (1963-2023) | [🔗 Enlace](https://datos.civio.es/dataset/todos-los-incendios-forestales/) |
| **Mapa Interactivo** | Visualización original de Civio | [🔗 Enlace](https://civio.es/medio-ambiente/mapa-de-incendios-forestales/) |
| **Provincias de España** | Ubicación de los límites de las provincias de España | [🔗 Enlace](https://gist.github.com/josemamira/3af52a4698d42b3f676fbc23f807a605?short_path=45ec3d9) |

---

## 🛠️ Tecnologías

| Tecnología | Uso |
|------------|-----|
| ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white) | Lenguaje principal |
| ![Dash](https://img.shields.io/badge/-Dash-008DE4?style=flat&logo=plotly&logoColor=white) | Framework web/dashboard |
| ![Plotly](https://img.shields.io/badge/-Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) | Visualizaciones interactivas |
| ![Polars](https://img.shields.io/badge/-Polars-CD792C?style=flat) | Procesamiento de datos |
| ![GeoPandas](https://img.shields.io/badge/-GeoPandas-139C5A?style=flat) | Datos geoespaciales |
| ![Bootstrap](https://img.shields.io/badge/-Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white) | Estilos (Cyborg theme) |

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---


<p align="center">
  <sub>👨🏻‍💻 Yago Boleas Francisco (<a href="https://github.com/yabol02">@yabol02</a>)</sub>
</p>