import matplotlib.pyplot as plt
import math
import os
from airport import *

class Aircraft:
    def __init__(self, id, comp, origin,time):
        self.Id = id
        self.Company = comp
        self.origin = origin #Importante este hay que poner los aeropuertos que están definidos en versión 1!!
        self.time = time

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
        i = i + 1


    categories = ['Schengen', 'non-Schengen']
    counts = [schengen_count, non_schengen_count]


    #pyplot
    plt.figure(figsize=(8, 6))

    plt.bar(categories, counts, color=['green', 'red'], edgecolor='black', width=0.6)

    plt.title('Type of Flights: Schengen vs non-Schengen')
    plt.xlabel('Origin Region')
    plt.ylabel('Number of Aircrafts')

    plt.text(0, schengen_count + 0.1, str(schengen_count), ha='center', fontweight='bold')
    plt.text(1, non_schengen_count + 0.1, str(non_schengen_count), ha='center', fontweight='bold')

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

    return long_distance_flights


# test section

if __name__ == "__main__":
    airports = LoadAirports("Airports.txt")
    aircrafts = LoadArrivals("arrivals.txt", airports)
    #Hemos añadido 2 variables en la función de Loadaircrafts, por la tanto, lo tenemos que definir así
    PlotArrivals(aircrafts)
    SaveFlights(aircrafts, "file")
    PlotAirlines(aircrafts)
    PlotFlightsType(aircrafts)
    MapFlights(aircrafts)
    LongDistanceArrivals(aircrafts)

