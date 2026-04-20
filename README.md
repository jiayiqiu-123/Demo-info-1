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

