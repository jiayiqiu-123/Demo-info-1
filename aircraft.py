import os
import math

class Aircraft:
    def __init__(self, id, comp, origin,time):
        self.Id = id
        self.Company = comp
        self.origin = origin #Importante este hay que poner los aeropuertos que están definidos en versión 1!!
        self.time = time

def MapFlights(aircrafts):

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
        origin_ap = aircrafts[i].origin

        f.write("  <Placemark>\n")
        f.write("    <name>" + aircrafts[i].id + " - " + origin_ap.ICAO + "</name>\n")

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
        os.startfile("flights_map.kml")
    except:
        print("KML generated, but Google Earth could not be opened automatically.")

def LongDistanceArrivals(aircrafts):

    lat_lebl = 41.29694
    lon_lebl = 2.07833
    R = 6371.0

    long_distance_flights = []

    i = 0
    while i < len(aircrafts):

        lat_origen = aircrafts[i].origin.latitude
        lon_origen = aircrafts[i].origin.longitude

        # Calcular Haversine distance, pág 18 está la fórmula esta rara, no hay nada especial
        lat_origen = math.radians(lat_origen)
        lat_final = math.radians(lat_lebl)
        d_lat = math.radians(lat_lebl - lat_origen)
        d_lon = math.radians(lon_lebl - lon_origen)

        a = math.sin(d_lat / 2)**2 + math.cos(lat_origen*1) * math.cos(lat_final*2) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        if distance > 2000:
            long_distance_flights.append(aircrafts[i])

        i = i + 1

    return long_distance_flights