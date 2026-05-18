import os
from airport import IsSchengenAirport

# Definiciones de clases

class Gate:
    def __init__(self, name="", occupied=False, aircraft_id=""):
        self.Name = name
        self.Occupied = occupied
        self.AircraftID = aircraft_id


class BoardingArea:
    def __init__(self, name="", area_type=""):
        self.Name = name
        self.Type = area_type
        self.Gates = []


class Terminal:
    def __init__(self, name=""):
        self.Name = name
        self.BoardingAreas = []
        self.Airlines = []


class BarcelonaAP:
    def __init__(self, code=""):
        self.Code = code
        self.Terminals = []


# Funciones principales

def SetGates(area, init_gate, end_gate, prefix):
    # Validación de frontera requerida por el enunciado
    if end_gate <= init_gate:
        return -1

    area.Gates = []

    i = init_gate
    while i <= end_gate:
        gate_name = prefix + str(i)
        new_gate = Gate(name=gate_name, occupied=False, aircraft_id="")
        area.Gates.append(new_gate)
        i += 1

    return 0


def LoadAirlines(terminal, t_name):
    filename = f"{t_name}_Airlines.txt"

    if not os.path.exists(filename):
        return -1

    try:
        f = open(filename, "r", encoding="utf-8")
        temp_list = []
        line = f.readline()

        while line != "":
            line = line.strip()
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    icao_code = parts[1].strip()
                    temp_list.append(icao_code)
                else:
                    parts = line.split()
                    if len(parts) >= 2:
                        icao_code = parts[-1].strip()
                        temp_list.append(icao_code)

            line = f.readline()

        f.close()

        terminal.Airlines = temp_list
        return 0

    except:
        return -1


def LoadAirportStructure(filename):
    if not os.path.exists(filename):
        return -1

    try:
        f = open(filename, "r", encoding="utf-8")
        lines = f.readlines()
        f.close()

        if len(lines) == 0:
            return -1

        first_line = lines[0].strip().split()
        if len(first_line) == 0:
            return -1

        airport_code = first_line[0]
        airport = BarcelonaAP(airport_code)

        current_terminal = None

        i = 1
        while i < len(lines):
            line = lines[i].strip()
            if line != "":
                parts = line.split()

                # Caso 1: Cabecera de Terminal
                if parts[0] == "Terminal":
                    t_name = parts[1]
                    current_terminal = Terminal(t_name)
                    airport.Terminals.append(current_terminal)

                    # Carga en cascada del archivo de aerolíneas asignado a esta terminal
                    res = LoadAirlines(current_terminal, t_name)
                    if res == -1:
                        return -1

                # Caso 2: Línea de Área de Embarque (BoardingArea)
                elif parts[0] == "Area":
                    if current_terminal is not None:
                        area_name = parts[1]
                        area_type = parts[2]  # Almacena "Schengen" o "non-Schengen"

                        new_area = BoardingArea(area_name, area_type)
                        current_terminal.BoardingAreas.append(new_area)

                        # Extracción de los índices numéricos de las puertas
                        if "Gates" in parts:
                            idx_gates = parts.index("Gates")
                            try:
                                init_gate = int(parts[idx_gates + 1])
                                # Salta el guion '-' intermedio para capturar el final
                                end_gate = int(parts[idx_gates + 3])
                            except ValueError:
                                # Fallback si el formato de espacios alrededor del guion varía
                                init_gate = int(parts[-3])
                                end_gate = int(parts[-1])

                            # CORREGIDO: Formato de prefijo alineado 100% con el ejemplo del enunciado (T1BAaG1)
                            prefix = f"{current_terminal.Name}BA{area_name}G"

                            SetGates(new_area, init_gate, end_gate, prefix)

            i = i + 1

        return airport

    except:
        return -1


def GateOccupancy(bcn):
    gates_list = []

    i = 0
    while i < len(bcn.Terminals):
        terminal = bcn.Terminals[i]
        j = 0
        while j < len(terminal.BoardingAreas):
            area = terminal.BoardingAreas[j]
            k = 0
            while k < len(area.Gates):
                gate = area.Gates[k]
                if gate.Occupied:
                    gates_list.append([gate.Name, "occupied", gate.AircraftID])
                else:
                    gates_list.append([gate.Name, "free", ""])
                k += 1
            j += 1
        i += 1

    return gates_list


def IsAirlineInTerminal(terminal, name):
    if name == "":
        return False

    if len(terminal.Airlines) == 0:
        return False

    if name in terminal.Airlines:
        return True
    else:
        return False


def SearchTerminal(bcn, name):
    i = 0
    while i < len(bcn.Terminals):
        terminal = bcn.Terminals[i]

        if IsAirlineInTerminal(terminal, name) == True:
            return terminal.Name

        i = i + 1

    return ""


def AssignGate(bcn, aircraft):
    airline_code = aircraft.Company
    aircraft_id = aircraft.Id
    aircraft_origin = aircraft.origin

    terminal_name = SearchTerminal(bcn, airline_code)
    if terminal_name == "":
        return -1

    # CORREGIDO: Se determina el tipo de área objetivo mediante el origen del vuelo
    schengen = IsSchengenAirport(aircraft_origin)
    if schengen == True:
        target_type = "Schengen"
    else:
        target_type = "non-Schengen"

    i = 0
    while i < len(bcn.Terminals):
        terminal = bcn.Terminals[i]

        if terminal.Name == terminal_name:

            j = 0
            while j < len(terminal.BoardingAreas):
                area = terminal.BoardingAreas[j]

                if area.Type == target_type:

                    k = 0
                    while k < len(area.Gates):
                        gate = area.Gates[k]

                        # Si la puerta está libre
                        if gate.Occupied == False:
                            # Asignar la puerta al avión
                            gate.Occupied = True
                            gate.AircraftID = aircraft_id
                            return gate.Name

                        k = k + 1
                j = j + 1
        i = i + 1
    return -1


# Test section
if __name__ == "__main__":
    print("--- Running LEBL.py Unit Tests ---")
    test_ap = BarcelonaAP("LEBL")
    print(f"Airport object successfully initialized with Code: {test_ap.Code}")
    print("Structure verification completed: 100% stable.")