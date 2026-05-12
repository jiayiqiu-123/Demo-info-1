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

def LoadAirportStructure(filename):
    if not os.path.exists(filename):
        return -1

    try:
        f = open(filename, "r")
        lines = f.readlines()
        f.close()

        if len(lines) == 0:
            return -1

        first_line = lines[0].strip().split()
        if len(first_line) == 0:
            return -1

        airport_code = first_line[0]
        airport = BarcelonaAP(airport_code)

        i = 1
        current_terminal = None

        while i < len(lines):
            line = lines[i].strip()

            if line:
                parts = line.split()

                if parts[0] == "Terminal":
                    t_name = parts[1]
                    current_terminal = Terminal(t_name)
                    airport.Terminals.append(current_terminal)

                    LoadAirlines(current_terminal, t_name)

                elif parts[0] == "Area":
                    if current_terminal is not None:
                        area_name = parts[1]
                        area_type = parts[2]

                        new_area = BoardingArea(area_name, area_type)
                        current_terminal.BoardingAreas.append(new_area)

                        if "Gates" in parts:
                            idx_gates = parts.index("Gates")
                            init_gate = int(parts[idx_gates + 1])
                            end_gate = int(parts[idx_gates + 2])

                            prefix = current_terminal.Name + area_name

                            SetGates(new_area, init_gate, end_gate, prefix)
            i += 1

        return airport

    except:
        return -1


def GateOccupancy(bcn):
    gates_list = []

    for terminal in bcn.Terminals:
        for area in terminal.BoardingAreas:
            for gate in area.Gates:
                if gate.Occupied:
                    gates_list.append([gate.Name, "occupied", gate.Aircraft])
                else:
                    gates_list.append([gate.Name, "free", ""])

    return gates_list


def IsAirlineInTerminal(terminal, name):
    if name == "":
        return False, -1

    if len(terminal.Airlines) == 0:
        return False

    if name in terminal.Airlines:
        return True
    else:
        return False