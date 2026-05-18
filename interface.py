import os
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from airport import *
from aircraft import *

from LEBL import BarcelonaAP, Terminal, BoardingArea, Gate
from LEBL import LoadAirportStructure, AssignGate, GateOccupancy

plt.show = lambda: None

# Variables globales
airports = []
aircrafts = []
canvas = None
bcn_airport = None  # Almacenará el objeto BarcelonaAP creado en V3


# Funciones de control de la interfaz

def clear_chart_area():
    """Limpia el area del grafico actual y elimina el texto de fondo"""
    for widget in chart_frame.winfo_children():
        widget.destroy()


def display_current_plot():
    """Captura el grafico y lo mete en el hueco exacto"""
    for widget in chart_frame.winfo_children():
        widget.destroy()

    fig = plt.gcf()

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()

    canvas.get_tk_widget().pack(fill="both", expand=True)

    plt.close('all')


def show_message(text, color="black"):
    """Muestra mensajes al usuario sin usar pop-ups (messagebox)"""
    lbl_status.config(text=text, fg=color)


def clear_interactions():
    """Limpia los botones y entradas (inputs) del panel de interaccion"""
    for widget in input_frame.winfo_children():
        widget.destroy()


# Funciones v1

def cmd_load():
    global airports
    clear_interactions()
    file = filedialog.askopenfilename(title="Select Airport File", filetypes=[("Text files", "*.txt")])
    if file:
        airports = LoadAirports(file)
        show_message(f"Success: Loaded {len(airports)} airports.", "green")


def cmd_add():
    clear_interactions()
    show_message("Enter new airport details below:", "blue")

    tk.Label(input_frame, text="ICAO Code:").grid(row=0, column=0, padx=5, pady=5)
    ent_code = tk.Entry(input_frame, width=10)
    ent_code.grid(row=0, column=1)

    tk.Label(input_frame, text="Latitude:").grid(row=0, column=2, padx=5)
    ent_lat = tk.Entry(input_frame, width=10)
    ent_lat.grid(row=0, column=3)

    tk.Label(input_frame, text="Longitude:").grid(row=0, column=4, padx=5)
    ent_lon = tk.Entry(input_frame, width=10)
    ent_lon.grid(row=0, column=5)

    def on_submit():
        code = ent_code.get().upper()
        try:
            lat = float(ent_lat.get())
            lon = float(ent_lon.get())
            new_ap = Airport(code, lat, lon)
            if AddAirport(airports, new_ap):
                show_message(f"Success: Airport {code} added!", "green")
            else:
                show_message("Warning: Airport already exists.", "orange")
            clear_interactions()
        except ValueError:
            show_message("Error: Invalid coordinates. Enter numbers.", "red")

    tk.Button(input_frame, text="Save Airport", command=on_submit).grid(row=0, column=6, padx=10)


def cmd_remove():
    clear_interactions()
    show_message("Enter ICAO Code to remove:", "blue")

    tk.Label(input_frame, text="ICAO Code:").grid(row=0, column=0, padx=5)
    ent_code = tk.Entry(input_frame)
    ent_code.grid(row=0, column=1)

    def on_remove():
        code = ent_code.get().upper()
        if RemoveAirport(airports, code):
            show_message(f"Success: Airport {code} removed.", "green")
        else:
            show_message("Error: Airport not found.", "red")
        clear_interactions()

    tk.Button(input_frame, text="Remove", command=on_remove).grid(row=0, column=2, padx=10)


def cmd_save():
    if not airports:
        show_message("Warning: The list is empty. Load data first.", "red")
        return
    clear_interactions()
    show_message("Enter filename to save Schengen airports:", "blue")

    tk.Label(input_frame, text="Filename:").grid(row=0, column=0, padx=5)
    ent_file = tk.Entry(input_frame)
    ent_file.grid(row=0, column=1)

    def on_save():
        filename = ent_file.get()
        if filename:
            if not filename.endswith(".txt"): filename += ".txt"
            if SaveSchengenAirports(airports, filename):
                show_message(f"Success: Saved to {filename}", "green")
            else:
                show_message("Result: No Schengen airports to save.", "orange")
            clear_interactions()

    tk.Button(input_frame, text="Save File", command=on_save).grid(row=0, column=2, padx=10)


def cmd_plot():
    if airports:
        show_message("Plotting Schengen Distribution...", "blue")
        PlotAirports(airports)
        display_current_plot()
    else:
        show_message("Warning: No data to plot.", "red")


def cmd_map_airports():
    if airports:
        MapAirports(airports)
        show_message(
            "Map Created: KML file generated (Google Earth). It opens automatically with Google Earth, or you can use the web version.",
            "green")
    else:
        show_message("Warning: No data to show on map.", "red")


# --- FUNCIONES DE CALIDAD EXIGIDAS PARA V1 ---

def cmd_set_schengen_all():
    """Asigna/actualiza el atributo Schengen a todos los aeropuertos cargados"""
    if not airports:
        show_message("Warning: No airport data loaded to set Schengen attribute.", "red")
        return
    clear_interactions()

    i = 0
    while i < len(airports):
        SetSchengen(airports[i])
        i += 1

    show_message(f"Success: Schengen attribute updated for all {len(airports)} airports.", "green")


def cmd_show_airports_data():
    """Muestra los datos detallados de los aeropuertos actuales mediante la interfaz gráfica"""
    if not airports:
        show_message("Warning: No airport data to show. Please load airports first.", "red")
        return
    clear_interactions()
    show_message(f"Displaying data for {len(airports)} loaded airports:", "blue")

    # Contenedor de texto con barra de desplazamiento vertical en el input_frame
    txt_display = tk.Text(input_frame, height=4, width=85, font=("Courier", 9))
    txt_display.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(input_frame, command=txt_display.yview)
    scrollbar.pack(side="right", fill="y")
    txt_display.config(yscrollcommand=scrollbar.set)

    # Cabecera de datos alineada
    txt_display.insert(tk.END, f"{'ICAO':<12}{'Latitude':<18}{'Longitude':<18}{'Schengen':<12}\n")
    txt_display.insert(tk.END, "-" * 60 + "\n")

    i = 0
    while i < len(airports):
        ap = airports[i]
        sch_status = "True" if ap.Schengen else "False"
        txt_display.insert(tk.END, f"{ap.ICAO:<12}{ap.latitude:<18.4f}{ap.longitude:<18.4f}{sch_status:<12}\n")
        i += 1

    txt_display.config(state="disabled")  # Desactivar edición manual


# Funciones v2

def cmd_load_arrivals():
    global aircrafts, airports
    clear_interactions()
    if not airports:
        show_message("Warning: Please load Airports first to match origins!", "red")
        return

    file = filedialog.askopenfilename(title="Select Arrivals File", filetypes=[("Text files", "*.txt")])
    if file:
        aircrafts = LoadArrivals(file, airports)
        show_message(f"Success: Loaded {len(aircrafts)} aircraft arrivals.", "green")


def cmd_save_flights():
    if not aircrafts:
        show_message("Warning: No aircraft data to save.", "red")
        return
    clear_interactions()
    show_message("Enter filename to save flights:", "blue")

    tk.Label(input_frame, text="Filename:").grid(row=0, column=0, padx=5)
    ent_file = tk.Entry(input_frame)
    ent_file.grid(row=0, column=1)

    def on_save_flights():
        filename = ent_file.get()
        if filename:
            if not filename.endswith(".txt"): filename += ".txt"
            SaveFlights(aircrafts, filename)
            show_message(f"Success: Flight list saved to {filename}", "green")
            clear_interactions()

    tk.Button(input_frame, text="Save Flights", command=on_save_flights).grid(row=0, column=2, padx=10)


def cmd_plot_arrivals_hour():
    if aircrafts:
        show_message("Plotting Arrivals by Hour...", "blue")
        PlotArrivals(aircrafts)
        display_current_plot()
    else:
        show_message("Warning: No aircraft data to plot.", "red")


def cmd_plot_airlines_dist():
    if aircrafts:
        show_message("Plotting Airlines Distribution...", "blue")
        PlotAirlines(aircrafts)
        display_current_plot()
    else:
        show_message("Warning: No data to plot.", "red")


def cmd_plot_schengen_v_non():
    if aircrafts:
        show_message("Plotting Schengen vs Non-Schengen Flights...", "blue")
        PlotFlightsType(aircrafts)
        display_current_plot()
    else:
        show_message("Warning: No data to plot.", "red")


def cmd_map_trajectories():
    if aircrafts:
        MapFlights(aircrafts)
        show_message(
            "Map Created: Flight trajectories generated. It opens automatically with Google Earth, or you can use the web version.",
            "green")
    else:
        show_message("Warning: No aircraft data for map.", "red")


def cmd_filter_long_distance():
    if not aircrafts:
        show_message("Warning: No aircraft data to filter. Please load arrivals first.", "red")
        return

    long_flights = LongDistanceArrivals(aircrafts)
    clear_interactions()

    if len(long_flights) > 0:
        msg = f"Success: {len(long_flights)} long distance flights filtered and stored in list."
        show_message(msg, "green")
        print(f"DEBUG: Se han guardado {len(long_flights)} objetos en la lista temporal.")
    else:
        show_message("Result: No flights longer than 2000km found.", "orange")

    root.after(3000, clear_interactions)


# Funciones v2

def cmd_build_airport_structure():
    """Carga y construye el mapa de terminales y puertas desde un archivo de texto"""
    global bcn_airport
    clear_interactions()

    file = filedialog.askopenfilename(title="Select Airport Structure File (LEBL.txt)",
                                      filetypes=[("Text files", "*.txt")])
    if file:
        res = LoadAirportStructure(file)
        if res == -1:
            show_message("Error: Failed to build airport structure. Check text files.", "red")
        else:
            bcn_airport = res
            show_message(f"Success: {bcn_airport.Code} Airport configuration built correctly.", "green")


def cmd_assign_gate_interface():
    """Permite al usuario interactuar para asignar una puerta a un avion del listado V2"""
    global bcn_airport, aircrafts
    clear_interactions()

    if bcn_airport is None:
        show_message("Warning: Build the LEBL data structure first.", "red")
        return

    if len(aircrafts) == 0:
        show_message("Warning: Load aircraft arrivals list from V2 first.", "red")
        return

    show_message("Enter the index of the aircraft from list to assign gate:", "blue")

    tk.Label(input_frame, text=f"Aircraft Index (0 - {len(aircrafts) - 1}):").grid(row=0, column=0, padx=5)
    ent_idx = tk.Entry(input_frame, width=8)
    ent_idx.grid(row=0, column=1)

    def on_assign():
        try:
            idx = int(ent_idx.get())
            if idx < 0 or idx >= len(aircrafts):
                show_message("Error: Index out of range.", "red")
                return

            selected_aircraft = aircrafts[idx]
            gate_allocated = AssignGate(bcn_airport, selected_aircraft)

            if gate_allocated == -1:
                show_message(f"Result: No free matching gate for {selected_aircraft.Id} ({selected_aircraft.Company}).",
                             "orange")
            else:
                show_message(f"Success: Aircraft {selected_aircraft.Id} assigned to Gate {gate_allocated}.", "green")
                clear_interactions()
                # Actualizar grafico de ocupación automáticamente tras asignación exitosa
                cmd_plot_gate_occupancy()
        except ValueError:
            show_message("Error: Please enter a valid numerical index.", "red")

    tk.Button(input_frame, text="Assign Gate", command=on_assign).grid(row=0, column=2, padx=10)


def cmd_plot_gate_occupancy():
    """Genera una visualización gráfica de barras de ocupación del aeropuerto en el panel"""
    global bcn_airport
    if bcn_airport is None:
        show_message("Warning: No airport structure loaded to display.", "red")
        return

    show_message("Generating Airport Map Plot...", "blue")

    # Extraemos la lista plana de ocupación mediante el core básico
    data = GateOccupancy(bcn_airport)
    if len(data) == 0:
        show_message("Result: Airport structure has no gates defined.", "orange")
        return

    # Listas auxiliares para la confección del Plot estadístico básico
    names = []
    colors = []

    i = 0
    while i < len(data):
        names.append(data[i][0])
        if data[i][1] == "occupied":
            colors.append("#ef5350")  # Rojo para ocupado
        else:
            colors.append("#66bb6a")  # Verde para libre
        i = i + 1

    # Inicialización del contenedor Matplotlib embebido
    plt.figure(figsize=(10, 4))

    # Si hay demasiadas puertas, mostramos una muestra o ajustamos etiquetas
    x_positions = range(len(names))
    plt.bar(x_positions, [1] * len(names), color=colors, edgecolor="grey", width=0.6)

    # Configuramos el formato visual de la gráfica
    plt.title(f"Airport {bcn_airport.Code} - Gate Map & Occupancy Layout", fontsize=11, fontweight="bold")
    plt.ylabel("Status Status")

    # Solo pintamos los nombres de los ticks si el tamaño de visualización es legible
    if len(names) <= 40:
        plt.xticks(x_positions, names, rotation=90, fontsize=7)
    else:
        plt.xticks([0, len(names) // 2, len(names) - 1], [names[0], "...", names[-1]], fontsize=8)

    plt.yticks([0, 1], ["", "Active"])

    # Parches estéticos manuales para simular leyenda interactiva
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor="#66bb6a", label='Free (Available)'),
                       Patch(facecolor="#ef5350", label='Occupied (Blocked)')]
    plt.legend(handles=legend_elements, loc='upper right', fontsize=8)
    plt.tight_layout()

    # Despliegue seguro en la interfaz TK
    display_current_plot()
    show_message("Success: Airport gate layout successfully plotted.", "green")


# Ventana principal del entorno gráfico
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Aviation Manager Pro - All in One")
    root.geometry("1100x820")  # Incrementado ligeramente el alto para acomodar botones V3

    # --- PANEL IZQUIERDO: Botones de control ---
    menu_frame = tk.Frame(root, width=250, bg="#f0f0f0", padx=10, pady=10)
    menu_frame.pack(side="left", fill="y")

    # SECCIÓN V1
    tk.Label(menu_frame, text="Airport Functions (V1)", font=("Arial", 11, "bold"), bg="#f0f0f0").pack(pady=5)
    tk.Button(menu_frame, text="Load Airports", width=25, command=cmd_load).pack(pady=2)
    tk.Button(menu_frame, text="Add Airport", width=25, command=cmd_add).pack(pady=2)
    tk.Button(menu_frame, text="Remove Airport", width=25, command=cmd_remove).pack(pady=2)
    tk.Button(menu_frame, text="Set Schengen Attr.", width=25, command=cmd_set_schengen_all).pack(pady=2)
    tk.Button(menu_frame, text="Show Airports Data", width=25, command=cmd_show_airports_data).pack(pady=2)
    tk.Button(menu_frame, text="Save Schengen List", width=25, command=cmd_save).pack(pady=2)
    tk.Button(menu_frame, text="Plot Schengen Dist.", width=25, command=cmd_plot).pack(pady=2)
    tk.Button(menu_frame, text="Map Airports (KML)", width=25, command=cmd_map_airports).pack(pady=2)

    # SECCIÓN V2
    tk.Label(menu_frame, text="Aircraft Functions (V2)", font=("Arial", 11, "bold"), bg="#f0f0f0").pack(pady=(10, 5))
    tk.Button(menu_frame, text="Load Arrivals", width=25, command=cmd_load_arrivals, bg="#e1f5fe").pack(pady=2)
    tk.Button(menu_frame, text="Save Flight List", width=25, command=cmd_save_flights, bg="#e1f5fe").pack(pady=2)
    tk.Button(menu_frame, text="Plot Arrivals by Hour", width=25, command=cmd_plot_arrivals_hour, bg="#e1f5fe").pack(
        pady=2)
    tk.Button(menu_frame, text="Plot Airline Dist.", width=25, command=cmd_plot_airlines_dist, bg="#e1f5fe").pack(
        pady=2)
    tk.Button(menu_frame, text="Plot Schengen Flights", width=25, command=cmd_plot_schengen_v_non, bg="#e1f5fe").pack(
        pady=2)
    tk.Button(menu_frame, text="Map Trajectories (KML)", width=25, command=cmd_map_trajectories, bg="#e1f5fe").pack(
        pady=2)
    tk.Button(menu_frame, text="Filter Long Distance", width=25, command=cmd_filter_long_distance, bg="#e1f5fe").pack(
        pady=2)

    # SECCIÓN V3
    tk.Label(menu_frame, text="Gate Management (V3)", font=("Arial", 11, "bold"), bg="#f0f0f0").pack(pady=(10, 5))
    tk.Button(menu_frame, text="Load LEBL Structure", width=25, command=cmd_build_airport_structure, bg="#e8f5e9").pack(
        pady=2)
    tk.Button(menu_frame, text="Assign Flight Gate", width=25, command=cmd_assign_gate_interface, bg="#e8f5e9").pack(
        pady=2)
    tk.Button(menu_frame, text="Plot Gate Occupancy", width=25, command=cmd_plot_gate_occupancy, bg="#e8f5e9").pack(
        pady=2)

    tk.Button(menu_frame, text="EXIT", width=20, fg="red", command=root.quit).pack(side="bottom", pady=10)

    # --- PANEL DERECHO: Graficos e Interaccion ---
    right_frame = tk.Frame(root)
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    chart_frame = tk.Frame(right_frame, bg="white", highlightbackground="gray", highlightthickness=1)
    chart_frame.pack(side="top", fill="both", expand=True)
    tk.Label(chart_frame, text="Chart Area (Graficos)", bg="white", fg="gray").pack(pady=100)

    interaction_area = tk.Frame(right_frame, height=120, highlightbackground="black", highlightthickness=1)
    interaction_area.pack(side="bottom", fill="x", pady=(10, 0))
    interaction_area.pack_propagate(False)

    tk.Label(interaction_area, text="System Messages & Interactions:", font=("Arial", 9, "bold")).pack(anchor="w",
                                                                                                       padx=5, pady=2)

    lbl_status = tk.Label(interaction_area, text="Ready.", font=("Arial", 10))
    lbl_status.pack(anchor="w", padx=10)

    input_frame = tk.Frame(interaction_area)
    input_frame.pack(fill="x", padx=10, pady=10)

    root.mainloop()