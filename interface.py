import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from airport import *
from aircraft import *

plt.show = lambda: None

# Variables globales
airports = []
aircrafts = []
canvas = None


#Funciones pest

def clear_chart_area():
    """Limpia el area del grafico actual y elimina el texto de fondo"""
    # Esto destruye cualquier cosa dentro del marco, incluido el texto "Chart Area"
    for widget in chart_frame.winfo_children():
        widget.destroy()


def display_current_plot():
    """Captura el grafico y lo mete en el hueco exacto"""
    # 1. Limpiar el area (borra el texto de "Chart Area")
    for widget in chart_frame.winfo_children():
        widget.destroy()

    fig = plt.gcf()  # Coge la gráfica que acaba de crear aircraft.py

    # 2. Meter la gráfica en el lienzo de Tkinter
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()

    # 3. 'pack' con expand=True hace que ocupe todo el espacio blanco disponible
    canvas.get_tk_widget().pack(fill="both", expand=True)

    plt.close('all')  # Limpia la memoria para la siguiente gráfica

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

    # Crear entradas de texto dentro de la ventana (reemplaza simpledialog)
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
        display_current_plot()  # Incrusta el grafico
    else:
        show_message("Warning: No data to plot.", "red")


def cmd_map_airports():
    if airports:
        MapAirports(airports)
        show_message("Map Created: KML file generated (Google Earth).", "green")
    else:
        show_message("Warning: No data to show on map.", "red")


# funciones V2

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
        show_message("Map Created: Flight trajectories generated.", "green")
    else:
        show_message("Warning: No aircraft data for map.", "red")


def cmd_filter_long_distance():
    if not aircrafts:
        show_message("Warning: No aircraft data to filter.", "red")
        return

    long_flights = LongDistanceArrivals(aircrafts)
    clear_interactions()

    if long_flights:
        show_message(f"Found {len(long_flights)} flights > 2000km. Enter filename to save:", "blue")
        tk.Label(input_frame, text="Filename:").grid(row=0, column=0, padx=5)
        ent_file = tk.Entry(input_frame)
        ent_file.grid(row=0, column=1)

        def on_save_long():
            filename = ent_file.get()
            if filename:
                if not filename.endswith(".txt"): filename += ".txt"
                SaveFlights(long_flights, filename)
                show_message(f"Success: Filtered flights saved to {filename}", "green")
                clear_interactions()

        tk.Button(input_frame, text="Save Filtered", command=on_save_long).grid(row=0, column=2, padx=10)
    else:
        show_message("Result: No flights longer than 2000km found.", "orange")


# Ventana
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Aviation Manager Pro - All in One")
    root.geometry("1100x750")  # Tamano ajustado para que quepa todo

    # --- PANEL IZQUIERDO: Botones de control ---
    menu_frame = tk.Frame(root, width=250, bg="#f0f0f0", padx=10, pady=10)
    menu_frame.pack(side="left", fill="y")

    tk.Label(menu_frame, text="Airport Functions (V1)", font=("Arial", 11, "bold"), bg="#f0f0f0").pack(pady=5)
    tk.Button(menu_frame, text="Load Airports", width=25, command=cmd_load).pack(pady=2)
    tk.Button(menu_frame, text="Add Airport", width=25, command=cmd_add).pack(pady=2)
    tk.Button(menu_frame, text="Remove Airport", width=25, command=cmd_remove).pack(pady=2)
    tk.Button(menu_frame, text="Save Schengen List", width=25, command=cmd_save).pack(pady=2)
    tk.Button(menu_frame, text="Plot Schengen Dist.", width=25, command=cmd_plot).pack(pady=2)
    tk.Button(menu_frame, text="Map Airports (KML)", width=25, command=cmd_map_airports).pack(pady=2)  # Anadido

    tk.Label(menu_frame, text="Aircraft Functions (V2)", font=("Arial", 11, "bold"), bg="#f0f0f0").pack(pady=(15, 5))
    tk.Button(menu_frame, text="Load Arrivals", width=25, command=cmd_load_arrivals, bg="#e1f5fe").pack(pady=2)
    tk.Button(menu_frame, text="Save Flight List", width=25, command=cmd_save_flights, bg="#e1f5fe").pack(pady=2)
    tk.Button(menu_frame, text="Plot Arrivals by Hour", width=25, command=cmd_plot_arrivals_hour, bg="#e1f5fe").pack(
        pady=2)
    tk.Button(menu_frame, text="Plot Airline Dist.", width=25, command=cmd_plot_airlines_dist, bg="#e1f5fe").pack(
        pady=2)
    tk.Button(menu_frame, text="Plot Schengen Flights", width=25, command=cmd_plot_schengen_v_non, bg="#e1f5fe").pack(
        pady=2)
    tk.Button(menu_frame, text="Map Trajectories (KML)", width=25, command=cmd_map_trajectories, bg="#e1f5fe").pack(
        pady=2)  # Anadido
    tk.Button(menu_frame, text="Filter Long Distance", width=25, command=cmd_filter_long_distance, bg="#fff9c4").pack(
        pady=2)  # Anadido

    tk.Button(menu_frame, text="EXIT", width=20, fg="red", command=root.quit).pack(side="bottom", pady=20)

    # --- PANEL DERECHO: Graficos e Interaccion ---
    right_frame = tk.Frame(root)
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Area Superior: Graficos (Canvas)
    chart_frame = tk.Frame(right_frame, bg="white", highlightbackground="gray", highlightthickness=1)
    chart_frame.pack(side="top", fill="both", expand=True)
    tk.Label(chart_frame, text="Chart Area (Graficos)", bg="white", fg="gray").pack(pady=100)

    # Area Inferior: Interaccion con el usuario (Inputs y Mensajes)
    interaction_area = tk.Frame(right_frame, height=120, highlightbackground="black", highlightthickness=1)
    interaction_area.pack(side="bottom", fill="x", pady=(10, 0))
    interaction_area.pack_propagate(False)  # Mantener altura fija

    tk.Label(interaction_area, text="System Messages & Interactions:", font=("Arial", 9, "bold")).pack(anchor="w",
                                                                                                       padx=5, pady=2)

    # Label para reemplazar los messagebox
    lbl_status = tk.Label(interaction_area, text="Ready.", font=("Arial", 10))
    lbl_status.pack(anchor="w", padx=10)

    # Frame dinamico para poner las cajas de texto (Entry)
    input_frame = tk.Frame(interaction_area)
    input_frame.pack(fill="x", padx=10, pady=10)

    root.mainloop()