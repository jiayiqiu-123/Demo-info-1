# Proyecto de Programación - Grupo 4

Canal de YouTube con los vídeos de presentación:
https://www.youtube.com/channel/UCGa-H1JCOWjI8ENadtNfq1w

---

## Versión 1 (V1)

En esta fase inicial hemos completado todas las funciones básicas de gestión de aeropuertos:
* `LoadAirports`, `SaveSchengenAirports`, `AddAirport`, `RemoveAirport`, `PlotAirports` y `MapAirports`.

Tanto los tests de lógica como la interfaz gráfica base funcionan correctamente.

### Puntos a mejorar:
* Integración total: El objetivo es que las gráficas y las consultas al usuario dejen de aparecer en ventanas emergentes y se muestren directamente en el panel principal.
* Visualización: Estudiar la integración de Google Earth dentro de la interfaz.
* Optimización: Refactorizar funciones para hacerlas más eficientes en la versión final (V4) una vez se dominen herramientas más avanzadas.

---

## Versión 2 (V2)

Se ha finalizado el desarrollo de las funciones relacionadas con la gestión de aeronaves y vuelos:
* `LoadArrivals`, `PlotArrivals`, `SaveFlights`, `PlotAirlines`, `PlotFlightsType`, `MapFlights` y `LongDistanceArrivals`.

Los tests de esta fase se pasan correctamente.

### Mejoras en la interfaz:
Se ha rediseñado la interfaz para que las gráficas y los paneles de interacción (preguntas y avisos) aparezcan incrustados en la propia ventana, mejorando la experiencia de uso.

### Tareas pendientes y correcciones:
* Ajuste de PlotAirlines: La gráfica de aerolíneas todavía no se visualiza bien en el marco de la interfaz cuando hay muchos datos; falta ajustar el escalado.
* Revisión de parámetros: La función `LoadArrivals` utiliza actualmente dos parámetros (`filename` y `airports`). Debemos confirmar si esto cumple estrictamente con el enunciado o si requiere cambios.
* Clarificación de condiciones: Es necesario revisar que `LoadArrivals` gestione correctamente todos los casos del enunciado.
* Simplificación de código: Siguiendo la línea de la V1, buscaremos simplificar la lógica de cara a la última entrega.
* En la función de PlotFlightsType(aircrafts), se ha considerado los aircraft sin origen como aeropuertos non-schengen. (Hay que preguntar sobre esto)

## Versión 3 (V3)

Se ha completado la arquitectura lógica de asignación de puertas y se ha integrado totalmente en la interfaz gráfica:
* `LoadAirportStructure`, `AssignGate`, `GateOccupancy`, `SearchTerminal` e `IsAirlineInTerminal`.

Tanto el nuevo módulo (`LEBL.py`) como el entorno visual funcionan correctamente.

### Mejoras en la interfaz:
Se ha extendido el panel con botones interactivos para la carga de estructuras, asignación de vuelos (individual y en lote) y resúmenes de terminales, mostrando el mapa de ocupación de puertas integrado mediante un gráfico de Matplotlib.

### Correcciones y optimización:
* Cierre de tareas V2: Se ha unificado el criterio para los vuelos sin origen y se ha confirmado el uso estricto de parámetros en `LoadArrivals`.
* Calidad en interfaz V1: Se han añadido los botones `Set Schengen Attr.` y `Show Airports Data` de forma incrustada para evitar salidas por consola.
* Optimización de Larga Distancia y Mapas (KML): Se ha perfeccionado el filtrado de `LongDistanceArrivals` y la exportación de trayectorias para Google Earth (`MapFlights`), asegurando un cálculo de distancias preciso y una apertura automatizada y fluida del mapa.

### Tareas pendientes y correcciones:
* Hay que mejorar la función Plot Gate Occupancy, para que sea más user-friendly

---

## Versión 4 (V4)

Se ha completado el desarrollo de la simulación dinámica de movimientos y se ha llevado a cabo una revisión integral de la interfaz gráfica, con mejoras sustanciales en usabilidad, visualización y diseño.

Las nuevas funciones implementadas en `aircraft.py` y `LEBL.py` son:
* `LoadDepartures`, `MergeMovements` y `NightAircraft` — en `aircraft.py`, para cargar salidas y combinarlas con las llegadas en una lista unificada de movimientos.
* `AssignNightGates` — asigna puertas a los aviones nocturnos al inicio del día, estableciendo el estado inicial antes de la simulación.
* `FreeGate` — libera la puerta ocupada por un avión dado su identificador, como paso previo a cada ciclo horario.
* `AssignGatesAtTime` — procesa todos los movimientos de una hora concreta: libera las puertas de los vuelos que salen y asigna puertas a los que llegan, devolviendo el número de aviones sin puerta disponible.
* `PlotDayOccupancy` — genera un gráfico de barras apiladas con la ocupación de puertas por terminal a lo largo de las 24 horas del día, con un segundo eje para los aviones sin puerta asignada.

Los ficheros de test (`test_airport.py` y la sección `if __name__ == "__main__"` de `LEBL.py`) cubren todas las funciones de V1 a V4 y se ejecutan correctamente.

### Mejoras en la interfaz:

La interfaz ha sido reescrita y reorganizada de forma completa respecto a la versión anterior. Los cambios más relevantes son:

* **Eliminación de ventanas emergentes**: todos los gráficos (barras, aerolíneas, Schengen, ocupación de puertas, mapa del día, mapas geográficos) se muestran embebidos en el panel derecho de cada pestaña, sin abrir ninguna ventana externa. Al mostrar un gráfico aparece el botón `◀ Back to Table` para volver a la tabla de datos.
* **Mapa geográfico embebido con mapa base**: los mapas de aeropuertos y trayectorias de vuelo utilizan `contextily` para superponer una capa de teselas CartoDB sobre un fondo oscuro, mostrando países y océanos de forma reconocible. Si `contextily` no está instalado, se muestra un mapa de coordenadas básico.
* **Integración con Google Earth**: al mostrar cualquier mapa (aeropuertos, trayectorias, larga distancia) se genera el fichero KML correspondiente y aparece el botón `🌍 Open in Google Earth` junto al botón de volver. Google Earth solo se abre cuando el usuario pulsa ese botón explícitamente; la generación del KML ya no lo abre de forma automática.
* **Filtro de aerolíneas con vista dividida**: al pulsar `Arrivals per Airline` el panel derecho se divide en dos: la parte izquierda muestra un panel de filtro con una barra de búsqueda en tiempo real y checkboxes individuales (con botones `✅ All` / `☐ None`), y la parte derecha actualiza el gráfico de forma inmediata al pulsar `📊 Plot Selected`. Esto resuelve el problema de legibilidad cuando hay muchas aerolíneas (87 en el dataset de LEBL).
* **Mapa de puertas estilo plano de planta**: la función `Gate Map (Visual Plot)` ahora reproduce la estructura real del aeropuerto: corredor horizontal, dedos verticales y puertas alternadas a izquierda y derecha de cada dedo, con etiquetas de nombre de puerta o ID del avión fuera del stub. Las puertas libres se muestran en verde y las ocupadas en rojo.
* **Selector de terminal**: sobre la tabla de puertas aparece una barra con un botón por cada terminal (T1, T2…). El gate map muestra únicamente el terminal seleccionado a pantalla completa, con un tamaño de fuente legible (9 pt), evitando la sobreposición de etiquetas que se producía al mostrar todos los terminales a la vez.
* **Simulación horaria integrada**: el control de hora (Spinbox 00–23 y botón `▶ Apply`) está incorporado en la propia barra del selector de terminal, procesando los movimientos de esa hora y actualizando el gate map y la tabla de puertas sin necesidad de ventanas emergentes.
* **Dos temas de color**: el botón `☀ Light Mode` / `🌙 Dark Mode` en la cabecera alterna entre un tema oscuro (navy profundo) y un tema claro (azul celeste y blanco). El cambio reconstruye completamente la interfaz para garantizar que ningún widget conserve colores residuales del tema anterior.

### Correcciones y optimización:
* Cierre de la tarea pendiente de V3: el mapa de ocupación de puertas es ahora legible y visualmente coherente con la estructura real del aeropuerto LEBL.
* Se ha eliminado el checkbox `Show only occupied gates` del panel de Gate Management por resultar redundante una vez disponible el gate map visual.
* `PlotDayOccupancy` recarga internamente una copia fresca de la estructura del aeropuerto antes de simular las 24 horas, evitando que el estado de `bcn` en uso se vea alterado por la simulación.
* La función `os.startfile` se desactiva temporalmente durante la generación de KML para impedir que `MapAirports` y `MapFlights` abran Google Earth de forma automática; se restaura inmediatamente después en un bloque `finally`.
