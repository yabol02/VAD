<div align="center">

# 🔥 Forest Fires in Spain (1983-2023)
  [![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
  [![Dependency Manager](https://img.shields.io/badge/uv-astral-purple?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
  [![Code Style Black](https://img.shields.io/badge/Code%20Style-Black-black)](https://github.com/psf/black)
  [![Imports isort](https://img.shields.io/badge/Imports-isort-blue)](https://pycqa.github.io/isort/)
  [![Dash](https://img.shields.io/badge/Dash-3.2+-008DE4?style=flat&logo=plotly&logoColor=white)](https://dash.plotly.com/)
  [![Polars](https://img.shields.io/badge/Polars-1.34+-CD792C?style=flat)](https://pola.rs/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

Interactive dashboard for exploring and visualizing historical data on forest fires in Spain. Analyze over **40 years of data** on wildfires, their causes, territorial impact, and temporal evolution.

<img src="https://img.shields.io/badge/📊-Interactive%20Dashboard-FF6B35?style=for-the-badge" alt="Dashboard"/>
<img src="https://img.shields.io/badge/🗺️-Choropleth%20Maps-2E86AB?style=for-the-badge" alt="Maps"/>
<img src="https://img.shields.io/badge/📈-Temporal%20Analysis-A23B72?style=for-the-badge" alt="Analysis"/>


---

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Data](#-data)
- [Technologies](#-technologies)
- [License](#-license)

---

## ✨ Features

### Geographic Visualization
- **Choropleth map** of Spain by province showing burned area
- **Interactive zoom** by Autonomous Community
- **Major fire markers** (>500 ha) with detailed information

### Cause Analysis
- **Stacked area chart** with percentage evolution of causes
- Classification: Lightning ⚡ | Negligence 🚬 | Accident 🛠️ | Intentional 🔥 | Unknown ❓ | Rekindled 🔁

### Regional Comparisons
- **Rankings** of communities and provinces by affected area
- **Annual average** analysis and trends

### Interactive Filters
- **Year range** selection (1983-2023)
- Filter by **Autonomous Community**
- Filter by **fire causes**
- **Dynamic KPIs**: total fires, burned area, trend

---

## 📸 Screenshots

### Main Dashboard

![Dashboard](imgs\dashboard.jpg)

### Dashboard with applied filters

---

## 🚀 Installation

### Prerequisites
- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

> [!IMPORTANT]
> For dependency and virtual environment management, **[uv](https://docs.astral.sh/uv/)** is used, an extremely fast package manager written in Rust.
> 
> If you don't have `uv`, install it by running:
> ```bash
> # On macOS/Linux
> curl -LsSf https://astral.sh/uv/install.sh | sh
>
> # On Windows
> powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
> ```

### Option 1: With uv (Recommended)


```bash
# Clone the repository
git clone https://github.com/yabol02/VAD.git
cd VAD

# Create virtual environment and install dependencies
uv sync
```

### Option 2: With pip

```bash
# Clone the repository
git clone https://github.com/yabol02/VAD.git
cd VAD

# Create virtual environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Activate environment (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -e .
```

---

## 💻 Usage

To run the application, execute one of the following commands:

```bash
# With uv
uv run python main.py

# With pip (environment activated)
python main.py
```

Open your browser at **http://127.0.0.1:8050**

---

## 📁 Project Structure

```
VAD/
├── 📄 main.py              # Main Dash application
├── 📄 plots.py             # Visualization functions (Plotly)
├── 📄 processing.py        # Data processing (Polars/GeoPandas)
├── 📄 utils.py             # Utilities and constants
├── 📓 exploracion.ipynb    # Exploratory analysis and chart proposals
├── 📄 pyproject.toml       # Project configuration
├── 📄 README.md
├── 📄 LEEME.md
└── 📂 data/
    ├── fires_all.csv              # Fire dataset
    └── provincias_espana.geojson  # Provincial geometries
```

---

## 📊 Data


Data sourced from [Civio](https://datos.civio.es/), a data journalism organization:

| Dataset | Description | Link |
|---------|-------------|------|
| **Forest Fires** | All fires in Spain (1963-2023) | [🔗 Link](https://datos.civio.es/dataset/todos-los-incendios-forestales/) |
| **Interactive Map** | Original Civio visualization | [🔗 Link](https://civio.es/medio-ambiente/mapa-de-incendios-forestales/) |
| **Spanish Provinces** | Location of Spain's province boundaries | [🔗 Link](https://gist.github.com/josemamira/3af52a4698d42b3f676fbc23f807a605?short_path=45ec3d9) |

---

## 🛠️ Technologies

| Technology | Purpose |
|------------|---------|
| ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white) | Main language |
| ![Dash](https://img.shields.io/badge/-Dash-008DE4?style=flat&logo=plotly&logoColor=white) | Web/dashboard framework |
| ![Plotly](https://img.shields.io/badge/-Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) | Interactive visualizations |
| ![Polars](https://img.shields.io/badge/-Polars-CD792C?style=flat) | Data processing |
| ![GeoPandas](https://img.shields.io/badge/-GeoPandas-139C5A?style=flat) | Geospatial data |
| ![Bootstrap](https://img.shields.io/badge/-Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white) | Styling (Cyborg theme) |

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---


<p align="center">
  <sub>👨🏻‍💻 Yago Boleas Francisco (<a href="https://github.com/yabol02">@yabol02</a>)</sub>
</p>