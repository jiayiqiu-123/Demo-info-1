import os

#Definiciones de classes

class Gate:
    def __init__(self, name):
        self.Name = name
        self.Occupied = False
        self.AircraftID = ""


class BoardingArea:
    def __init__(self, name, area_type):
        self.Name = name
        self.Type = area_type  # "Schengen" o "non-Schengen"
        self.Gates = []


class Terminal:
    def __init__(self, name):
        self.Name = name
        self.BoardingAreas = []
        self.Airlines = []  # ICAO codes


class BarcelonaAP:
    def __init__(self, code):
        self.Code = code
        self.Terminals = []


# Funciones

def SetGates(area, init_gate, end_gate, prefix):

    if end_gate <= init_gate:
        return -1

    area.Gates = []
    i = init_gate
    while i <= end_gate:
        gate_name = prefix + str(i)
        new_gate = Gate(gate_name)
        area.Gates.append(new_gate)
        i = i + 1

    return 0


def LoadAirlines(terminal, t_name):

    filename = t_name + "_Airlines.txt"

    if not os.path.exists(filename):
        return -1

    try:
        f = open(filename, "r")
        lines = f.readlines()  # Leemos todas las líneas en una lista
        f.close()

        new_airlines_list = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line:
                # Separamos por tabulador
                parts = line.split('\t')
                if len(parts) >= 2:
                    icao_code = parts[1].strip()
                    new_airlines_list.append(icao_code)
            i = i + 1  # Siguiente línea

        terminal.Airlines = new_airlines_list
        return 0

    except:
        return -1