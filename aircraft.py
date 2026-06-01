import matplotlib.pyplot as plt
import math
import os

from airport import *

# ---------------------------------------------------------------------------
# Clase Aircraft — V4: Destination y DepartureTime ahora se usan activamente
# ---------------------------------------------------------------------------
class Aircraft:
    # dest y dtime ya existían en V2 como None por defecto
    # En V4 los rellenamos con los datos del fichero de salidas
    def __init__(self, id, comp, origin, time, dest=None, dtime=None):
        self.Id            = id       # ID del avión, ej: "ECMKV"
        self.Company       = comp     # Código ICAO aerolínea, ej: "VLG"
        self.origin        = origin   # Objeto Airport origen (o None si no se encuentra)
        self.time          = time     # Hora de llegada "hh:mm" (None si es avión nocturno)
        self.Destination   = dest     # Código ICAO destino, ej: "LYBE" (None si no hay salida)
        self.DepartureTime = dtime    # Hora de salida "hh:mm" (None si no hay salida)


# ---------------------------------------------------------------------------
# Funciones V2 (sin cambios)
# ---------------------------------------------------------------------------

def LoadArrivals(filename, airports):
    # Lee el fichero de llegadas y devuelve una lista de Aircraft.
    # Salta líneas con formato incorrecto. Destination y DepartureTime quedan None.
    # NOTA: airports es necesario para obtener coordenadas del origen → justificado en el vídeo.

    aircrafts = []
    try:
        with open(filename, 'r') as f:
            next(f)         # Salta la primera línea (cabecera: AIRCRAFT ORIGIN ARRIVAL AIRLINE)
            for line in f:  # Recorre el resto de líneas una a una
                elementos = line.split()    # Separa la línea por espacios

                # El fichero siempre tiene 4 columnas fijas
                # Si una línea tiene menos de 4 elementos → estructura incorrecta → saltar
                if len(elementos) < 4:
                    continue

                # Acceso directo por posición (más fiable que intentar adivinar el tipo)
                aircraft_id = elementos[0]  # Ej: "ECMKV"
                origin_code = elementos[1]  # Ej: "LYBE" (código ICAO del aeropuerto origen)
                arrival     = elementos[2]  # Ej: "00:04" (hora de llegada)
                airline     = elementos[3]  # Ej: "VLG"  (código ICAO de la aerolínea)

                # Validación del formato de la hora (debe ser "hh:mm")
                # Si split(":") no da exactamente 2 partes → formato incorrecto → saltar
                time_parts = arrival.split(":")
                if len(time_parts) != 2:
                    continue
                try:
                    hour   = int(time_parts[0])     # Convierte "00" a 0, "23" a 23, etc.
                    minute = int(time_parts[1])     # Convierte "04" a 4, "59" a 59, etc.
                    if not (0 <= hour < 24 and 0 <= minute < 60):
                        continue    # Hora o minuto fuera de rango → saltar
                except ValueError:
                    continue        # No es un número (ej: "ab:cd") → saltar

                # Busca el objeto Airport cuyo ICAO coincide con origin_code
                # next() devuelve el primero que encuentre, o None si no existe
                # None significa que el aeropuerto de origen no está en nuestra lista
                found_ap_obj = next(
                    (ap for ap in airports if ap.ICAO == origin_code), None
                )

                # Crea el objeto Aircraft con los 4 campos disponibles
                # Destination y DepartureTime quedan None por defecto (se rellenan en V4)
                aircraft = Aircraft(aircraft_id, airline, found_ap_obj, arrival)
                aircrafts.append(aircraft)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    return aircrafts


def PlotArrivals(aircrafts):
    # Muestra un gráfico de barras con el número de llegadas por cada hora del día (0-23)
    if not aircrafts:
        print("Error: The aircraft list is empty. No plot will be shown.")
        return

    hours = [0] * 24    # Lista de 24 ceros, uno por cada hora del día

    for ac in aircrafts:
        if ac.time:
            try:
                hour_val = int(ac.time.split(":")[0])
                if 0 <= hour_val <= 23:
                    hours[hour_val] += 1
            except (ValueError, IndexError):
                pass

    plt.bar(range(24), hours)
    plt.xlabel("Hour")
    plt.ylabel("Arrivals")
    plt.title("Arrivals per hour")
    plt.xticks(range(24))
    plt.show()


def SaveFlights(aircrafts, filename):
    # Guarda la lista de vuelos en un fichero con el mismo formato que el de entrada
    # Si la lista está vacía, no crea el fichero y devuelve -1
    if not aircrafts:
        return -1

    with open(filename, 'w') as f:
        f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
        for ac in aircrafts:
            origin_ap    = ac.origin.ICAO if ac.origin  else "-"
            aircraft_id  = ac.Id          if ac.Id      else "-"
            arrival_time = ac.time        if ac.time    else "0"
            company      = ac.Company     if ac.Company else "-"
            f.write(f"{aircraft_id} {origin_ap} {arrival_time} {company}\n")
    return 0


def PlotAirlines(aircrafts):
    # Muestra un gráfico de barras con el número de vuelos por aerolínea
    if not aircrafts:
        print("Error: The aircraft list is empty. No plot will be shown.")
        return

    airlines = {}

    for ac in aircrafts:
        company = ac.Company
        if company is None:
            continue
        airlines[company] = airlines.get(company, 0) + 1

    names  = list(airlines.keys())
    values = list(airlines.values())
    index  = list(range(1, len(names) + 1))

    plt.figure(figsize=(10, 5))
    barres = plt.bar(index, values)
    plt.title("Flights per Airline", fontsize=14, pad=10)
    plt.xlabel("Airline Index", fontsize=11)
    plt.ylabel("Number of Flights", fontsize=11)
    plt.xticks(index, fontsize=7, rotation=90)

    llegenda_textos = [str(index[j]) + ": " + str(names[j]) for j in range(len(names))]
    plt.legend(barres, llegenda_textos, ncol=6, fontsize=7,
               bbox_to_anchor=(0.5, -0.25), loc='upper center')
    plt.tight_layout()
    plt.show()
    return 0


def PlotFlightsType(aircrafts):
    # Muestra un gráfico de barras apiladas: vuelos de origen Schengen vs no Schengen
    if not aircrafts:
        print("Error: The aircraft list is empty. No plot will be shown.")
        return

    schengen_count     = sum(1 for ac in aircrafts
                             if ac.origin is not None and ac.origin.Schengen)
    non_schengen_count = len(aircrafts) - schengen_count

    plt.figure(figsize=(6, 6))
    plt.bar(['Flights'], [schengen_count], color='green', edgecolor='black',
            width=0.4, label='Schengen')
    plt.bar(['Flights'], [non_schengen_count], bottom=[schengen_count],
            color='red', edgecolor='black', width=0.4, label='non-Schengen')
    plt.title('Type of Flights: Schengen vs non-Schengen')
    plt.xlabel('Origin Region')
    plt.ylabel('Number of Aircrafts')
    plt.text(0, schengen_count / 2, str(schengen_count),
             ha='center', va='center', fontweight='bold', color='white')
    plt.text(0, schengen_count + (non_schengen_count / 2), str(non_schengen_count),
             ha='center', va='center', fontweight='bold', color='white')
    plt.legend()
    plt.show()


def MapFlights(aircrafts):
    # Genera un fichero KML con las trayectorias de todos los vuelos hacia LEBL.
    # Schengen en verde, no Schengen en rojo.
    if not aircrafts:
        print("Error: No hay datos de vuelos para generar el mapa.")
        return

    lebl_lat = 41.29694
    lebl_lon = 2.07833

    with open("flights_map.kml", "w") as f:
        f.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        f.write("<Document>\n")
        f.write("  <name>Flight Trajectories to LEBL</name>\n")
        f.write("  <Style id=\"SchengenLine\">\n")
        f.write("    <LineStyle><color>ff00ff00</color><width>2</width></LineStyle>\n")
        f.write("  </Style>\n")
        f.write("  <Style id=\"NonSchengenLine\">\n")
        f.write("    <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>\n")
        f.write("  </Style>\n")

        for ac in aircrafts:
            origin_ap = ac.origin
            if origin_ap is not None:
                f.write("  <Placemark>\n")
                f.write(f"    <name>{ac.Id} - {origin_ap.ICAO}</name>\n")
                style = "SchengenLine" if origin_ap.Schengen else "NonSchengenLine"
                f.write(f"    <styleUrl>#{style}</styleUrl>\n")
                f.write("    <LineString>\n")
                f.write("      <altitudeMode>clampToGround</altitudeMode>\n")
                f.write("      <tessellate>1</tessellate>\n")
                f.write("      <coordinates>\n")
                f.write(f"        {origin_ap.longitude},{origin_ap.latitude}\n")
                f.write(f"        {lebl_lon},{lebl_lat}\n")
                f.write("      </coordinates>\n")
                f.write("    </LineString>\n")
                f.write("  </Placemark>\n")

        f.write("</Document>\n")
        f.write("</kml>\n")

    try:
        os.startfile("flights_map.kml")
    except:
        print("KML generado, pero Google Earth no pudo abrirse automáticamente.")


def LongDistanceArrivals(aircrafts):
    # Devuelve una lista con los vuelos que provienen de más de 2000 km de LEBL
    if not aircrafts:
        return []

    lat_lebl = 41.29694
    lon_lebl = 2.07833
    R = 6371.0

    long_distance_flights = []

    for ac in aircrafts:
        origin_ap = ac.origin
        if origin_ap is not None:
            phi1     = math.radians(origin_ap.latitude)
            phi2     = math.radians(lat_lebl)
            d_phi    = math.radians(lat_lebl - origin_ap.latitude)
            d_lambda = math.radians(lon_lebl - origin_ap.longitude)
            a = (math.sin(d_phi / 2)**2 +
                 math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            if R * c > 2000:
                long_distance_flights.append(ac)

    return long_distance_flights


# ---------------------------------------------------------------------------
# Funciones V4 — Nuevas
# ---------------------------------------------------------------------------

def LoadDepartures(filename):
    # Lee el fichero de salidas y devuelve una lista de Aircraft.
    # Solo rellena Id, Company, Destination y DepartureTime. origin y time quedan None.
    aircrafts = []
    try:
        with open(filename, 'r') as f:
            next(f)         # Salta la cabecera
            for line in f:
                elementos = line.split()

                # Necesitamos al menos 4 columnas: ID, DESTINATION, DEPARTURE, AIRLINE
                if len(elementos) < 4:
                    continue

                aircraft_id = elementos[0]  # Ej: "ECMKV"
                destination = elementos[1]  # Ej: "LYBE" (código ICAO destino)
                departure   = elementos[2]  # Ej: "04:58" (hora de salida)
                airline     = elementos[3]  # Ej: "VLG"

                # Validación del formato de la hora de salida
                time_parts = departure.split(":")
                if len(time_parts) != 2:
                    continue
                try:
                    hour   = int(time_parts[0])
                    minute = int(time_parts[1])
                    if not (0 <= hour < 24 and 0 <= minute < 60):
                        continue
                except ValueError:
                    continue

                # origin=None y time=None porque este fichero solo tiene datos de salida
                # dest y dtime sí los rellenamos con los datos del fichero
                aircraft = Aircraft(aircraft_id, airline, None, None, destination, departure)
                aircrafts.append(aircraft)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []

    return aircrafts


def MergeMovements(arrivals, departures):
    # Combina llegadas y salidas: mismo ID + salida posterior a llegada → un solo Aircraft.
    # Aviones sin salida compatible se conservan. Aviones sin llegada = nocturnos.

    if not arrivals or not departures:
        return -1   # Si alguna lista está vacía → error code

    merged = []

    # Lista de booleanos para controlar qué salidas ya han sido emparejadas
    # False = disponible, True = ya emparejada con una llegada
    used = [False] * len(departures)

    # Paso 1: Para cada llegada, intentar encontrar una salida compatible
    for arrival in arrivals:
        # Convertir hora de llegada a minutos para poder comparar numéricamente
        # Ej: "07:28" → 7*60 + 28 = 448 minutos
        # CAMBIO: añadido try-except por si arrival.time tiene formato inválido
        try:
            arr_parts = arrival.time.split(":")
            arr_min   = int(arr_parts[0]) * 60 + int(arr_parts[1])
        except (ValueError, AttributeError):
            # Si el tiempo de llegada es inválido, conservamos el avión sin emparejar
            merged.append(arrival)
            continue

        best_idx  = -1              # Índice de la mejor salida encontrada
        best_time = float('inf')    # Tiempo de la mejor salida (buscamos la más cercana)

        for i, dep in enumerate(departures):
            # Solo consideramos salidas no usadas y del mismo avión
            if used[i] or dep.Id != arrival.Id:
                continue

            # Convertir hora de salida a minutos
            # CAMBIO: añadido try-except por si dep.DepartureTime tiene formato inválido
            try:
                dep_parts = dep.DepartureTime.split(":")
                dep_min   = int(dep_parts[0]) * 60 + int(dep_parts[1])
            except (ValueError, AttributeError):
                continue    # Salida con tiempo inválido → saltamos esta salida

            # Compatible: la salida debe ser POSTERIOR a la llegada
            # Y elegimos la más cercana (greedy) para dejar las más lejanas
            # disponibles para posibles llegadas posteriores del mismo avión
            if dep_min > arr_min and dep_min < best_time:
                best_time = dep_min
                best_idx  = i

        if best_idx != -1:
            # Emparejamiento encontrado → fusionar llegada + salida en un solo Aircraft
            dep            = departures[best_idx]
            used[best_idx] = True   # Marcar esta salida como usada

            merged_ac = Aircraft(
                arrival.Id,
                arrival.Company,
                arrival.origin,
                arrival.time,           # Hora de llegada (del objeto arrival)
                dep.Destination,        # Destino (del objeto departure)
                dep.DepartureTime       # Hora de salida (del objeto departure)
            )
            merged.append(merged_ac)
        else:
            # Sin salida compatible → mantener solo con datos de llegada
            merged.append(arrival)

    # Paso 2: Añadir las salidas no emparejadas (aviones nocturnos)
    # Son aviones que pasaron la noche en el aeropuerto y salen hoy
    # pero no tienen llegada registrada en el día de hoy
    for i, dep in enumerate(departures):
        if not used[i]:
            merged.append(dep)

    return merged


def NightAircraft(aircrafts):
    # Devuelve los aviones nocturnos: sin llegada (time=None) pero con salida registrada.
    if not aircrafts:
        return -1   # Lista vacía → error code

    # Lista por comprensión: filtra los aviones sin llegada pero con salida
    return [ac for ac in aircrafts
            if ac.time is None and ac.DepartureTime is not None]


# ---------------------------------------------------------------------------
# Sección de pruebas — Actualizada con los tests de V4
# Este bloque SOLO se ejecuta cuando corres aircraft.py directamente
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("      aircraft.py — Sección de pruebas V4")
    print("=" * 55)

    # --- Tests V2 (sin cambios) ---
    print("\n[V2] Cargando aeropuertos y llegadas...")
    airports  = LoadAirports("Airports.txt")
    print(f"  Airports loaded: {len(airports)}")
    aircrafts = LoadArrivals("Arrivals.txt", airports)
    print(f"  Arrivals loaded: {len(aircrafts)}")

    print("\n[V2] Test PlotArrivals (cerrar ventana para continuar)...")
    PlotArrivals(aircrafts)

    result = SaveFlights(aircrafts, "output.txt")
    print(f"\n[V2] SaveFlights: {'OK → output.txt creado' if result == 0 else 'ERROR'}")

    print("\n[V2] Test PlotAirlines (cerrar ventana para continuar)...")
    PlotAirlines(aircrafts)

    print("\n[V2] Test PlotFlightsType (cerrar ventana para continuar)...")
    PlotFlightsType(aircrafts)

    print("\n[V2] Test MapFlights (todos los vuelos)...")
    MapFlights(aircrafts)

    long_flights = LongDistanceArrivals(aircrafts)
    print(f"\n[V2] LongDistanceArrivals: {len(long_flights)} vuelos >2000km")
    MapFlights(long_flights)

    # --- Tests V4 ---
    print("\n" + "=" * 55)
    print("      Tests nuevos V4")
    print("=" * 55)

    # --- Test LoadDepartures ---
    print("\n[V4-1] Test LoadDepartures")
    departures = LoadDepartures("Departures.txt")
    print(f"  Departures loaded: {len(departures)}")

    # Verificamos que los campos de llegada son None y los de salida tienen datos
    if departures:
        d = departures[0]
        print(f"  Primer avión: ID={d.Id}, Destino={d.Destination}, "
              f"Salida={d.DepartureTime}, Llegada={d.time} → esperado None")

    # Test fichero inexistente → debe devolver lista vacía
    dep_err = LoadDepartures("fichero_inexistente.txt")
    print(f"  Fichero inexistente: {dep_err} → esperado []")

    # --- Test MergeMovements ---
    print("\n[V4-2] Test MergeMovements")
    merged = MergeMovements(aircrafts, departures)
    if merged == -1:
        print("  ERROR: alguna lista estaba vacía")
    else:
        print(f"  Total movimientos fusionados: {len(merged)}")

        # Contamos cuántos tienen información completa (llegada + salida)
        complete = sum(1 for ac in merged
                       if ac.time is not None and ac.DepartureTime is not None)
        only_arr = sum(1 for ac in merged
                       if ac.time is not None and ac.DepartureTime is None)
        only_dep = sum(1 for ac in merged
                       if ac.time is None and ac.DepartureTime is not None)

        print(f"  Con llegada Y salida:    {complete}")
        print(f"  Solo llegada (sin salida): {only_arr}")
        print(f"  Solo salida (nocturnos):   {only_dep}")

    # Test con lista vacía → debe devolver -1
    result_err = MergeMovements([], departures)
    print(f"  Lista vacía: {result_err} → esperado -1")

    # --- Test NightAircraft ---
    print("\n[V4-3] Test NightAircraft")
    if merged != -1:
        night = NightAircraft(merged)
        if night == -1:
            print("  ERROR: lista vacía")
        else:
            print(f"  Aviones nocturnos encontrados: {len(night)}")
            if night:
                # Verificamos que realmente no tienen hora de llegada
                n = night[0]
                print(f"  Primer nocturno: ID={n.Id}, "
                      f"Llegada={n.time} → esperado None, "
                      f"Salida={n.DepartureTime}")

    # Test con lista vacía → debe devolver -1
    result_err = NightAircraft([])
    print(f"  Lista vacía: {result_err} → esperado -1")

    print("\n" + "=" * 55)
    print("      Pruebas completadas")
    print("=" * 55)