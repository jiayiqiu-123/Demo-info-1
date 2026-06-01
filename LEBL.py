import os
import matplotlib.pyplot as plt
from airport import *
from aircraft import *

# ---------------------------------------------------------------------------
# Definición de clases
# ---------------------------------------------------------------------------

class Gate:
    def __init__(self, name="", occupied=False, aircraft_id=""):
        self.Name       = name          # Nombre de la puerta, ej: "T1BAaG1"
        self.Occupied   = occupied      # True = ocupada, False = libre
        self.AircraftID = aircraft_id   # ID del avión que ocupa la puerta (vacío si libre)


class BoardingArea:
    def __init__(self, name="", area_type=""):
        self.Name  = name       # Nombre del área, ej: "A", "B", "M"
        self.Type  = area_type  # "Schengen" o "non-Schengen"
        self.Gates = []         # Lista de objetos Gate


class Terminal:
    def __init__(self, name=""):
        self.Name          = name   # Nombre del terminal, ej: "T1", "T2"
        self.BoardingAreas = []     # Lista de objetos BoardingArea
        self.Airlines      = []     # Lista de códigos ICAO de aerolíneas (ej: ["VLG", "IBE"])


class BarcelonaAP:
    def __init__(self, code=""):
        self.Code      = code   # Código ICAO del aeropuerto, ej: "LEBL"
        self.Terminals = []     # Lista de objetos Terminal


# ---------------------------------------------------------------------------
# Funciones principales
# ---------------------------------------------------------------------------

def SetGates(area, init_gate, end_gate, prefix):
    # Asigna una lista de puertas a un área de embarque
    # El nombre de cada puerta = prefijo + número de puerta (ej: "T1BAaG" + "1" = "T1BAaG1")
    # Si end_gate no es mayor que init_gate → devuelve -1 (error)

    if end_gate <= init_gate:
        return -1

    area.Gates = []     # Limpia la lista anterior antes de asignar las nuevas puertas

    # range(init_gate, end_gate + 1) genera números desde init_gate hasta end_gate (inclusive)
    for i in range(init_gate, end_gate + 1):
        gate_name = prefix + str(i)
        new_gate  = Gate(name=gate_name, occupied=False, aircraft_id="")
        area.Gates.append(new_gate)

    return 0


def LoadAirlines(terminal, t_name):
    # Lee el fichero {t_name}_Airlines.txt y actualiza la lista de aerolíneas del terminal
    # Si el fichero no existe → devuelve -1 sin modificar el terminal
    # Formato del fichero: "Nombre Aerolínea\tCódigo ICAO" por línea

    filename = f"{t_name}_Airlines.txt"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            temp_list = []
            for line in f:
                line = line.strip()
                if not line:            # Salta líneas vacías
                    continue
                parts = line.split('\t')    # Separa por tabulación
                if len(parts) >= 2:
                    icao_code = parts[-1].strip()   # El código ICAO siempre es el último elemento
                    temp_list.append(icao_code)

        # Solo actualizamos el terminal si el fichero se leyó correctamente
        terminal.Airlines = temp_list
        return 0

    except FileNotFoundError:
        return -1   # No modificamos el terminal si el fichero no existe


def LoadAirportStructure(filename):
    # Lee el fichero LEBL.txt y construye un objeto BarcelonaAP completo
    # Llama a SetGates() y LoadAirlines() para completar la estructura
    # Si el fichero no existe → devuelve -1

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return -1

    if not lines:
        return -1

    # Primera línea: "LEBL 2 terminals"
    first_line = lines[0].strip().split()
    if not first_line:
        return -1

    airport_code = first_line[0]
    airport      = BarcelonaAP(airport_code)

    current_terminal = None

    # lines[1:] = todas las líneas menos la primera (cabecera del aeropuerto)
    for line in lines[1:]:
        line  = line.strip()
        if not line:
            continue
        parts = line.split()

        # Caso 1: Cabecera de Terminal → "Terminal T1 5 boarding areas"
        if parts[0] == "Terminal":
            t_name           = parts[1]
            current_terminal = Terminal(t_name)
            airport.Terminals.append(current_terminal)

            # Carga las aerolíneas del fichero {t_name}_Airlines.txt
            res = LoadAirlines(current_terminal, t_name)
            if res == -1:
                # Avisamos pero no paramos: el aeropuerto puede funcionar sin aerolíneas asignadas
                print(f"Aviso: No se encontró el fichero de aerolíneas para {t_name}")

        # Caso 2: Línea de área de embarque → "Area A Schengen Gates 1 - 11"
        elif parts[0] == "Area" and current_terminal is not None:
            area_name = parts[1]    # "A", "B", "M", etc.
            area_type = parts[2]    # "Schengen" o "non-Schengen"

            new_area = BoardingArea(area_name, area_type)
            current_terminal.BoardingAreas.append(new_area)

            # Extrae los números de puerta: "Gates 1 - 11" → init=1, end=11
            if "Gates" in parts:
                idx_gates = parts.index("Gates")
                try:
                    init_gate = int(parts[idx_gates + 1])
                    end_gate  = int(parts[idx_gates + 3])   # Salta el guion "-"
                except (ValueError, IndexError):
                    init_gate = int(parts[-3])
                    end_gate  = int(parts[-1])

                # Prefijo único para cada área siguiendo el formato del enunciado
                # Ejemplo: Terminal "T1" + "BA" + Área "A" + "G" = "T1BAaG"
                prefix = f"{current_terminal.Name}BA{area_name}G"
                SetGates(new_area, init_gate, end_gate, prefix)

    return airport


def GateOccupancy(bcn):
    # Devuelve una lista con el estado de todas las puertas del aeropuerto
    # Cada elemento es: [nombre_puerta, "free"/"occupied", id_avión]

    gates_list = []

    # Tres for anidados para recorrer: Terminales → Áreas → Puertas
    for terminal in bcn.Terminals:
        for area in terminal.BoardingAreas:
            for gate in area.Gates:
                # Operador ternario: "occupied" si está ocupada, "free" si no
                status = "occupied" if gate.Occupied else "free"
                gates_list.append([gate.Name, status, gate.AircraftID])

    return gates_list


def IsAirlineInTerminal(terminal, name):
    # Devuelve True si la aerolínea (código ICAO) opera en este terminal
    # Cadena vacía → devuelve False
    # Lista de aerolíneas vacía → devuelve False
    # NOTA: El enunciado pide también un error code para cadena vacía,
    # pero devolver (False, -1) rompería SearchTerminal porque una tupla siempre es True en Python
    # → La protección de cadena vacía se gestiona en SearchTerminal directamente

    if not name:            # "not name" cubre tanto "" como None
        return False

    if not terminal.Airlines:   # Lista vacía → False
        return False

    # "in" devuelve True/False directamente, sin necesidad de if/else
    return name in terminal.Airlines


def SearchTerminal(bcn, name):
    # Devuelve el nombre del terminal donde opera la aerolínea recibida
    # Usa IsAirlineInTerminal() para comprobar cada terminal
    # Si name es cadena vacía → devuelve "" (cubre el error code del enunciado)
    # Si no se encuentra la aerolínea → devuelve ""

    if not name:
        return ""

    for terminal in bcn.Terminals:
        if IsAirlineInTerminal(terminal, name):
            return terminal.Name

    return ""   # Aerolínea no encontrada en ningún terminal


def AssignGate(bcn, aircraft):
    # Asigna la primera puerta libre del área correcta al avión recibido
    # Área correcta = terminal de la aerolínea + tipo Schengen/non-Schengen del vuelo
    # Si no hay puertas libres del tipo correcto → devuelve -1 sin modificar bcn

    airline_code = aircraft.Company
    aircraft_id  = aircraft.Id

    # Paso 1: Encontrar el terminal de la aerolínea
    terminal_name = SearchTerminal(bcn, airline_code)
    if terminal_name == "":
        return -1   # Aerolínea no encontrada en ningún terminal

    # Paso 2: Protección para aircraft.origin = None
    # Sin esta protección, aircraft.origin.Schengen provocaría AttributeError
    aircraft_origin = aircraft.origin
    if aircraft_origin is None:
        return -1   # No se puede determinar Schengen sin el aeropuerto de origen

    # Paso 3: Determinar el tipo de área (Schengen o non-Schengen)
    # Usamos aircraft_origin.Schengen directamente (ya calculado al cargar aeropuertos)
    target_type = "Schengen" if aircraft_origin.Schengen else "non-Schengen"

    # Paso 4: Buscar la primera puerta libre en el terminal y área correctos
    for terminal in bcn.Terminals:
        if terminal.Name == terminal_name:
            for area in terminal.BoardingAreas:
                if area.Type == target_type:
                    for gate in area.Gates:
                        if not gate.Occupied:
                            gate.Occupied   = True
                            gate.AircraftID = aircraft_id
                            return gate.Name    # Devuelve el nombre de la puerta asignada
            # break después de revisar todas las áreas del terminal correcto
            # No tiene sentido seguir buscando en otros terminales
            break

    return -1   # No hay puertas libres del tipo correcto


# ---------------------------------------------------------------------------
# Funciones V4 — Nuevas
# ---------------------------------------------------------------------------

def AssignNightGates(bcn, aircrafts):
    # Asigna puertas a los aviones nocturnos al inicio del día.
    # Solo procesa aviones sin llegada (time=None) pero con salida registrada.
    # Si la lista está vacía → devuelve -1.

    if not aircrafts:
        return -1

    for ac in aircrafts:
        # Solo procesamos aviones nocturnos: sin hora de llegada pero con hora de salida
        # Si tiene hora de llegada, NO es nocturno → saltamos
        if ac.time is not None:
            continue
        if ac.DepartureTime is None:
            continue
        # Llamamos a AssignGate() para asignar la puerta
        # Si devuelve -1 es porque no hay puertas libres → simplemente continuamos
        AssignGate(bcn, ac)

    return 0


def FreeGate(bcn, id):
    # Libera la puerta ocupada por el avión con el ID recibido.
    # Recorre todos los terminales → áreas → puertas hasta encontrar el avión.
    # Si no se encuentra el avión en ninguna puerta → devuelve -1.

    # Tres for anidados para recorrer toda la estructura del aeropuerto
    for terminal in bcn.Terminals:
        for area in terminal.BoardingAreas:
            for gate in area.Gates:
                if gate.AircraftID == id and gate.Occupied:
                    # Puerta encontrada → la ponemos libre
                    gate.Occupied   = False
                    gate.AircraftID = ""    # Vaciamos el ID del avión
                    return 0                # Éxito

    return -1   # No se encontró ninguna puerta con ese ID de avión


def AssignGatesAtTime(bcn, aircrafts, time):
    # Procesa todos los movimientos del aeropuerto durante una hora concreta.
    # Primero libera las puertas de los aviones que ya salieron en esa hora.
    # Luego asigna puertas a los aviones que llegan en esa hora.
    # Devuelve el número de aviones que NO pudieron ser asignados por falta de puertas.

    if not aircrafts:
        return 0

    # Convertir la hora recibida ("07:00") al número de hora (7)
    # para poder comparar con las horas de llegada y salida de los aviones
    try:
        target_hour = int(time.split(":")[0])
    except (ValueError, AttributeError):
        return 0

    # Paso 1: Liberar puertas de aviones que salen durante esta hora
    # Ej: si target_hour=7, liberamos todos los aviones con DepartureTime entre 07:00 y 07:59
    for ac in aircrafts:
        if ac.DepartureTime is not None:
            try:
                dep_hour = int(ac.DepartureTime.split(":")[0])
                if dep_hour == target_hour:
                    FreeGate(bcn, ac.Id)    # Libera la puerta de este avión
            except (ValueError, AttributeError):
                continue    # Si el tiempo tiene formato inválido → saltamos

    # Paso 2: Asignar puertas a aviones que llegan durante esta hora
    # Ej: si target_hour=7, asignamos puertas a aviones con time entre 07:00 y 07:59
    unassigned = 0  # Contador de aviones que no pudieron ser asignados
    for ac in aircrafts:
        if ac.time is not None:
            try:
                arr_hour = int(ac.time.split(":")[0])
                if arr_hour == target_hour:
                    result = AssignGate(bcn, ac)
                    if result == -1:
                        unassigned += 1     # No había puertas libres para este avión
            except (ValueError, AttributeError):
                continue

    return unassigned   # Devuelve cuántos aviones no pudieron ser asignados


def PlotDayOccupancy(bcn, aircrafts):
    # Muestra un gráfico con la ocupación de puertas por terminal a lo largo del día.
    # Llama a AssignGatesAtTime() hora a hora para simular el día completo.
    # ⚠️ IMPORTANTE: Esta función modifica bcn. Antes de llamarla, bcn debe estar
    # en el estado inicial del día (solo aviones nocturnos asignados).
    # Si se llama dos veces seguidas, hay que recargar bcn con LoadAirportStructure() primero.

    if not aircrafts:
        print("Error: La lista de vuelos está vacía.")
        return

    hours               = list(range(24))   # Lista [0, 1, 2, ..., 23]
    unassigned_per_hour = []                # Aviones sin puerta por hora

    # CAMBIO: Diccionario dinámico en vez de variables hardcoded t1_count/t2_count
    # Así funciona aunque el aeropuerto tenga más de 2 terminales en el futuro
    # {nombre_terminal: [ocupación_hora0, ocupación_hora1, ...]}
    terminal_counts = {t.Name: [] for t in bcn.Terminals}

    for hour in hours:
        # :02d significa que el número siempre tiene 2 dígitos (ej: 7 → "07")
        time_str   = f"{hour:02d}:00"
        unassigned = AssignGatesAtTime(bcn, aircrafts, time_str)
        unassigned_per_hour.append(unassigned)

        # Contar puertas ocupadas en cada terminal después de procesar esta hora
        for terminal in bcn.Terminals:
            # sum() con generador: cuenta las puertas ocupadas de todas las áreas del terminal
            count = sum(1 for area in terminal.BoardingAreas
                        for gate in area.Gates if gate.Occupied)
            terminal_counts[terminal.Name].append(count)

    # --- Construcción del gráfico ---
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Colores para cada terminal
    colors  = ['steelblue', 'orange', 'green', 'purple']
    bottom  = [0] * 24  # Base de las barras apiladas, empieza en 0

    # Dibuja una barra por terminal, apiladas una encima de la otra
    for idx, (t_name, counts) in enumerate(terminal_counts.items()):
        color = colors[idx % len(colors)]   # % len(colors) evita error si hay más terminales que colores
        ax1.bar(hours, counts, bottom=bottom,
                label=f'{t_name} - puertas ocupadas',
                color=color, alpha=0.8)
        # Actualizar la base para la siguiente barra apilada
        # zip() combina dos listas elemento a elemento: zip([1,2], [3,4]) → [(1,3), (2,4)]
        bottom = [b + c for b, c in zip(bottom, counts)]

    ax1.set_xlabel('Hora del día')
    ax1.set_ylabel('Puertas ocupadas')
    ax1.set_xticks(hours)

    # Eje secundario (derecha) para los aviones sin asignar
    # twinx() crea un segundo eje Y que comparte el mismo eje X
    ax2 = ax1.twinx()
    ax2.plot(hours, unassigned_per_hour, color='red', marker='o',
             linewidth=2, label='Aviones sin puerta')
    ax2.set_ylabel('Aviones sin puerta asignada', color='red')

    # Combinar las leyendas de los dos ejes en una sola
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.title('Ocupación de puertas por terminal a lo largo del día')
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# Sección de pruebas
# Este bloque SOLO se ejecuta cuando corres LEBL.py directamente
# Si otro fichero hace "from LEBL import *", este bloque NO se ejecuta
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("       LEBL.py — Sección de pruebas")
    print("=" * 50)

    # --- Test LoadAirportStructure ---
    print("\n[1] Test LoadAirportStructure")
    bcn = LoadAirportStructure("Terminals.txt")
    if bcn == -1:
        print("  ERROR: No se pudo cargar la estructura del aeropuerto")
    else:
        print(f"  Aeropuerto cargado: {bcn.Code}")
        print(f"  Número de terminales: {len(bcn.Terminals)}")
        for t in bcn.Terminals:
            # sum() con generador: cuenta el total de puertas de todas las áreas del terminal
            total_gates = sum(len(area.Gates) for area in t.BoardingAreas)
            print(f"    Terminal {t.Name}: {len(t.BoardingAreas)} áreas, "
                  f"{len(t.Airlines)} aerolíneas, {total_gates} puertas")

    # --- Test SetGates ---
    print("\n[2] Test SetGates")
    test_area  = BoardingArea("TEST", "Schengen")
    result_ok  = SetGates(test_area, 1, 5, "TESTG")
    result_err = SetGates(test_area, 5, 1, "TESTG")
    print(f"  SetGates(1→5): {len(test_area.Gates)} puertas → esperado 5")
    print(f"  SetGates(5→1): {result_err} → esperado -1 (error)")
    print(f"  Primera puerta: {test_area.Gates[0].Name} → esperado TESTG1")

    # --- Test LoadAirlines ---
    print("\n[3] Test LoadAirlines")
    test_terminal = Terminal("T1")
    result        = LoadAirlines(test_terminal, "T1")
    print(f"  LoadAirlines T1: {len(test_terminal.Airlines)} aerolíneas cargadas")
    result_err = LoadAirlines(test_terminal, "T99")
    print(f"  LoadAirlines fichero inexistente: {result_err} → esperado -1")

    # --- Test IsAirlineInTerminal ---
    print("\n[4] Test IsAirlineInTerminal")
    if bcn != -1:
        t1 = bcn.Terminals[0]   # T1
        t2 = bcn.Terminals[1]   # T2
        print(f"  VLG en T1: {IsAirlineInTerminal(t1, 'VLG')} → esperado True")
        print(f"  RYR en T1: {IsAirlineInTerminal(t1, 'RYR')} → esperado False")
        print(f"  RYR en T2: {IsAirlineInTerminal(t2, 'RYR')} → esperado True")
        print(f"  Cadena vacía: {IsAirlineInTerminal(t1, '')} → esperado False")

    # --- Test SearchTerminal ---
    print("\n[5] Test SearchTerminal")
    if bcn != -1:
        print(f"  VLG: {SearchTerminal(bcn, 'VLG')} → esperado T1")
        print(f"  RYR: {SearchTerminal(bcn, 'RYR')} → esperado T2")
        print(f"  ZZZ: '{SearchTerminal(bcn, 'ZZZ')}' → esperado '' (vacío)")
        print(f"  Cadena vacía: '{SearchTerminal(bcn, '')}' → esperado '' (vacío)")

    # --- Test AssignGate + GateOccupancy ---
    # CAMBIO: Cargamos airports y aircrafts aquí una sola vez
    # y los reutilizamos en todos los tests que los necesiten (incluyendo V4)
    print("\n[6] Test AssignGate")
    airports  = LoadAirports("Airports.txt")
    aircrafts = LoadArrivals("Arrivals.txt", airports)
    if bcn != -1 and aircrafts:
        ac     = aircrafts[0]
        result = AssignGate(bcn, ac)
        print(f"  Primer avión ({ac.Id}, {ac.Company}): puerta asignada = {result}")

        # Test con avión sin origen (origin=None) → debe devolver -1
        fake_ac     = Aircraft("FAKE", "VLG", None, "10:00")
        result_none = AssignGate(bcn, fake_ac)
        print(f"  Avión sin origen: {result_none} → esperado -1")

        # Test con aerolínea desconocida → debe devolver -1
        fake_ac2    = Aircraft("FAKE2", "ZZZ", aircrafts[0].origin, "10:00")
        result_unkn = AssignGate(bcn, fake_ac2)
        print(f"  Aerolínea desconocida: {result_unkn} → esperado -1")

    # --- Test GateOccupancy ---
    print("\n[7] Test GateOccupancy")
    if bcn != -1:
        gates    = GateOccupancy(bcn)
        occupied = sum(1 for g in gates if g[1] == "occupied")
        free     = sum(1 for g in gates if g[1] == "free")
        print(f"  Total puertas: {len(gates)}")
        print(f"  Ocupadas: {occupied}")
        print(f"  Libres:   {free}")

    # ---------------------------------------------------------------------------
    # Tests V4
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("       Tests V4 — Nuevas funciones")
    print("=" * 50)

    # CAMBIO: Reutilizamos airports y aircrafts ya cargados arriba
    # Solo cargamos lo nuevo: departures y merged
    departures = LoadDepartures("Departures.txt")
    merged     = MergeMovements(aircrafts, departures)

    # --- Test AssignNightGates ---
    print("\n[V4-1] Test AssignNightGates")
    if merged != -1:
        night = NightAircraft(merged)
        if night == -1 or not night:
            print("  No hay aviones nocturnos para probar")
        else:
            # Recargamos la estructura para empezar desde cero
            bcn_test = LoadAirportStructure("Terminals.txt")
            result   = AssignNightGates(bcn_test, night)
            print(f"  AssignNightGates: resultado = {result} → esperado 0")

            # Verificamos que las puertas fueron asignadas
            gates    = GateOccupancy(bcn_test)
            occupied = sum(1 for g in gates if g[1] == "occupied")
            print(f"  Puertas ocupadas tras asignar nocturnos: {occupied}")

    # Test con lista vacía → debe devolver -1
    if bcn != -1:
        result_err = AssignNightGates(bcn, [])
        print(f"  Lista vacía: {result_err} → esperado -1")

    # --- Test FreeGate ---
    print("\n[V4-2] Test FreeGate")
    if merged != -1 and aircrafts:
        bcn_test2 = LoadAirportStructure("Terminals.txt")
        ac        = aircrafts[0]
        gate_name = AssignGate(bcn_test2, ac)
        print(f"  Puerta asignada a {ac.Id}: {gate_name}")
        result = FreeGate(bcn_test2, ac.Id)
        print(f"  FreeGate ({ac.Id}): {result} → esperado 0")

        # Test con ID inexistente → debe devolver -1
        result_err = FreeGate(bcn_test2, "AVION_INEXISTENTE")
        print(f"  ID inexistente: {result_err} → esperado -1")

    # --- Test AssignGatesAtTime ---
    print("\n[V4-3] Test AssignGatesAtTime")
    if merged != -1:
        bcn_test3 = LoadAirportStructure("Terminals.txt")
        night     = NightAircraft(merged)
        if night and night != -1:
            AssignNightGates(bcn_test3, night)

        # Procesamos la hora 7 (07:00 - 07:59)
        unassigned = AssignGatesAtTime(bcn_test3, merged, "07:00")
        print(f"  AssignGatesAtTime('07:00'): {unassigned} aviones sin asignar")

        # Test con lista vacía → debe devolver 0
        result_err = AssignGatesAtTime(bcn_test3, [], "07:00")
        print(f"  Lista vacía: {result_err} → esperado 0")

    # --- Test PlotDayOccupancy ---
    print("\n[V4-4] Test PlotDayOccupancy (cerrar ventana para continuar)...")
    if merged != -1:
        # Recargamos bcn para empezar desde el estado inicial (solo nocturnos)
        # ⚠️ Necesario porque PlotDayOccupancy modifica bcn internamente
        bcn_plot = LoadAirportStructure("Terminals.txt")
        night    = NightAircraft(merged)
        if night and night != -1:
            AssignNightGates(bcn_plot, night)
        PlotDayOccupancy(bcn_plot, merged)

    print("\n" + "=" * 50)
    print("       Pruebas completadas")
    print("=" * 50)