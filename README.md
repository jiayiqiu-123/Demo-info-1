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