[Mapa incendios](https://civio.es/medio-ambiente/mapa-de-incendios-forestales/)

[Todos los datos](https://datos.civio.es/colecciones/)

[Incendios forestales España 1963-2023](https://datos.civio.es/dataset/todos-los-incendios-forestales/)

[Riesgo meteorológico Europa 1971-2022](https://datos.civio.es/dataset/riesgo-meteorologico-de-incendio-en-europa/)

Los grandes incendios se consideran a partir de las 500 hectáreas afectadas

graficos interesantes de incendios forestales <- Para ver ideas chulis

#### Apuntes

barra apilada visual
gráfico de tiempos con piruletas
gráficas de barras personalizadas con más información e insights
distribución de datos categóricos a lo largo del tiempo (como waffle?)
areaplot a lo largo del tiempo por causa o comunidad autónoma
número de incendios / áreas afectadas
mostrar mes a mes o acumulado a lo largo del año
hectáreas quemadas por mes y año por comunidad autónoma

Diagrama de Sankey que empieza con log-hectáreas quemadas, personal empleado, pasa a tiempo de control y finalmente a tiempo de extinción. Igual está bien añadir heridos y muertos. Mirar si merece la pena hacerlo por causa o comunidad autónoma (no creo). Igual toca filtrar por mega-incendios

En el mapa, dar la opción a elegir la comunidad autónoma con un desplegable. Al elegir una, la enfoca y permite ver todos los incendios, pintados por causa y viendo tamaños. Permitir elegir el intervalo de fechas. Debajo que haya un histograma por mes. Hacer algo parecido a esto: https://civio.es/medio-ambiente/2023/10/17/el-territorio-de-europa-en-riesgo-alto-de-incendios-se-ha-duplicado-en-los-ultimos-50-anos/


Con plotly con add_annotation creo que puedo poner fueguitos. Creo que con los datos meteo puedo poner los incendios top o algo así para cada mes

https://cdn.statcdn.com/Infographic/images/normal/19098.jpeg
https://www.fundacionaquae.org/wp-content/uploads/2019/08/incendios-forestales-1.jpg
https://es.statista.com/grafico/34866/superficie-acumulada-quemada-por-incendios-forestales-en-la-union-europea/
https://es.statista.com/grafico/22946/numero-de-incendios-en-paises-sudamericanos/
https://archivo-es.greenpeace.org/espana/Global/espana/2017/imgs/bosques/evolucion%20superficie%20afectada.jpg 
https://www.datocms-assets.com/17507/1679411469-hosteleria_espana_2023.jpeg
https://python-graph-gallery.com/web-stacked-area-charts-on-a-map/ <-- Como este pero para cada comunidad autónoma y para las causas
https://communities.sas.com/t5/SAS-Visual-Analytics-Gallery/Fighting-the-Amazon-forest-fires-with-advanced-analytics/ta-p/784221
https://blogs.sas.com/content/sascom/2018/06/29/blazing-statistics-visualizing-wildfire-data/


Tengo un dataframe de polars llamado "fuegos" que corresponde a los incendios ocurridos en España desde el 1983. Tiene este esquema:

```
Schema([('id', Int64), ('superficie', Float64), ('fecha', Date), ('lat', Float64), ('lng', Float64), ('latlng_explicit', Int8), ('idcomunidad', Int64), ('idprovincia', Int64), ('idmunicipio', Int64), ('municipio', String), ('causa', String), ('causa_supuesta', Int64), ('causa_desc', Int64), ('muertos', Int64), ('heridos', Int64), ('time_ctrl', Int64), ('time_ext', Int64), ('personal', Int64), ('medios', Int64), ('gastos', Float64), ('perdidas', Float64), ('comunidad', String), ('provincia', String), ('año', Int32), ('mes', Int8)])
```