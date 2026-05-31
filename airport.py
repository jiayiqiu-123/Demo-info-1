import matplotlib.pyplot as plt
import os

# Clase que representa un aeropuerto con sus datos básicos
class Airport:
    def __init__(self, code, lat, lon):
        self.ICAO = code        # Código ICAO del aeropuerto (4 caracteres, ej: LEBL)
        self.latitude = lat     # Latitud en grados decimales (positivo = Norte, negativo = Sur)
        self.longitude = lon    # Longitud en grados decimales (positivo = Este, negativo = Oeste)
        self.Schengen = False   # Por defecto no es Schengen, se actualiza con SetSchengen()

# Conjunto de prefijos ICAO que pertenecen a países del espacio Schengen
# Usamos {} en vez de [] porque es un "set": más rápido para buscar elementos con "in"
llistaSchengen = {'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH',
                  'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE',
                  'ES', 'LS'}

def IsSchengenAirport(code):
    # Recibe un código ICAO y devuelve True si el aeropuerto está en un país Schengen
    if not code:                            # Si el código está vacío, devuelve False directamente
        return False
    return code[:2].upper() in llistaSchengen
    # code[:2] coge solo los 2 primeros caracteres del código (ej: "LEBL" → "LE")
    # .upper() lo convierte a mayúsculas por si acaso el usuario escribe en minúsculas
    # "in llistaSchengen" comprueba si esos 2 caracteres están en el conjunto Schengen

def SetSchengen(airport):
    # Recibe un objeto Airport y actualiza su atributo Schengen (True o False)
    # Llama a IsSchengenAirport() para saber si el aeropuerto es Schengen o no
    airport.Schengen = IsSchengenAirport(airport.ICAO)

def PrintAirport(airport):
    # Imprime por consola los datos de un aeropuerto de forma legible
    # :.4f significa que imprime el número con 4 decimales (ej: 41.2974)
    print(f"ICAO: {airport.ICAO} | Lat: {airport.latitude:.4f} | "
          f"Lon: {airport.longitude:.4f} | Schengen: {airport.Schengen}")

def LoadAirports(filename):
    # Abre un fichero de texto con aeropuertos y devuelve una lista de objetos Airport
    # El fichero tiene el formato: CODE LAT LON (con cabecera en la primera línea)
    # Si el fichero no existe, devuelve una lista vacía
    try:
        with open(filename, 'r') as F:  # Abre el fichero en modo lectura ('r' = read)
            next(F)                     # Salta la primera línea (cabecera: "CODE LAT LON")
            airports = []
            for linea in F:             # Recorre todas las líneas del fichero una a una
                elementos = linea.split()   # Separa la línea por espacios → ["LEBL", "N411749", "E0020442"]
                if len(elementos) >= 3:     # Evita errores si hay líneas vacías o incompletas
                    lat = elementos[1]      # Coge el segundo elemento (latitud), ej: "N411749"
                    lon = elementos[2]      # Coge el tercer elemento (longitud), ej: "E0020442"

                    # Convierte formato DMS (grados, minutos, segundos) a grados decimales
                    # lat[1:3] = grados (2 dígitos), lat[3:5] = minutos, lat[5:7] = segundos
                    lati = float(lat[1:3]) + (float(lat[3:5]) / 60) + (float(lat[5:7]) / 3600)
                    # lon[1:4] = grados (3 dígitos porque longitud puede llegar a 180°)
                    long = float(lon[1:4]) + (float(lon[4:6]) / 60) + (float(lon[6:8]) / 3600)

                    if lat[0] == "S":   # Si el primer carácter es "S" (Sur), la latitud es negativa
                        lati = -lati
                    if lon[0] == "W":   # Si el primer carácter es "W" (Oeste), la longitud es negativa
                        long = -long

                    new_airport = Airport(elementos[0], lati, long)  # Crea el objeto Airport
                    SetSchengen(new_airport)        # Le asigna si es Schengen o no
                    airports.append(new_airport)    # Lo añade a la lista
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []       # Si no existe el fichero, devuelve lista vacía
    return airports     # Devuelve la lista con todos los aeropuertos cargados

def SaveSchengenAirports(airports, filename):
    # Guarda en un fichero solo los aeropuertos Schengen de la lista
    # El formato de salida es el mismo que el del fichero de entrada
    # Si la lista está vacía, no crea el fichero y devuelve -1 (código de error)
    if not airports:    # "not airports" es True cuando la lista está vacía
        return -1

    encontrado = False  # Controla si hemos encontrado algún aeropuerto Schengen
    with open(filename, 'w') as f:  # Abre el fichero en modo escritura ('w' = write)
        f.write("CODE\tLAT\tLON\n")    # Escribe la cabecera (\t = tabulación, \n = salto de línea)
        for airport in airports:
            SetSchengen(airport)        # Actualiza el atributo Schengen antes de comprobar
            if airport.Schengen:        # Solo guarda los aeropuertos Schengen
                encontrado = True
                lat = airport.latitude
                lon = airport.longitude

                # Determina la letra de dirección (N/S para latitud, E/W para longitud)
                # Sintaxis: "valor_si_true" if condicion else "valor_si_false"
                letra_lat = "N" if lat >= 0 else "S"
                letra_lon = "E" if lon >= 0 else "W"
                lat = abs(lat)  # abs() convierte el número a positivo (valor absoluto)
                lon = abs(lon)

                # Convierte grados decimales a grados, minutos y segundos (DMS)
                deg_lat = int(lat)                              # int() quita los decimales → grados
                min_lat = int((lat - deg_lat) * 60)            # La parte decimal × 60 → minutos
                sec_lat = int(round((lat - deg_lat - min_lat / 60) * 3600))  # Lo que queda × 3600 → segundos
                if sec_lat >= 60:   # Corrección por redondeo: si los segundos llegan a 60, pasan a minutos
                    sec_lat = 0
                    min_lat += 1    # += 1 es lo mismo que min_lat = min_lat + 1

                deg_lon = int(lon)
                min_lon = int((lon - deg_lon) * 60)
                sec_lon = int(round((lon - deg_lon - min_lon / 60) * 3600))
                if sec_lon >= 60:
                    sec_lon = 0
                    min_lon += 1

                # zfill(n) rellena con ceros a la izquierda hasta tener n dígitos (ej: 2 → "02")
                str_lat = letra_lat + str(deg_lat).zfill(2) + str(min_lat).zfill(2) + str(sec_lat).zfill(2)
                str_lon = letra_lon + str(deg_lon).zfill(3) + str(min_lon).zfill(2) + str(sec_lon).zfill(2)
                f.write(f"{airport.ICAO}\t{str_lat}\t{str_lon}\n")  # Escribe la línea en el fichero

    return encontrado   # Devuelve True si se guardaron aeropuertos, False si ninguno era Schengen

def AddAirport(airports, airport):
    # Añade un aeropuerto a la lista si no existe ya (comprueba por código ICAO)
    # any() recorre la lista y devuelve True si encuentra al menos un elemento que cumpla la condición
    if any(a.ICAO == airport.ICAO for a in airports):
        print(f"The airport {airport.ICAO} is already in the list.")
        return False    # El aeropuerto ya existe, no se añade
    airports.append(airport)    # append() añade el elemento al final de la lista
    return True         # Se añadió correctamente

def RemoveAirport(airports, code):
    # Elimina de la lista el aeropuerto con el código ICAO recibido
    # Si no existe, imprime un error y devuelve False
    code_upper = code.upper()       # Convierte a mayúsculas para evitar errores de capitalización
    original_len = len(airports)    # Guarda la longitud original para comprobar si se borró algo

    # Reemplaza la lista por una nueva lista que NO incluye el aeropuerto con ese código
    # Sintaxis: [expresion for variable in lista if condicion]
    airports[:] = [a for a in airports if a.ICAO != code_upper]

    if len(airports) == original_len:   # Si la longitud no cambió, no se encontró el aeropuerto
        print(f"Error: Airport {code} not found.")
        return False
    return True     # Se eliminó correctamente

def PlotAirports(airports):
    # Muestra un gráfico de barras apiladas con el número de aeropuertos Schengen y no Schengen
    if not airports:
        print("Error: No airports to plot.")
        return  # Sale de la función sin hacer nada más

    # sum(1 for a in airports if a.Schengen) cuenta cuántos aeropuertos tienen Schengen=True
    schengen_count = sum(1 for a in airports if a.Schengen)
    non_schengen_count = len(airports) - schengen_count  # El resto son no Schengen

    labels = ['Airports']
    plt.ylabel('Number of Airports')
    plt.title('Schengen vs Non-Schengen')
    plt.bar(labels, [schengen_count], label='Schengen', color='blue')
    # bottom=[schengen_count] hace que la barra roja empiece donde termina la azul (barra apilada)
    plt.bar(labels, [non_schengen_count], bottom=[schengen_count], label='Non-Schengen', color='red')
    plt.legend()    # Muestra la leyenda con los colores
    plt.show()      # Muestra el gráfico en pantalla

def MapAirports(airports):
    # Genera un fichero KML con la ubicación de todos los aeropuertos
    # Los aeropuertos Schengen aparecen en verde y los no Schengen en rojo en Google Earth
    if not airports:
        print("Error: No airports to map.")
        return
    with open("airports_map.kml", 'w') as f:
        # Cabecera obligatoria del formato KML
        f.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        f.write("<Document>\n")

        # Define los estilos de color para los puntos en Google Earth
        # ff00ff00 = verde (formato KML: alpha-blue-green-red), ff0000ff = rojo
        f.write("  <Style id=\"SchengenStyle\">\n")
        f.write("    <IconStyle><color>ff00ff00</color></IconStyle>\n")
        f.write("  </Style>\n")
        f.write("  <Style id=\"NonSchengenStyle\">\n")
        f.write("    <IconStyle><color>ff0000ff</color></IconStyle>\n")
        f.write("  </Style>\n")

        for airport in airports:
            SetSchengen(airport)
            f.write("  <Placemark>\n")
            f.write(f"    <name>{airport.ICAO}</name>\n")
            # Operador ternario: asigna "SchengenStyle" o "NonSchengenStyle" según el atributo
            style = "SchengenStyle" if airport.Schengen else "NonSchengenStyle"
            f.write(f"    <styleUrl>#{style}</styleUrl>\n")
            f.write("    <Point>\n")
            f.write("      <coordinates>\n")
            # En KML el orden es: longitud, latitud (al revés de lo habitual)
            f.write(f"        {airport.longitude},{airport.latitude}\n")
            f.write("      </coordinates>\n")
            f.write("    </Point>\n")
            f.write("  </Placemark>\n")

        # Cierre obligatorio del formato KML
        f.write("</Document>\n")
        f.write("</kml>\n")

    try:
        os.startfile("airports_map.kml")    # Abre el fichero KML con Google Earth (solo Windows)
    except:
        print("Map saved, but could not open Google Earth automatically.")

#Version 4

def AssignNightGates(bcn, aircrafts):

    if len(aircrafts) == 0:
        return -1

    i = 0

    while i < len(aircrafts):

        aircraft = aircrafts[i]

        if aircraft.origin == "":
            AssignGate(bcn, aircraft)

        i += 1

    return 0


