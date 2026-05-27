import matplotlib.pyplot as plt
import math
import os

from fontTools.misc.textTools import deHexStr

from airport import *

class Aircraft:
    def __init__(self, id, comp, origin,time, dest, dtime):
        self.Id = id
        self.Company = comp
        self.origin = origin #Importante este hay que poner los aeropuertos que están definidos en versión 1!!
        self.time = time
        self.Destination = dest
        self.DepartureTime = dtime

# CONDICIONES IMPORTANTE PARA LOADARRIVALS:
#In the file you will not find all data defined in the structure Aircraft, so update only the fields of the structure you can.
# In case some of the aircraft lines do not have a correct time or the expected structure, then the function must skip this line and proceed with the rest of lines in the file. Note that the arrivals
# file is sorted by landing time.
#CON ESTAS CONDICIONES CONSIDERAMOS QUE:
#     · La información que nos da el documento puede haber errores de estructuras o falta de información
#     · Necessitamos identificar la estructura de cada elemento partido por split para assegurar de qué categoría es.
#     · Consideramos categorias con elementos vaciás como None
#     · Consideramos que tenemos que saltar la linea directamente cuando la estructura de las categorias es incorrecta

def LoadArrivals(filename, airports):
    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        return []

    line = f.readline()
    aircrafts = []
    last_time_in_minutes = -1 #lo utilizamos para contar el tiempo (explicado en la linea 45)

    line = f.readline()
    while line != "":
        elementos = line.split()
        buscador_de_errores = False
        if len(elementos) >= 2 and buscador_de_errores == False: # Aunque dice que falte dadas, el ID y el tiempo serán las informaciones mínimas necessaria para assegurar las otras funciones funcione bien
            id = elementos[0]  #Inducimos que el documento siempre tendrá ID en la primera posición, ya que no tiene una estructura uniformada, además es la información mínima para una aerolinea
            origin = None
            arrival = None
            airline = None
            i = 1 #Comenzamos desde 1 porque el 0 ya esta definido
            #indentificar los elementos divididos
            while i < len(elementos) and buscador_de_errores == False:
                item = elementos[i]
                if ":" in item:
                    arrival = item
                elif len(item) == 4 and item.isupper(): #A través del número de letras y el formato mayúsculas indentificar si la estructura es correcta
                    origin = item
                elif len(item) == 3 and item.isupper():
                    airline = item
                else:
                    buscador_de_errores = True
                i = i + 1

            # Comprovamos si el tiempo es coherente (más tarde que la linea anterior y más temprano que la siguiente linea)
            if arrival is not None and buscador_de_errores == False:
                #Para comparar pasamos el tiempo en minutos
                time_parts = arrival.split(":")
                if len(time_parts) == 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    current_total_minutes = hour * 60 + minute
                    if 0 <= hour < 24 and 0 <= minute < 60 and current_total_minutes >= last_time_in_minutes:
                        found_ap_obj = None
                        j = 0
                        encontrado = False
                        while j < len(airports) and encontrado == False:
                            if airports[j].ICAO == origin:
                                found_ap_obj = airports[j]
                                encontrado = True
                            j = j + 1
                        aircraft = Aircraft(id, airline, found_ap_obj, arrival)
                        aircrafts.append(aircraft)

                        last_time_in_minutes = current_total_minutes
        line = f.readline()

    f.close()
    return aircrafts


def PlotArrivals(aircrafts):
    if len(aircrafts) == 0:
        print("Error: llista buida")
        return

    hours = [0] * 24

    for aircraft in aircrafts:
        if aircraft.time is not None and aircraft.time != "":
            try:
                parts = aircraft.time.split(":")
                if len(parts) >= 1:
                    hour_val = int(parts[0])
                    if 0 <= hour_val <= 23:
                        hours[hour_val] = hours[hour_val] + 1
            except ValueError:
                pass

    plt.bar(range(24), hours)
    plt.xlabel("Hour")
    plt.ylabel("Arrivals")
    plt.title("Arrivals per hour")
    plt.show()

def SaveFlights(aircrafts, filename): #Esta parte creo que se puede simplificar con la funcion de ind si es schen o no de V.1
    if not aircrafts:
        return -1
    f=open(filename,"w")
    f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
    i=0
    while i < len(aircrafts):
        if aircrafts[i].origin:
            origin_ap = aircrafts[i].origin.ICAO
        else:
            origin_ap="-"
        if aircrafts[i].Id:
            aircraft_id=aircrafts[i].Id
        else:
            aircraft_id="-"
        if aircrafts[i].time:
            arrival_time=aircrafts[i].time
        else:
            arrival_time="0"
        if aircrafts[i].Company:
            company=aircrafts[i].Company
        else:
            company="-"
        linea=aircraft_id + " " + origin_ap + " " + arrival_time +" " + company + "\n"
        f.write(linea)
        i = i+1
    f.close()
    return 0

def PlotAirlines(aircrafts): #la gràfica no cabe ne la interface
    if not aircrafts:
        print("Error: llista buida")
        return
    airlines = {} #Diccionario!!! NO LISTA, NO TOQUÉIS!!!
    i = 0
    while i < len(aircrafts):
        company = aircrafts[i].Company

        if company in airlines:
            airlines[company] = airlines[company] + 1
        else:
            airlines[company] = 1

        i = i + 1

    names = list(airlines.keys())
    values = list(airlines.values())
    index = list(range(1, len(names) + 1))

    # A partir de aquí ya viene lo visual:
    # 1. Tamaño ancho pero no muy alto para que deje espacio a la leyenda abajo
    plt.figure(figsize=(10, 5))

    barres = plt.bar(index, values)
    plt.title("Flights per Airline", fontsize=14, pad=10)
    plt.xlabel("Airline Index", fontsize=11)
    plt.ylabel("Number of Flights", fontsize=11)

    # 2. LA CLAVE: Hacemos la fuente muy pequeña y rotamos los números 90 grados
    # para que se lean en vertical y no se superpongan.
    plt.xticks(index, fontsize=7, rotation=90)

    llegenda_textos = []
    j = 0
    while j < len(names):
        text_element = str(index[j]) + ": " + str(names[j])
        llegenda_textos.append(text_element)
        j = j + 1

    # 3. Ponemos la leyenda debajo del gráfico, con 6 columnas y letra pequeña
    plt.legend(barres, llegenda_textos, ncol=6, fontsize=7,
               bbox_to_anchor=(0.5, -0.25), loc='upper center')

    # 4. Ajuste automático de márgenes para que no se corte nada
    plt.tight_layout()

    plt.show()
    return 0

def PlotFlightsType(aircrafts):
    if len(aircrafts) == 0:
        print("Error: The aircraft list is empty. No plot will be shown.")
        return

    schengen_count = 0
    non_schengen_count = 0
    i = 0

    while i < len(aircrafts):
        if aircrafts[i].origin is not None:
            if aircrafts[i].origin.Schengen == True:
                schengen_count = schengen_count + 1
            else: #Consideramos automaticamente los aeropuertos sin origin como non schengen_count
                non_schengen_count = non_schengen_count + 1
        else:
            non_schengen_count = non_schengen_count + 1
        i = i + 1


    #pyplot
    plt.figure(figsize=(6, 6))

    plt.bar(['Flights'], [schengen_count], color='green', edgecolor='black', width=0.4, label='Schengen')
    plt.bar(['Flights'], [non_schengen_count], bottom=[schengen_count], color='red', edgecolor='black', width=0.4, label='non-Schengen')

    plt.title('Type of Flights: Schengen vs non-Schengen')
    plt.xlabel('Origin Region')
    plt.ylabel('Number of Aircrafts')

    plt.text(0, schengen_count / 2, str(schengen_count), ha='center', va='center', fontweight='bold', color='white')
    plt.text(0, schengen_count + (non_schengen_count / 2), str(non_schengen_count), ha='center', va='center', fontweight='bold', color='white')

    plt.legend()
    plt.show()

def MapFlights(aircrafts):
    # Comprobación defensiva inicial: si la lista está vacía, no tiene sentido generar el KML
    if len(aircrafts) == 0:
        print("Error: No hay datos de vuelos para generar el mapa.")
        return

    lebl_lat = 41.29694
    lebl_lon = 2.07833

    # Example 1 line pàg 17, similar al versión 1 (que es de puntos)
    f = open("flights_map.kml", "w")

    f.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
    f.write("<Document>\n")
    f.write("  <name>Flight Trajectories to LEBL</name>\n")

    f.write("  <Style id=\"SchengenLine\">\n")
    f.write("    <LineStyle><color>ff00ff00</color><width>2</width></LineStyle>\n")
    f.write("  </Style>\n")

    f.write("  <Style id=\"NonSchengenLine\">\n")
    f.write("    <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>\n")
    f.write("  </Style>\n")

    i = 0
    while i < len(aircrafts):
        ac = aircrafts[i]
        origin_ap = ac.origin

        # Protección defensiva: solo dibujamos si tenemos la información del aeropuerto de origen
        if origin_ap is not None:
            f.write("  <Placemark>\n")
            # Usamos ac.Id y origin_ap.ICAO
            f.write("    <name>" + str(ac.Id) + " - " + str(origin_ap.ICAO) + "</name>\n")

            # Comprobamos la zona Schengen para el estilo
            if origin_ap.Schengen == True:
                f.write("    <styleUrl>#SchengenLine</styleUrl>\n")
            else:
                f.write("    <styleUrl>#NonSchengenLine</styleUrl>\n")

            f.write("    <LineString>\n")
            f.write("      <altitudeMode>clampToGround</altitudeMode>\n")
            f.write("        <tessellate>1</tessellate>\n")
            f.write("           <coordinates>\n")

            line_coords = f"        {origin_ap.longitude},{origin_ap.latitude}\n"
            line_coords += f"        {lebl_lon},{lebl_lat}\n"

            f.write(line_coords)
            f.write("           </coordinates>\n")
            f.write("    </LineString>\n")
            f.write("  </Placemark>\n")

        i = i + 1

    f.write("</Document>\n")
    f.write("</kml>\n")
    f.close()

    try:
        import os
        os.startfile("flights_map.kml")
    except:
        print("KML generado, pero Google Earth no pudo abrirse automáticamente.")

def LongDistanceArrivals(aircrafts):
    # Comprobación defensiva: si no hay vuelos, devolvemos una lista vacía
    if len(aircrafts) == 0:
        return []

    lat_lebl = 41.29694
    lon_lebl = 2.07833
    R = 6371.0

    long_distance_flights = []

    i = 0
    while i < len(aircrafts):
        ac = aircrafts[i]
        origin_ap = ac.origin

        # Protección defensiva: si el aeropuerto es None, no podemos calcular la distancia
        if origin_ap is not None:
            lat_origen = origin_ap.latitude
            lon_origen = origin_ap.longitude

            # Calcular Haversine distance, pág 18 está la fórmula esta rara
            phi1 = math.radians(lat_origen)
            phi2 = math.radians(lat_lebl)
            d_phi = math.radians(lat_lebl - lat_origen)
            d_lambda = math.radians(lon_lebl - lon_origen)

            # Corregimos la fórmula de Haversine para que sea matemáticamente correcta
            a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c

            if distance > 2000:
                long_distance_flights.append(ac)

        i = i + 1

    # --- Generación de KML para Google Earth exclusivo de Larga Distancia ---
    if len(long_distance_flights) > 0:
        f = open("long_distance_flights.kml", "w")
        f.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        f.write("<Document>\n")
        f.write("  <name>Long Distance Flight Trajectories to LEBL</name>\n")

        f.write("  <Style id=\"SchengenLine\">\n")
        f.write("    <LineStyle><color>ff00ff00</color><width>2</width></LineStyle>\n")
        f.write("  </Style>\n")

        f.write("  <Style id=\"NonSchengenLine\">\n")
        f.write("    <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>\n")
        f.write("  </Style>\n")

        j = 0
        while j < len(long_distance_flights):
            ac = long_distance_flights[j]
            origin_ap = ac.origin

            if origin_ap is not None:
                f.write("  <Placemark>\n")
                f.write("    <name>" + str(ac.Id) + " - " + str(origin_ap.ICAO) + "</name>\n")

                if origin_ap.Schengen == True:
                    f.write("    <styleUrl>#SchengenLine</styleUrl>\n")
                else:
                    f.write("    <styleUrl>#NonSchengenLine</styleUrl>\n")

                f.write("    <LineString>\n")
                f.write("      <altitudeMode>clampToGround</altitudeMode>\n")
                f.write("        <tessellate>1</tessellate>\n")
                f.write("           <coordinates>\n")

                line_coords = f"        {origin_ap.longitude},{origin_ap.latitude}\n"
                line_coords += f"        {lon_lebl},{lat_lebl}\n"  # <-- Corregido para usar las variables correctas de esta función

                f.write(line_coords)
                f.write("           </coordinates>\n")
                f.write("    </LineString>\n")
                f.write("  </Placemark>\n")
            j = j + 1

        f.write("</Document>\n")
        f.write("</kml>\n")
        f.close()

        try:
            import os
            os.startfile("long_distance_flights.kml")
        except:
            print("KML de larga distancia generado, pero Google Earth no pudo abrirse automáticamente.")

    return long_distance_flights


#Version 4

def LoadDepartures(filename):

    if not os.path.exists(filename):
        return [], -1

    departures_list = []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            header = f.readline()

            line = f.readline()
            while line != "":
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 4:
                        ac_id = parts[0].strip()
                        dest = parts[1].strip()
                        dep_time = parts[2].strip()
                        airline = parts[3].strip()

                        ac = Aircraft(aircraft_id=ac_id, company=airline)
                        ac.Destination = dest
                        ac.DepartureTime = dep_time

                        departures_list.append(ac)
                line = f.readline()

        return departures_list, 0
    except:
        return [], -1


def MergeMovements(arrivals, departures):
    if not arrivals or not departures:
        return -1

    merged_list = []
    used_departures = set()

    def time_to_minutes(t_str):
        if not t_str or ":" not in t_str:
            return 0
        h, m = map(int, t_str.split(":"))
        return h * 60 + m

    for arr_ac in arrivals:
        new_ac = Aircraft(arr_ac.Id,arr_ac.Company,arr_ac.ArrivalTime,arr_ac.origin)

        matched_dep = None
        for dep_ac in departures:
            if dep_ac.Id == arr_ac.Id and dep_ac not in used_departures:
                arr_min = time_to_minutes(arr_ac.ArrivalTime)
                dep_min = time_to_minutes(dep_ac.DepartureTime)

                if arr_min < dep_min:
                    matched_dep = dep_ac
                    break

        if matched_dep:
            new_ac.Destination = matched_dep.Destination
            new_ac.DepartureTime = matched_dep.DepartureTime
            used_departures.add(matched_dep)

        merged_list.append(new_ac)

    for dep_ac in departures:
        if dep_ac not in used_departures:
            night_ac = Aircraft(dep_ac.Id, dep_ac.Company)
            night_ac.Destination = dep_ac.Destination
            night_ac.DepartureTime = dep_ac.DepartureTime
            merged_list.append(night_ac)

    return merged_list


def NightAircraft(aircrafts):
    if not aircrafts:
        return -1

    night_list = []
    for ac in aircrafts:
        if (ac.ArrivalTime == "" or ac.ArrivalTime is None) and ac.DepartureTime != "":
            night_list.append(ac)

    return night_list

# test section

if __name__ == "__main__":
    airports = LoadAirports("Airports.txt")
    aircrafts = LoadArrivals("arrivals.txt", airports)
    PlotArrivals(aircrafts)
    SaveFlights(aircrafts, "file")
    PlotAirlines(aircrafts)
    PlotFlightsType(aircrafts)
    MapFlights(aircrafts)
    LongDistanceArrivals(aircrafts)