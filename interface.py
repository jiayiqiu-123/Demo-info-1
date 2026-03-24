import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from airport import *

airports_list = []


#Funciones en botones, para que sea más user friendly

def cmd_load():
    global airports_list
    # Deja el usuario abrir el archivo para cargar
    file = filedialog.askopenfilename(title="Select Airport File", filetypes=[("Text files", "*.txt")])

    if file:
        airports_list = LoadAirports(file)
        messagebox.showinfo("Success", f"Loaded {len(airports_list)} airports from {file}")


def cmd_add():
    # Pregunta dentro de la pestaña
    code = simpledialog.askstring("Input", "Enter ICAO Code (e.g., LEBL):")
    if code: # Si ha introducido el codigo
        try:
            lat = simpledialog.askfloat("Input", "Enter Latitude (Decimal):")
            lon = simpledialog.askfloat("Input", "Enter Longitude (Decimal):")

            new_ap = Airport(code.upper(), lat, lon)
            if AddAirport(airports_list, new_ap):
                messagebox.showinfo("Success", f"Airport {code.upper()} added!")
            else:
                messagebox.showwarning("Warning", "Airport already exists.")
        except:
            messagebox.showerror("Error", "Invalid coordinates. Please enter numbers.")


def cmd_remove():
    code = simpledialog.askstring("Input", "Enter ICAO Code to remove:")
    if code:
        if RemoveAirport(airports_list, code.upper()):
            messagebox.showinfo("Success", f"Airport {code.upper()} removed.")
        else:
            messagebox.showerror("Error", "Airport not found.")


def cmd_save():
    if not airports_list:
        messagebox.showwarning("Warning", "The list is empty. Load data first.")
        return

    # pregunta el nombre que quiere nominar
    filename = simpledialog.askstring("Save As", "Enter filename (e.g., my_schengen.txt):")

    if filename:
        if not filename.endswith(".txt"):
            filename = filename + ".txt"

        if SaveSchengenAirports(airports_list, filename):
            messagebox.showinfo("Success", f"Schengen airports saved to {filename}")
        else:
            messagebox.showwarning("Result", "No Schengen airports were found to save.")


def cmd_plot():
    if airports_list:
        PlotAirports(airports_list)
    else:
        messagebox.showwarning("Warning", "No data to plot.")


def cmd_map():
    if airports_list:
        MapAirports(airports_list)
        messagebox.showinfo("Map Created", "KML file generated and opening Google Earth...")
    else:
        messagebox.showwarning("Warning", "No data to show on map.")


# La parte de pestaña

root = tk.Tk()
root.title("Airport Manager Pro")
root.geometry("400x500")

# El título
lbl = tk.Label(root, text="Airport Management System", font=("Arial", 14, "bold"))
lbl.pack(pady=20)

# Los botones con las funciones
tk.Button(root, text="Load File", width=30, command=cmd_load).pack(pady=5)
tk.Button(root, text="Add Airport", width=30, command=cmd_add).pack(pady=5)
tk.Button(root, text="Remove Airport", width=30, command=cmd_remove).pack(pady=5)
tk.Button(root, text="Save Schengen As...", width=30, command=cmd_save).pack(pady=5)
tk.Button(root, text="Show Statistics", width=30, command=cmd_plot).pack(pady=5)
tk.Button(root, text="Open Google Earth", width=30, command=cmd_map).pack(pady=5)
tk.Button(root, text="EXIT", width=30, fg="red", command=root.quit).pack(pady=30)

root.mainloop()