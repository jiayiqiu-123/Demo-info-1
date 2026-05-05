import os

#Definiciones de classes

class Gate:
    def __init__(self, name, Occupied, id):
        self.Name = name
        self.Occupied = Occupied
        self.AircraftID = id


class BoardingArea:
    def __init__(self, name, area_type, gate):
        self.Name = name
        self.Type = area_type  # "Schengen" o "non-Schengen"
        self.Gates = gate


class Terminal:
    def __init__(self, name, BoardA, Airline):
        self.Name = name
        self.BoardingAreas = BoardA
        self.Airlines = Airline  # ICAO codes


class BarcelonaAP:
    def __init__(self, code, terminal):
        self.Code = code
        self.Terminals = terminal


# Funciones

def SetGates(area, init_gate, end_gate, prefix):

    if end_gate <= init_gate:
        return -1

    area.Gates = []
    i = init_gate
    while i <= end_gate:
        gate_name = prefix + str(i)
        new_gate = Gate(gate_name)
        new_gate.Occupied = False
        area.Gates.append(new_gate)
        i = i + 1

    return 0


def LoadAirlines(terminal, t_name):
    filename = t_name + "_Airlines.txt"
    try:
        f = open(filename, "r")
        temp_list = []
        line = f.readline()

        while line != "":
            line = line.strip()
            if line: # Para asegurar que line haya contenido real (NO espacios)
                parts = line.split(" ")
                if len(parts) >= 2:
                    icao_code = parts[len(parts) - 1]
                    temp_list.append(icao_code)

            line = f.readline()

        f.close()

        terminal.Airlines = temp_list
        return 0

    except FileNotFoundError:
        return -1
    except:
        return -1