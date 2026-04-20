import matplotlib.pyplot as plt
import os
#No sé si se puede utilizar el import os, esto es para abrir el Google Earth de manera automática

class Airport:
    def __init__(self, code, lat, lon): #Hay que poner 2 barras bajas para esta función
        self.ICAO = code #Para facilitar la definición, hay que dejarlo en este formato, así podremos definir ICAO, latitude, longitude en el mismo parentesis (como el step2)
        self.latitude = lat
        self.longitude = lon
        self.Schengen = False

llistaSchengen = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH','BI','LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES','LS']

def IsSchengenAirport(code):
    if not code: #If the input parameter is empty then False is returned.
        return False
    pertenece = False
    i = 0
    while pertenece == False and i < len(llistaSchengen):
        if code[0:2].upper() == llistaSchengen[i]: # Para leer solo los 2 primeros caracteres de un str, hay que poner [0:2]. (Esta función funciona sin perteneciendo el último carácter, osea, así"[)")
            pertenece = True
            return pertenece
        i = i + 1
    return False

def SetSchengen (airport): #lo que hace por aquí es definir el elemento Schengen del aeropuerto.
    airport.Schengen = IsSchengenAirport(airport.ICAO)

def PrintAirport (airport):
    print(airport.__dict__) #Esto es una función de "clase", lo que hace es escribir todos los elementos que hemos definido. (en el test_airport (hace prueba a todas estas funciones) se ve mejor)

def LoadAirports (filename):
    F = open(filename, 'r')
    linea = F.readline()
    airports = []
    while linea != "":
        linea = F.readline()
        elementos = linea.split() #trata por defecto cualquier secuencia de espacios en blanco como un solo separador, resolviendo problemas de alineación.
        if len(elementos) >= 3: #Para evitar líneas en espacios que salga errores
            lat = elementos[1]
            lon = elementos[2]
            lati = float(lat[1:3]) + (float(lat[3:5]) / 60) + (float(lat[5:7]) / 3600)
            long = float(lon[1:3]) + (float(lon[3:5]) / 60) + (float(lon[5:7]) / 3600)
            if lat[0] == "S":
                lati = lati * -1
            if lon[0] == "W":
                long = long * -1

            new_airport = Airport(elementos[0], lati, long)
            SetSchengen(new_airport)
            airports.append(new_airport)
    F.close()
    return airports

def SaveSchengenAirports(airports, filename):
    f = open(filename, "w")

    f.write("ICAO\tLatitude\tLongitude\n")

    i = 0
    encontrado = False
    while i < len(airports):
        SetSchengen(airports[i])
        if airports[i].Schengen == True:
            encontrado = True
            lat = airports[i].latitude
            lon = airports[i].longitude
            if lat >= 0:
                letra_lat = "N"
            else:
                letra_lat = "S"
                lat = lat * -1
            if lon >= 0:
                letra_lon = "E"
            else:
                letra_lon = "W"
                lon = lon * -1
            # Recorda que el int quita los decimales, a través de esto pasamos de grados en min y segundos
            deg_lat = int(lat)
            min_lat = int((lat - deg_lat) * 60)
            sec_lat = int(round((lat - deg_lat - min_lat / 60) * 3600)) # round es igual a arondonir

            deg_lon = int(lon)
            min_lon = int((lon - deg_lon) * 60)
            sec_lon = int(round((lon - deg_lon - min_lon / 60) * 3600))
            # para cuando sec = 60 no de error, y que quede en 59
            if sec_lat >= 60:
                sec_lat = 0
                min_lat = min_lat + 1

            if sec_lon >= 60:
                sec_lon = 0
                min_lon = min_lon + 1

            # Ponemos zill fill para que los números de una unidad ponga 0N
            str_lat = letra_lat + str(deg_lat).zfill(2) + str(min_lat).zfill(2) + str(sec_lat).zfill(2)
            str_lon = letra_lon + str(deg_lon).zfill(2) + str(min_lon).zfill(2) + str(sec_lon).zfill(2)

            linea = airports[i].ICAO + "\t" + str_lat + "\t" + str_lon + "\n"
            f.write(linea)

        i = i + 1

    f.close()
    return encontrado

def AddAirport(airports, airport):
    i = 0
    encontrado = False
    while i < len(airports) and encontrado == False:
        if airport.ICAO == airports[i].ICAO:
            print(f"The airport {airport.ICAO} is in the list ")
            encontrado = True
            return False
        i = i + 1
    if encontrado == False:
        airports.append(airport)
    return True


def RemoveAirport(airports, code): # En el versión 4 se puede cambiar por un remove
    encontrado = False
    i = 0
    while i < len(airports) and encontrado == False:
        if code.upper() == airports[i].ICAO: # podemos utilizar upper() para que el code introducido sea en mayúsculas
            j = i
            while j < len(airports) - 1:
                airports[j] = airports[j + 1]
                j = j + 1
            airports[:] = airports[:-1] # Esta línea hace que el numero de espacios de la lista disminuya uno, ósea, len(airports) - 1
            encontrado = True
        i = i + 1
    if not encontrado:
        print(f"Error: Airport {code} not found.")
        return False
    return True


def PlotAirports(airports):
    schengen_count = 0
    non_schengen_count = 0

    i = 0
    while i < len(airports):
        SetSchengen(airports[i])
        if airports[i].Schengen == True:
            schengen_count = schengen_count + 1
        else:
            non_schengen_count = non_schengen_count + 1
        i = i + 1

    labels = ['Airports'] # nombre de eje x
    plt.ylabel('Number of Airports') # nombre de eje y
    plt.title('Schengen vs Non-Schengen') # nombre del título
    plt.bar(labels, [schengen_count], label='Schengen', color='blue') # Crea primero la parte schengen
    plt.bar(labels, [non_schengen_count], bottom=[schengen_count], label='Non-Schengen', color='red') # bottom=[schengen_count] define que està arriba de parte schengen
    plt.legend()
    plt.show()


def MapAirports(airports):
    f = open("airports_map.kml", "w")
    #La estructura de programación de KML está explicado en el apartado Annex 1
    # en las siguientes lineas ponemos espacios para que quede más bonito el documento KML
    f.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
    f.write("<Document>\n")

    #define un color para los países de schengen y otro para los países no schengen
    f.write("  <Style id=\"SchengenStyle\">\n")
    f.write("    <IconStyle><color>ff00ff00</color></IconStyle>\n")
    f.write("  </Style>\n")

    f.write("  <Style id=\"NonSchengenStyle\">\n")
    f.write("    <IconStyle><color>ff0000ff</color></IconStyle>\n")
    f.write("  </Style>\n")

    #crea un bucle para escribir el documento KML
    i = 0
    while i < len(airports):
        SetSchengen(airports[i])
        #Nombra el punto
        f.write("  <Placemark>\n")
        f.write("    <name>" + airports[i].ICAO + "</name>\n")

        #Defini el color de ese punto
        if airports[i].Schengen == True:
            f.write("    <styleUrl>#SchengenStyle</styleUrl>\n")
        else:
            f.write("    <styleUrl>#NonSchengenStyle</styleUrl>\n")

        #Ubica el punto
        f.write("    <Point>\n")
        f.write("      <coordinates>\n")
        coords_line = "        " + str(airports[i].longitude) + "," + str(airports[i].latitude) + "\n"
        f.write(coords_line)
        f.write("      </coordinates>\n")
        f.write("    </Point>\n")
        f.write("  </Placemark>\n")
        i = i + 1

    f.write("</Document>\n")
    f.write("</kml>\n")
    f.close()
    filename = "airports_map.kml"
    try: #Para que no de error cuando el usuario no ha descargado el Google Earth
        os.startfile("airports_map.kml")
    except:
        print("Map saved, but could not open Google Earth automatically.")
    # No sé si se puede utilizar el import os, esto es para abrir el Google Earth de manera automática