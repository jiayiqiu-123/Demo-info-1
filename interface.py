"""
interface.py — Airport Management System LEBL
Interfaz gráfica principal construida con tkinter.
Paleta cromática fría: azules, teals, cyans, navy.
Los gráficos se muestran embebidos en el panel derecho (sin ventana emergente).
Cubre todos los requisitos V1, V2, V3 y V4.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import math

# ── IMPORTANTE: el backend TkAgg debe fijarse ANTES de importar pyplot ──
# Sin esto FigureCanvasTkAgg no puede embeber figuras en tkinter.
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from airport import *
from aircraft import *
from LEBL import *

# ── Mapa interactivo (opcional) ──────────────────────────────────────
# Si folium + tkinterweb están instalados → mapa embebido e interactivo.
# Si no → mapa matplotlib embebido igualmente (sin tiles externos).
# Instalar con: pip install folium tkinterweb
try:
    import folium
    from tkinterweb import HtmlFrame
    HAS_WEB_MAP = False
except ImportError:
    HAS_WEB_MAP = False


# ═══════════════════════════════════════════════════════════════════════
# PALETAS DE COLORES — DARK (navy) + LIGHT (cielo)
# ═══════════════════════════════════════════════════════════════════════

DARK_THEME = {
    "bg":     "#060d1a",
    "panel":  "#0a1628",
    "card":   "#0f2240",
    "border": "#1c3558",
    "text":   "#d0e8ff",
    "textdim":"#5b8baf",
    "c_load": "#1a52a8",
    "c_save": "#0e7490",
    "c_add":  "#0c7068",
    "c_del":  "#2d3d52",
    "c_plot": "#1a5276",
    "c_map":  "#164e7a",
    "c_main": "#1d6eb0",
    "c_v4":   "#154e7a",
    "entry":  "#060d1a",
    "header": "#040c1c",
    "tree_sel":"#1d5ea0",
}

LIGHT_THEME = {
    "bg":     "#eaf4fd",
    "panel":  "#d0e8f8",
    "card":   "#e0f0fb",
    "border": "#90bedd",
    "text":   "#0a1f35",
    "textdim":"#2d6898",
    "c_load": "#1a7abf",
    "c_save": "#0a8a9a",
    "c_add":  "#0a9080",
    "c_del":  "#6fa8cc",
    "c_plot": "#1a6fa0",
    "c_map":  "#145e88",
    "c_main": "#1e85cc",
    "c_v4":   "#145e88",
    "entry":  "#f5fbff",
    "header": "#a8d4f0",
    "tree_sel":"#4aadde",
}

# C es la paleta activa — se modifica in-place en _toggle_theme()
C = dict(DARK_THEME)

# ═══════════════════════════════════════════════════════════════════════
# FUENTES
# ═══════════════════════════════════════════════════════════════════════
F = {
    "title":  ("Segoe UI", 20, "bold"),
    "h2":     ("Segoe UI", 12, "bold"),
    "h3":     ("Segoe UI", 10, "bold"),
    "normal": ("Segoe UI", 10),
    "small":  ("Segoe UI", 9),
    "mono":   ("Consolas", 10),
    "btn":    ("Segoe UI", 9, "bold"),
    "status": ("Segoe UI", 9),
}


class AirportApp:
    """Clase principal de la aplicación."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("✈  Airport Management System — LEBL")
        self.root.geometry("1340x840")
        self.root.configure(bg=C["bg"])
        self.root.minsize(1000, 660)

        # ── Estado global ────────────────────────────────────────
        self.airports           = []
        self.aircrafts          = []
        self.departures         = []
        self.merged             = []
        self.bcn                = None
        self.structure_filename = None
        self.hour_var           = tk.StringVar(value="07")

        # Tema activo ("dark" | "light")
        self._theme_name = "dark"

        # Última ruta KML generada por pestaña (para botón Google Earth)
        self._kml_paths  = {}   # {'airports': path, 'flights': path}

        # Registro de paneles
        self._panels = {}

        self._configure_styles()
        self._build_header()
        self._build_notebook()
        self._build_statusbar()
        self._set_status("Welcome to the LEBL Airport Management System  ✈", "info")

    # ══════════════════════════════════════════════════════════════
    # ESTILOS TTK
    # ══════════════════════════════════════════════════════════════

    def _configure_styles(self):
        """Aplica estilos personalizados a los widgets ttk."""
        style = ttk.Style()
        style.theme_use("clam")

        # Notebook — pestañas
        style.configure("TNotebook", background=C["bg"], borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=C["panel"], foreground=C["textdim"],
                        padding=[22, 9], font=F["h3"])
        style.map("TNotebook.Tab",
                  background=[("selected", C["c_main"])],
                  foreground=[("selected", C["text"])])

        # Treeview — tablas de datos
        style.configure("Custom.Treeview",
                        background=C["card"], foreground=C["text"],
                        rowheight=28, fieldbackground=C["card"],
                        borderwidth=0, font=F["mono"])
        style.configure("Custom.Treeview.Heading",
                        background=C["c_load"], foreground=C["text"],
                        relief="flat", font=F["h3"])
        style.map("Custom.Treeview",
                  background=[("selected", C["tree_sel"])],
                  foreground=[("selected", C["text"])])

    # ══════════════════════════════════════════════════════════════
    # CABECERA SUPERIOR
    # ══════════════════════════════════════════════════════════════

    def _build_header(self):
        self._header_frame = tk.Frame(self.root, bg=C["header"], height=68)
        self._header_frame.pack(fill="x", side="top")
        self._header_frame.pack_propagate(False)

        tk.Label(self._header_frame, text="✈  Airport Management System",
                 font=F["title"], bg=C["header"], fg=C["text"]).pack(
            side="left", padx=28, pady=14)

        # Botón de cambio de tema — extremo derecho de la cabecera
        self._theme_btn = tk.Button(
            self._header_frame,
            text="☀  Light Mode",
            command=self._toggle_theme,
            font=F["btn"],
            bg=C["c_v4"], fg=C["text"],
            relief="flat", cursor="hand2",
            pady=6, padx=14, bd=0)
        self._theme_btn.pack(side="right", padx=14, pady=16)

        tk.Label(self._header_frame, text="LEBL — Barcelona El Prat  🇪🇸",
                 font=("Segoe UI", 11), bg=C["header"], fg=C["textdim"]).pack(
            side="right", padx=14)

    # ══════════════════════════════════════════════════════════════
    # NOTEBOOK (PESTAÑAS)
    # ══════════════════════════════════════════════════════════════

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill="both", expand=True)

        self.tab_airports = tk.Frame(self.notebook, bg=C["bg"])
        self.tab_flights  = tk.Frame(self.notebook, bg=C["bg"])
        self.tab_gates    = tk.Frame(self.notebook, bg=C["bg"])

        self.notebook.add(self.tab_airports, text="  🌍  Airports  ")
        self.notebook.add(self.tab_flights,  text="  ✈️  Flights   ")
        self.notebook.add(self.tab_gates,    text="  🏢  Gate Management  ")

        self._build_tab_airports()
        self._build_tab_flights()
        self._build_tab_gates()

    # ══════════════════════════════════════════════════════════════
    # BARRA DE ESTADO INFERIOR
    # ══════════════════════════════════════════════════════════════

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=C["panel"], height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status_dot = tk.Label(bar, text="●", font=F["status"],
                                   bg=C["panel"], fg=C["c_main"])
        self.status_dot.pack(side="left", padx=(10, 4))

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self.status_var,
                 font=F["status"], bg=C["panel"], fg=C["textdim"]).pack(side="left")

        self.count_var = tk.StringVar(value="")
        tk.Label(bar, textvariable=self.count_var,
                 font=F["status"], bg=C["panel"], fg=C["textdim"]).pack(side="right", padx=12)

    def _set_status(self, msg: str, level: str = "info"):
        """Actualiza el mensaje de estado y el color del indicador."""
        dot_colors = {
            "info":    C["c_main"],
            "success": C["c_save"],
            "warning": "#5b8baf",
            "error":   "#4a6fa5",
        }
        self.status_var.set(msg)
        self.status_dot.config(fg=dot_colors.get(level, C["c_main"]))

    def _toggle_theme(self):
        """
        Alterna entre tema oscuro (navy) y tema claro (cielo).
        Destruye y reconstruye toda la UI — garantiza que TODOS los widgets
        (matplotlib, treeview, frames, entries) usen el nuevo tema.
        El estado de datos (airports, aircrafts, bcn…) se conserva en self.
        """
        if self._theme_name == "dark":
            C.update(LIGHT_THEME)
            self._theme_name  = "light"
            next_btn_text     = "🌙  Dark Mode"
        else:
            C.update(DARK_THEME)
            self._theme_name  = "dark"
            next_btn_text     = "☀  Light Mode"

        # Cerrar todas las figuras matplotlib abiertas antes de destruir widgets
        plt.close('all')

        # Destruir todos los widgets existentes
        for w in self.root.winfo_children():
            w.destroy()

        # Resetear referencias internas que apuntan a widgets destruidos
        self._panels = {}
        self._term_buttons = {}

        # Reconstruir con el nuevo tema
        self.root.configure(bg=C["bg"])
        self._configure_styles()
        self._build_header()
        self._theme_btn.config(text=next_btn_text)  # Corregir texto del botón recién creado
        self._build_notebook()
        self._build_statusbar()

        # Restaurar datos en las tablas
        if self.airports:
            self._refresh_airports_tree()
        if self.aircrafts:
            self._refresh_flights_tree()
        if self.bcn:
            total_gates    = sum(len(area.Gates) for t in self.bcn.Terminals
                                 for area in t.BoardingAreas)
            total_airlines = sum(len(t.Airlines) for t in self.bcn.Terminals)
            self.gate_info_var.set(
                f"{self.bcn.Code}  |  {len(self.bcn.Terminals)} terminals  |  "
                f"{total_gates} gates  |  {total_airlines} airlines registered")
            self._populate_terminal_selector()
            self._refresh_gate_tree()

        theme_label = "Light" if self._theme_name == "light" else "Dark"
        self._set_status(f"Theme switched to {theme_label} Mode", "info")

    def _call_no_ge(self, func, *args, **kwargs):
        """
        Llama a func() con os.startfile temporalmente desactivado.
        Evita que MapAirports / MapFlights abran Google Earth automáticamente
        al final de su ejecución — el usuario abre GE solo cuando pulsa el botón.
        """
        original_startfile = getattr(os, 'startfile', None)
        os.startfile = lambda *a, **kw: None   # no-op mientras generamos el KML
        try:
            return func(*args, **kwargs)
        finally:
            # Restaurar siempre, incluso si func() lanza una excepción
            if original_startfile is not None:
                os.startfile = original_startfile
            elif hasattr(os, 'startfile'):
                del os.startfile

    def _make_log_panel(self, parent, attr_name: str):
        """
        Construye un panel de Operation Log reutilizable.
        Crea un tk.Text scrollable en `parent` y lo guarda en self.<attr_name>.
        Llamar así en cada pestaña:
            self._make_log_panel(left_frame, '_ap_log')   # Airports
            self._make_log_panel(left_frame, '_fl_log')   # Flights
        El método _log(attr_name, lines, level) escribe en él.
        """
        outer = tk.Frame(parent, bg=C["panel"])
        outer.pack(fill="both", expand=True, padx=12, pady=(4, 8))

        tk.Label(outer, text="📋  Operation Log",
                 font=F["small"], bg=C["panel"], fg=C["textdim"]).pack(
            anchor="w", pady=(0, 3))

        log_frame = tk.Frame(outer, bg=C["card"],
                             highlightbackground=C["border"], highlightthickness=1)
        log_frame.pack(fill="both", expand=True)

        log_widget = tk.Text(log_frame,
                             font=("Consolas", 8),
                             bg=C["card"], fg=C["text"],
                             relief="flat", bd=0,
                             wrap="word",
                             state="disabled",
                             cursor="arrow")
        log_sb = ttk.Scrollbar(log_frame, orient="vertical",
                               command=log_widget.yview)
        log_widget.configure(yscrollcommand=log_sb.set)
        log_sb.pack(side="right", fill="y")
        log_widget.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        # Guardar el widget como atributo dinámico (ej: self._ap_log)
        setattr(self, attr_name, log_widget)

    def _log(self, attr_name: str, lines: list, level: str = "info"):
        """
        Escribe en cualquier log panel identificado por attr_name.
        Funciona para '_ap_log', '_fl_log' y '_gate_log'.
        level: "info" | "success" | "warning" | "error"
        """
        widget = getattr(self, attr_name, None)
        if widget is None:
            return
        icons = {"info": "ℹ", "success": "✅", "warning": "⚠", "error": "❌"}
        icon  = icons.get(level, "ℹ")

        widget.configure(state="normal")
        if widget.get("1.0", "end").strip():
            widget.insert("end", "\n─────────────────────\n")
        for i, line in enumerate(lines):
            prefix = f"{icon} " if i == 0 else "   "
            widget.insert("end", f"{prefix}{line}\n")
        widget.see("end")
        widget.configure(state="disabled")

    def _log_gate(self, lines: list, level: str = "info"):
        """Atajo de compatibilidad: escribe en el log de Gate Management."""
        self._log('_gate_log', lines, level)

    # ══════════════════════════════════════════════════════════════
    # UTILIDADES DE WIDGETS
    # ══════════════════════════════════════════════════════════════

    def _make_btn(self, parent, text: str, command, color: str = None) -> tk.Button:
        """Crea un botón flat con el estilo de la aplicación."""
        bg = color or C["c_main"]
        return tk.Button(parent, text=text, command=command,
                         font=F["btn"], bg=bg, fg=C["text"],
                         activebackground=C["card"], activeforeground=C["text"],
                         relief="flat", cursor="hand2", pady=7, bd=0)

    def _make_section(self, parent, title: str) -> tk.LabelFrame:
        """Crea un LabelFrame con el estilo estándar para agrupar controles."""
        return tk.LabelFrame(parent, text=f"  {title}  ",
                             font=F["small"], bg=C["panel"], fg=C["textdim"],
                             bd=1, relief="groove", highlightbackground=C["border"])

    def _make_treeview(self, parent, columns: list, widths: list):
        """Crea un Treeview con scrollbar. Devuelve (frame_contenedor, tree)."""
        frame = tk.Frame(parent, bg=C["bg"])
        tree  = ttk.Treeview(frame, columns=columns, show="headings",
                             style="Custom.Treeview", selectmode="browse")
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center", minwidth=50)
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return frame, tree

    # ══════════════════════════════════════════════════════════════
    # SISTEMA DE GRÁFICOS EMBEBIDOS
    # Estos tres métodos gestionan la visualización inline de plots.
    # ══════════════════════════════════════════════════════════════

    def _capture_plot(self, plot_func, *args, **kwargs):
        """
        Ejecuta una función de plot PERO intercepta plt.show() para
        que no abra una ventana emergente.
        Cierra todas las figuras anteriores antes de crear la nueva,
        para evitar que plots acumulados se superpongan al reutilizar el canvas.
        Devuelve la Figure matplotlib generada.
        """
        # Cerrar todas las figuras abiertas ANTES de crear la nueva.
        # Esto garantiza que al llamar de nuevo al mismo botón (o a otro)
        # no se mezclen figuras antiguas con la nueva.
        plt.close('all')

        figs_before   = set(plt.get_fignums())
        original_show = plt.show
        plt.show      = lambda *a, **kw: None  # No-op: desactiva el popup

        try:
            plot_func(*args, **kwargs)
        finally:
            plt.show = original_show   # Siempre restaurar, aunque haya excepción

        figs_after = set(plt.get_fignums())
        new_figs   = figs_after - figs_before
        fig_num    = max(new_figs) if new_figs else (max(figs_after) if figs_after else None)
        return plt.figure(fig_num) if fig_num else plt.gcf()

    def _style_figure(self, fig):
        """
        Aplica la paleta fría al fondo y ejes de la figura embebida.
        Así el gráfico tiene el mismo aspecto visual que la interfaz.
        """
        fig.patch.set_facecolor(C["panel"])
        for ax in fig.get_axes():
            ax.set_facecolor(C["card"])
            ax.tick_params(colors=C["textdim"], labelcolor=C["textdim"])
            ax.xaxis.label.set_color(C["textdim"])
            ax.yaxis.label.set_color(C["textdim"])
            ax.title.set_color(C["text"])
            for spine in ax.spines.values():
                spine.set_edgecolor(C["border"])
            leg = ax.get_legend()
            if leg:
                leg.get_frame().set_facecolor(C["card"])
                leg.get_frame().set_edgecolor(C["border"])
                for txt in leg.get_texts():
                    txt.set_color(C["text"])

    def _show_plot(self, fig, tab_key: str):
        """
        Muestra una figura matplotlib embebida en el panel derecho.
        Oculta tabla y split_view (si existen) y muestra el canvas matplotlib.
        """
        panel = self._panels[tab_key]

        panel['table'].pack_forget()
        if panel.get('split_view'):
            panel['split_view'].pack_forget()

        if panel.get('canvas'):
            try:
                panel['canvas'].get_tk_widget().destroy()
            except Exception:
                pass
            panel['canvas'] = None

        for w in panel['plot_area'].winfo_children():
            w.destroy()

        self._style_figure(fig)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=panel['plot_area'])
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        panel['canvas'] = canvas

        panel['plot_area'].pack(fill="both", expand=True)
        panel['back_btn'].pack(side="right", padx=8, pady=2)

        # Botón Google Earth — aparece a la izquierda de "Back to Table"
        # solo cuando hay un KML generado para esta pestaña
        self._update_ge_button(tab_key)

    def _back_to_table(self, tab_key: str):
        """Oculta gráfico/split_view, KML button, y vuelve a mostrar la tabla."""
        panel = self._panels[tab_key]
        panel['plot_area'].pack_forget()
        if panel.get('split_view'):
            panel['split_view'].pack_forget()
        panel['back_btn'].pack_forget()
        # Ocultar botón GE y label de aviso si existen
        if panel.get('ge_btn'):
            panel['ge_btn'].pack_forget()
        if panel.get('ge_lbl'):
            panel['ge_lbl'].pack_forget()
        plt.close('all')
        panel['table'].pack(fill="both", expand=True)

    def _update_ge_button(self, tab_key: str):
        """
        Muestra u oculta el botón de Google Earth para la pestaña indicada.
        Si hay KML → muestra botón a la izquierda de "Back to Table".
        Si GE no está instalado → añade un label de aviso a la derecha del botón.
        """
        panel    = self._panels[tab_key]
        kml_path = self._kml_paths.get(tab_key)
        if not kml_path or not os.path.exists(kml_path):
            return

        # Crear el botón GE si aún no existe en el panel
        if not panel.get('ge_btn'):
            top_bar = panel.get('top_bar')
            if top_bar is None:
                return
            btn = tk.Button(top_bar,
                            text="🌍  Open in Google Earth",
                            command=lambda k=tab_key: self._open_ge(k),
                            font=F["btn"],
                            bg=C["c_map"], fg=C["text"],
                            relief="flat", cursor="hand2",
                            pady=6, padx=10, bd=0)
            panel['ge_btn'] = btn
            # Label para cuando GE no está disponible
            ge_lbl = tk.Label(top_bar, text="", font=("Segoe UI", 8),
                              bg=C["bg"], fg="#5b8baf")
            panel['ge_lbl'] = ge_lbl

        panel['ge_btn'].pack(side="right", padx=(0, 4), pady=2)

    def _open_ge(self, tab_key: str):
        """
        Intenta abrir el fichero KML con Google Earth.
        Si GE no está instalado → muestra aviso junto al botón.
        """
        panel    = self._panels[tab_key]
        kml_path = self._kml_paths.get(tab_key, "")
        if not kml_path or not os.path.exists(kml_path):
            self._set_status("KML file not found — generate the map first", "warning")
            return
        try:
            os.startfile(kml_path)   # Windows: abre el fichero con la app registrada para .kml
            self._set_status(f"Opened {os.path.basename(kml_path)} in Google Earth", "success")
            if panel.get('ge_lbl'):
                panel['ge_lbl'].pack_forget()
        except (AttributeError, OSError):
            # os.startfile no existe en Mac/Linux, o GE no está instalado
            msg = f"Google Earth not found — KML saved: {kml_path}"
            if panel.get('ge_lbl'):
                panel['ge_lbl'].config(text="⚠ Google Earth not found — KML saved (see status bar)")
                panel['ge_lbl'].pack(side="right", padx=(0, 4))
            self._set_status(f"Google Earth not found. KML file: {kml_path}", "warning")

    def _make_right_panel(self, tab, tab_key: str, title: str,
                          columns: list, widths: list):
        """
        Construye el panel derecho estándar con tabla y área de gráfico.
        Guarda las referencias en self._panels[tab_key].
        Devuelve (right_frame, tree, count_label).
        """
        right = tk.Frame(tab, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True, padx=14, pady=14)

        # Barra superior: título | botón "volver" (oculto) | contador
        top = tk.Frame(right, bg=C["bg"])
        top.pack(fill="x", pady=(0, 8))

        tk.Label(top, text=title, font=F["h2"],
                 bg=C["bg"], fg=C["text"]).pack(side="left")

        # El botón "volver" no se hace pack() ahora — solo se muestra cuando hay un plot
        back_btn = self._make_btn(top, "◀  Back to Table",
                                  lambda k=tab_key: self._back_to_table(k), C["c_v4"])

        count_lbl = tk.Label(top, text="", font=F["small"],
                             bg=C["bg"], fg=C["textdim"])
        count_lbl.pack(side="right")

        # Contenedor de contenido (tabla o gráfico — nunca los dos a la vez)
        content = tk.Frame(right, bg=C["bg"])
        content.pack(fill="both", expand=True)

        # Tabla (visible inicialmente)
        table_f, tree = self._make_treeview(content, columns, widths)
        table_f.pack(fill="both", expand=True)

        # Área de gráfico (oculta inicialmente)
        plot_area = tk.Frame(content, bg=C["panel"])

        # Guardar referencias para _show_plot / _back_to_table
        self._panels[tab_key] = {
            'table':     table_f,
            'plot_area': plot_area,
            'back_btn':  back_btn,
            'top_bar':   top,
            'canvas':    None,
            'ge_btn':    None,
            'ge_lbl':    None,
        }

        return right, tree, count_lbl

    # ══════════════════════════════════════════════════════════════
    # TAB 1 — AIRPORTS (V1)
    # ══════════════════════════════════════════════════════════════

    def _build_tab_airports(self):
        tab = self.tab_airports

        # ── Panel izquierdo ──────────────────────────────────────
        left = tk.Frame(tab, bg=C["panel"], width=270)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🌍  Airport Management",
                 font=F["h2"], bg=C["panel"], fg=C["text"]).pack(
            pady=(18, 8), padx=16, anchor="w")

        s = self._make_section(left, "📂  File")
        s.pack(fill="x", padx=12, pady=5)
        self._make_btn(s, "📂  Load Airports File",     self.load_airports,  C["c_load"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s, "💾  Save Schengen Airports", self.save_schengen,  C["c_save"]).pack(pady=(0,6), padx=8, fill="x")

        s2 = self._make_section(left, "✏️  Add Airport")
        s2.pack(fill="x", padx=12, pady=5)
        for label_text, var_name in [("ICAO Code (4 chars):", "ap_code_var"),
                                      ("Latitude (decimal):",  "ap_lat_var"),
                                      ("Longitude (decimal):", "ap_lon_var")]:
            tk.Label(s2, text=label_text, font=F["small"],
                     bg=C["panel"], fg=C["textdim"]).pack(anchor="w", padx=8, pady=(5, 0))
            var = tk.StringVar()
            setattr(self, var_name, var)
            tk.Entry(s2, textvariable=var, font=F["mono"],
                     bg=C["entry"], fg=C["text"], insertbackground=C["text"],
                     relief="flat", bd=4, highlightthickness=0).pack(fill="x", padx=8, pady=(0, 2))

        self._make_btn(s2, "➕  Add Airport",     self.add_airport,    C["c_add"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s2, "🗑️  Delete Selected", self.delete_airport, C["c_del"]).pack(pady=(0,6), padx=8, fill="x")

        s3 = self._make_section(left, "🔄  Attributes")
        s3.pack(fill="x", padx=12, pady=5)
        self._make_btn(s3, "🔄  Update Schengen Status", self.set_schengen_all, C["c_v4"]).pack(pady=4, padx=8, fill="x")

        # ── Buscador ICAO inline ──────────────────────────────────
        tk.Label(s3, text="🔍  Search ICAO:", font=F["small"],
                 bg=C["panel"], fg=C["textdim"]).pack(anchor="w", padx=8, pady=(5, 0))
        srch_row = tk.Frame(s3, bg=C["panel"])
        srch_row.pack(fill="x", padx=8, pady=(2, 6))
        self.ap_search_var = tk.StringVar()
        srch_entry = tk.Entry(srch_row, textvariable=self.ap_search_var,
                              font=F["mono"], bg=C["entry"], fg=C["text"],
                              insertbackground=C["text"], relief="flat",
                              bd=4, highlightthickness=0)
        srch_entry.pack(side="left", fill="x", expand=True)
        tk.Button(srch_row, text="✕",
                  command=lambda: self.ap_search_var.set(""),
                  font=("Segoe UI", 8, "bold"),
                  bg=C["c_del"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  padx=6, pady=0, bd=0).pack(side="right", padx=(3, 0))
        self.ap_search_var.trace_add("write", lambda *_: self._filter_airports_tree())

        s4 = self._make_section(left, "📊  Visualize")
        s4.pack(fill="x", padx=12, pady=5)
        self._make_btn(s4, "📊  Schengen Bar Chart",   self.plot_airports, C["c_plot"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s4, "🗺️  Show in Google Earth", self.map_airports,  C["c_map"]).pack(pady=(0,6), padx=8, fill="x")

        # ── Operation Log — rellena el espacio restante del panel izquierdo
        self._make_log_panel(left, '_ap_log')
        _, self.ap_tree, self.ap_count_lbl = self._make_right_panel(
            tab, 'airports', "Loaded Airports",
            ["ICAO", "Latitude", "Longitude", "Schengen"],
            [110, 150, 150, 110])

        # Tags de color para filas Schengen / no Schengen
        self.ap_tree.tag_configure("schengen",     foreground="#7ec8e3")   # Azul claro
        self.ap_tree.tag_configure("non_schengen", foreground=C["textdim"])

    # ── Métodos V1 ──────────────────────────────────────────────

    def load_airports(self):
        fn = filedialog.askopenfilename(title="Select Airports File",
                                        filetypes=[("Text files", "*.txt"), ("All", "*.*")])
        if not fn: return
        data = LoadAirports(fn)
        self.airports = data if data else []
        self._refresh_airports_tree()
        n   = len(self.airports)
        sch = sum(1 for a in self.airports if a.Schengen)
        msg = f"Loaded {n} airport{'s' if n!=1 else ''} from {os.path.basename(fn)}"
        self._set_status(msg, "success")
        self._log('_ap_log', [msg, f"  ✅ {sch} Schengen  |  ❌ {n-sch} non-Schengen"], "success")

    def add_airport(self):
        code = self.ap_code_var.get().strip().upper()
        lat_str, lon_str = self.ap_lat_var.get().strip(), self.ap_lon_var.get().strip()
        if not code or len(code) != 4:
            self._log('_ap_log', ["Invalid ICAO code — must be exactly 4 characters."], "warning"); return
            return
        try:
            lat, lon = float(lat_str), float(lon_str)
        except ValueError:
            self._log('_ap_log', ["Invalid coordinates — Latitude and Longitude must be valid numbers."], "warning"); return
            return
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            self._log('_ap_log', ["Out of range — Latitude: −90 to 90°  |  Longitude: −180 to 180°."], "warning"); return
            return
        new_ap = Airport(code, lat, lon)
        SetSchengen(new_ap)
        if AddAirport(self.airports, new_ap):
            self._refresh_airports_tree()
            self.ap_code_var.set(""); self.ap_lat_var.set(""); self.ap_lon_var.set("")
            msg = f"Added {code}  (Lat {lat:.4f}°, Lon {lon:.4f}°)  —  Schengen: {new_ap.Schengen}"
            self._set_status(f"Airport {code} added (Schengen: {new_ap.Schengen})", "success")
            self._log('_ap_log', [msg], "success")
        else:
            # log already written below
            self._set_status(f"Airport {code} already in list", "warning")
            self._log('_ap_log', [f"{code} already in list — not added"], "warning")

    def delete_airport(self):
        sel = self.ap_tree.selection()
        if not sel:
            self._log('_ap_log', ["Select an airport in the table first."], "warning")
            return
        code = self.ap_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm Delete", f"Delete airport '{code}' from the list?"):
            if RemoveAirport(self.airports, code):
                self._refresh_airports_tree()
                self._set_status(f"Airport {code} deleted", "success")
                self._log('_ap_log', [f"Deleted {code} from list"], "warning")

    def set_schengen_all(self):
        if not self.airports:
            self._log('_ap_log', ["No airports loaded — use Load Airports File first."], "warning"); return
        for ap in self.airports: SetSchengen(ap)
        self._refresh_airports_tree()
        count = sum(1 for ap in self.airports if ap.Schengen)
        non   = len(self.airports) - count
        self._set_status(f"Schengen updated: {count} Schengen, {non} non-Schengen", "success")
        self._log('_ap_log',
                  [f"Schengen status updated for {len(self.airports)} airports",
                   f"  ✅ {count} Schengen  |  ❌ {non} non-Schengen"],
                  "success")

    def _filter_airports_tree(self):
        """
        Filtra la tabla de aeropuertos según el texto del buscador ICAO.
        Si el campo está vacío muestra todos los aeropuertos.
        """
        query = self.ap_search_var.get().strip().upper()
        for item in self.ap_tree.get_children():
            self.ap_tree.delete(item)

        matches = [ap for ap in self.airports
                   if not query or query in ap.ICAO.upper()] if self.airports else []

        for ap in matches:
            tag = "schengen" if ap.Schengen else "non_schengen"
            self.ap_tree.insert("", "end", values=(
                ap.ICAO, f"{ap.latitude:.4f}°", f"{ap.longitude:.4f}°",
                "✅ Yes" if ap.Schengen else "❌ No"), tags=(tag,))

        n   = len(self.airports)
        sch = sum(1 for a in self.airports if a.Schengen)
        if query:
            self.ap_count_lbl.config(
                text=f"Showing {len(matches)} of {n} airports  —  filter: \"{query}\"")
        else:
            self.ap_count_lbl.config(
                text=f"{n} airports  |  ✅ {sch} Schengen  |  ❌ {n-sch} non-Schengen")
        self.count_var.set(f"Airports loaded: {n}")

    def save_schengen(self):
        if not self.airports:
            self._log('_ap_log', ["No airports loaded — nothing to save."], "warning"); return
        fn = filedialog.asksaveasfilename(title="Save Schengen Airports",
                                          defaultextension=".txt",
                                          filetypes=[("Text files", "*.txt")])
        if not fn: return
        result = SaveSchengenAirports(self.airports, fn)
        if result == -1:
            # logged below
            self._set_status("Nothing saved — no Schengen airports", "warning")
            self._log('_ap_log', ["Save failed — no Schengen airports in list"], "warning")
        else:
            count = sum(1 for ap in self.airports if ap.Schengen)
            fname = os.path.basename(fn)
            self._set_status(f"Saved {count} Schengen airports to {fname}", "success")
            self._log('_ap_log', [f"Saved {count} Schengen airports", f"  → {fname}"], "success")

    def plot_airports(self):
        """Muestra el gráfico de barras apiladas Schengen / no-Schengen embebido."""
        if not self.airports:
            self._log('_ap_log', ["No airports loaded — use Load Airports File first."], "warning"); return
        fig = self._capture_plot(PlotAirports, self.airports)
        self._show_plot(fig, 'airports')
        sch = sum(1 for a in self.airports if a.Schengen)
        self._set_status("Schengen bar chart displayed", "info")
        self._log('_ap_log',
                  [f"Schengen bar chart — {len(self.airports)} airports",
                   f"  ✅ {sch} Schengen  |  ❌ {len(self.airports)-sch} non-Schengen"],
                  "info")

    def map_airports(self):
        """Mapa embebido + genera KML sin abrir GE automáticamente."""
        if not self.airports:
            self._log('_ap_log', ["No airports loaded — use Load Airports File first."], "warning"); return
        self._call_no_ge(MapAirports, self.airports)
        kml_abs = os.path.abspath("airports_map.kml")
        self._kml_paths['airports'] = kml_abs

        if HAS_WEB_MAP:
            html = self._create_airports_html()
            self._show_html(html, 'airports')
            self._set_status("Interactive airport map displayed  (folium)", "info")
        else:
            fig = self._capture_plot(self._create_map_matplotlib, airports=self.airports)
            self._show_plot(fig, 'airports')
            self._set_status("Airport map displayed", "info")
        self._log('_ap_log',
                  [f"Airport map — {len(self.airports)} airports plotted",
                   f"  KML saved: airports_map.kml",
                   f"  Press 🌍 to open in Google Earth"],
                  "info")

    def _refresh_airports_tree(self):
        """Reconstruye la tabla de aeropuertos con los datos actuales (limpia el filtro)."""
        # Limpiar el buscador para mostrar todos los aeropuertos
        if hasattr(self, 'ap_search_var'):
            self.ap_search_var.set("")
        # _filter_airports_tree se dispara sola por el trace; si no existe aún, reconstruir
        else:
            for item in self.ap_tree.get_children(): self.ap_tree.delete(item)
            for ap in self.airports:
                tag = "schengen" if ap.Schengen else "non_schengen"
                self.ap_tree.insert("", "end", values=(
                    ap.ICAO, f"{ap.latitude:.4f}°", f"{ap.longitude:.4f}°",
                    "✅ Yes" if ap.Schengen else "❌ No"), tags=(tag,))
            n   = len(self.airports)
            sch = sum(1 for a in self.airports if a.Schengen)
            self.ap_count_lbl.config(
                text=f"{n} airports  |  ✅ {sch} Schengen  |  ❌ {n-sch} non-Schengen")
            self.count_var.set(f"Airports loaded: {n}")

    # ══════════════════════════════════════════════════════════════
    # TAB 2 — FLIGHTS (V2)
    # ══════════════════════════════════════════════════════════════

    def _build_tab_flights(self):
        tab = self.tab_flights

        # ── Panel izquierdo ──────────────────────────────────────
        left = tk.Frame(tab, bg=C["panel"], width=270)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="✈️  Flight Management",
                 font=F["h2"], bg=C["panel"], fg=C["text"]).pack(
            pady=(18, 8), padx=16, anchor="w")

        s = self._make_section(left, "📂  File")
        s.pack(fill="x", padx=12, pady=5)
        self._make_btn(s, "📂  Load Arrivals", self.load_arrivals, C["c_load"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s, "💾  Save Flights",  self.save_flights,  C["c_save"]).pack(pady=(0,6), padx=8, fill="x")

        s2 = self._make_section(left, "📊  Plots  (inline)")
        s2.pack(fill="x", padx=12, pady=5)
        self._make_btn(s2, "⏰  Arrivals per Hour",    self.plot_arrivals,     C["c_plot"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s2, "🏢  Arrivals per Airline", self.plot_airlines,     C["c_plot"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s2, "🌍  Schengen vs Non-Sch",  self.plot_flights_type, C["c_plot"]).pack(pady=(0,6), padx=8, fill="x")

        s3 = self._make_section(left, "🗺️  Maps  (inline)")
        s3.pack(fill="x", padx=12, pady=5)
        self._make_btn(s3, "🌐  All Trajectories",         self.map_flights,       C["c_map"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s3, "✈️  Long Distance (>2000 km)", self.map_long_distance, C["c_map"]).pack(pady=(0,6), padx=8, fill="x")

        # ── Operation Log — rellena el espacio restante del panel izquierdo
        self._make_log_panel(left, '_fl_log')
        right = tk.Frame(tab, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True, padx=14, pady=14)

        # Barra superior
        top = tk.Frame(right, bg=C["bg"])
        top.pack(fill="x", pady=(0, 8))
        tk.Label(top, text="Arrivals List",
                 font=F["h2"], bg=C["bg"], fg=C["text"]).pack(side="left")
        back_btn = self._make_btn(top, "◀  Back to Table",
                                  lambda: self._back_to_table('flights'), C["c_v4"])
        self.fl_count_lbl = tk.Label(top, text="No flights loaded",
                                      font=F["small"], bg=C["bg"], fg=C["textdim"])
        self.fl_count_lbl.pack(side="right")

        # Contenedor de contenido
        content = tk.Frame(right, bg=C["bg"])
        content.pack(fill="both", expand=True)

        # — Modo 1: Tabla (visible por defecto)
        cols   = ["ID", "Origin", "Arrival", "Airline", "Schengen", "Distance to LEBL"]
        widths = [110, 90, 85, 85, 95, 130]
        table_f, self.fl_tree = self._make_treeview(content, cols, widths)
        table_f.pack(fill="both", expand=True)

        self.fl_tree.tag_configure("schengen",     foreground="#7ec8e3")
        self.fl_tree.tag_configure("non_schengen", foreground=C["textdim"])
        self.fl_tree.tag_configure("long_dist",    foreground="#a5f3fc")

        # — Modo 2: Área de gráfico (para plots que no son de aerolíneas)
        plot_area = tk.Frame(content, bg=C["panel"])

        # — Modo 3: Vista dividida filtro + plot aerolíneas
        split_view = tk.Frame(content, bg=C["bg"])

        #   Izquierda: panel de filtro (anchura fija)
        filter_pane = tk.Frame(split_view, bg=C["panel"], width=215)
        filter_pane.pack(side="left", fill="y")
        filter_pane.pack_propagate(False)

        # Separador vertical
        tk.Frame(split_view, bg=C["border"], width=1).pack(side="left", fill="y")

        #   Derecha: área de plot de aerolíneas
        airline_plot = tk.Frame(split_view, bg=C["panel"])
        airline_plot.pack(side="right", fill="both", expand=True)

        # Guardar todas las referencias
        self._panels['flights'] = {
            'table':        table_f,
            'plot_area':    plot_area,
            'back_btn':     back_btn,
            'top_bar':      top,
            'canvas':       None,
            'split_view':   split_view,
            'filter_pane':  filter_pane,
            'airline_plot': airline_plot,
            'ge_btn':       None,
            'ge_lbl':       None,
        }

    # ── Métodos V2 ──────────────────────────────────────────────

    def load_arrivals(self):
        if not self.airports:
            self._log('_fl_log', ["Load airports first (Airports tab) — they are needed to get origin coordinates."], "warning")
            return
        fn = filedialog.askopenfilename(title="Select Arrivals File",
                                        filetypes=[("Text files", "*.txt"), ("All", "*.*")])
        if not fn: return
        data = LoadArrivals(fn, self.airports)
        self.aircrafts = data if data else []
        self._refresh_flights_tree()
        n   = len(self.aircrafts)
        sch = sum(1 for ac in self.aircrafts if ac.origin and ac.origin.Schengen)
        msg = f"Loaded {n} arrival{'s' if n!=1 else ''} from {os.path.basename(fn)}"
        self._set_status(msg, "success")
        self._log('_fl_log',
                  [msg, f"  ✅ {sch} Schengen  |  ❌ {n-sch} non-Schengen"],
                  "success")

    def save_flights(self):
        if not self.aircrafts:
            self._log('_fl_log', ["No flights loaded — use Load Arrivals first."], "warning"); return
        fn = filedialog.asksaveasfilename(title="Save Flights",
                                          defaultextension=".txt",
                                          filetypes=[("Text files", "*.txt")])
        if not fn: return
        result = SaveFlights(self.aircrafts, fn)
        if result == -1:
            self._log('_fl_log', ["Save failed — list is empty."], "error")
        else:
            fname = os.path.basename(fn)
            self._set_status(f"Saved {len(self.aircrafts)} flights to {fname}", "success")
            self._log('_fl_log', [f"Saved {len(self.aircrafts)} flights", f"  → {fname}"], "success")

    def plot_arrivals(self):
        """Gráfico de llegadas por hora — se muestra embebido en el panel derecho."""
        if not self.aircrafts:
            self._log('_fl_log', ["No flights loaded — use Load Arrivals first."], "warning"); return
        fig = self._capture_plot(PlotArrivals, self.aircrafts)
        self._show_plot(fig, 'flights')
        self._set_status("Arrivals-per-hour chart displayed", "info")
        self._log('_fl_log', [f"Arrivals per hour — {len(self.aircrafts)} flights"], "info")

    def plot_flights_type(self):
        """Gráfico apilado Schengen / no-Schengen — embebido."""
        if not self.aircrafts:
            self._log('_fl_log', ["No flights loaded — use Load Arrivals first."], "warning"); return
        fig = self._capture_plot(PlotFlightsType, self.aircrafts)
        self._show_plot(fig, 'flights')
        sch = sum(1 for ac in self.aircrafts if ac.origin and ac.origin.Schengen)
        self._set_status("Schengen/Non-Schengen chart displayed", "info")
        self._log('_fl_log',
                  [f"Schengen vs Non-Schengen chart",
                   f"  ✅ {sch} Schengen  |  ❌ {len(self.aircrafts)-sch} non-Schengen"],
                  "info")

    def plot_airlines(self):
        """
        Construye la vista dividida inline:
        — Izquierda: panel de filtro con checkboxes (aerolíneas + nº vuelos)
        — Derecha:   gráfico matplotlib actualizado al pulsar 'Plot'
        El filtro se reconstruye con los datos actuales cada vez que se llama.
        """
        if not self.aircrafts:
            self._log('_fl_log', ["No flights loaded — use Load Arrivals first."], "warning"); return
        airlines = sorted(set(ac.Company for ac in self.aircrafts if ac.Company))
        if not airlines:
            self._log('_fl_log', ["No airline data available in the loaded flights."], "warning")
            return

        panel = self._panels['flights']

        # ── Reconstruir el panel de filtro ───────────────────────
        for w in panel['filter_pane'].winfo_children():
            w.destroy()

        self._fl_filter_vars = {}   # airline_code → BooleanVar

        counts = {}
        for ac in self.aircrafts:
            if ac.Company:
                counts[ac.Company] = counts.get(ac.Company, 0) + 1

        # Título
        tk.Label(panel['filter_pane'],
                 text="✈  Filter Airlines",
                 font=F["h3"], bg=C["panel"], fg=C["text"]).pack(
            pady=(10, 2), padx=8, anchor="w")
        tk.Label(panel['filter_pane'],
                 text=f"{len(airlines)} airlines in dataset",
                 font=F["small"], bg=C["panel"], fg=C["textdim"]).pack(
            padx=8, anchor="w")

        # ── Caja de búsqueda ─────────────────────────────────────
        # Filtra los checkboxes en tiempo real según el texto escrito
        srch_frame = tk.Frame(panel['filter_pane'], bg=C["panel"])
        srch_frame.pack(fill="x", padx=8, pady=(5, 2))
        tk.Label(srch_frame, text="🔍", font=F["small"],
                 bg=C["panel"], fg=C["textdim"]).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(srch_frame, textvariable=search_var,
                                font=("Consolas", 8),
                                bg=C["entry"], fg=C["text"],
                                insertbackground=C["text"],
                                relief="flat", bd=3, highlightthickness=0)
        search_entry.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Botones Select All / None
        btn_f = tk.Frame(panel['filter_pane'], bg=C["panel"])
        btn_f.pack(fill="x", padx=8, pady=5)

        def _select_all():
            for v in self._fl_filter_vars.values(): v.set(True)
        def _deselect_all():
            for v in self._fl_filter_vars.values(): v.set(False)

        tk.Button(btn_f, text="✅ All",  command=_select_all,
                  font=F["btn"], bg=C["c_add"], fg=C["text"],
                  relief="flat", cursor="hand2", pady=4, bd=0).pack(
            side="left", fill="x", expand=True, padx=(0, 2))
        tk.Button(btn_f, text="☐ None", command=_deselect_all,
                  font=F["btn"], bg=C["c_del"], fg=C["text"],
                  relief="flat", cursor="hand2", pady=4, bd=0).pack(
            side="right", fill="x", expand=True, padx=(2, 0))

        # ── Botón Plot — se empaqueta como "bottom" ANTES que el canvas ─────
        # En tkinter pack(), quien se empaqueta primero gana espacio.
        # Si el canvas (expand=True) se empaquetara primero, ocuparía todo y el botón
        # quedaría aplastado. Así el botón reserva su espacio en la parte inferior.
        tk.Button(panel['filter_pane'],
                  text="📊  Plot Selected",
                  command=self._apply_airline_filter,
                  font=F["btn"], bg=C["c_plot"], fg=C["text"],
                  relief="flat", cursor="hand2", pady=9, bd=0).pack(
            side="bottom", fill="x")

        # ── Lista scrollable — scrollbar en el borde derecho del panel ──────
        # SIN frame wrapper intermedio y SIN padx para que el scrollbar
        # quede pegado al borde derecho del filter_pane (215 px).
        sb = ttk.Scrollbar(panel['filter_pane'], orient="vertical")
        sb.pack(side="right", fill="y")

        cv     = tk.Canvas(panel['filter_pane'], bg=C["card"],
                           highlightthickness=0, yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.config(command=cv.yview)

        sf     = tk.Frame(cv, bg=C["card"])
        win_id = cv.create_window((0, 0), window=sf, anchor="nw")

        # Ajustar el ancho de sf al ancho real del canvas cuando se redimensione
        cv.bind("<Configure>", lambda e: cv.itemconfig(win_id, width=e.width))
        # Actualizar scrollregion cuando el contenido de sf cambie
        sf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))

        # Rueda del ratón para scroll (bind_all lo captura aunque el cursor
        # esté sobre un checkbox hijo, no solo sobre el canvas)
        def _mw(event): cv.yview_scroll(int(-1 * (event.delta / 120)), "units")
        cv.bind_all("<MouseWheel>", _mw)

        # "No encontrado" — oculto hasta que la búsqueda no dé resultados
        not_found_lbl = tk.Label(sf, text="No matching airlines found",
                                  font=F["small"], bg=C["card"], fg=C["textdim"])

        rows_dict = {}   # airline_code → row Frame (para show/hide en búsqueda)
        for airline in airlines:
            var = tk.BooleanVar(value=True)
            self._fl_filter_vars[airline] = var
            row = tk.Frame(sf, bg=C["card"])
            row.pack(fill="x", padx=2, pady=1)
            rows_dict[airline] = row
            tk.Checkbutton(row, text=f" {airline}",
                           variable=var,
                           font=("Consolas", 8), bg=C["card"], fg=C["text"],
                           selectcolor=C["border"], activebackground=C["card"],
                           cursor="hand2").pack(side="left")
            tk.Label(row,
                     text=str(counts.get(airline, 0)),
                     font=("Consolas", 8), bg=C["card"], fg=C["textdim"]).pack(
                side="right", padx=4)

        # Función de filtrado en tiempo real ← conectada al Entry de búsqueda
        def _do_search(*_):
            q = search_var.get().strip().upper()
            has = False
            for code, rf in rows_dict.items():
                if not q or q in code.upper():
                    rf.pack(fill="x", padx=2, pady=1)
                    has = True
                else:
                    rf.pack_forget()
            if has:
                not_found_lbl.pack_forget()
            else:
                not_found_lbl.pack(padx=8, pady=8)
            # Actualizar la scrollregion tras mostrar/ocultar filas
            sf.update_idletasks()
            cv.configure(scrollregion=cv.bbox("all"))

        # trace_add("write") es el API correcto en Tcl 9 / Python 3.14+
        search_var.trace_add("write", _do_search)

        # ── Mostrar la vista dividida ─────────────────────────────
        panel['table'].pack_forget()
        panel['plot_area'].pack_forget()
        panel['split_view'].pack(fill="both", expand=True)
        panel['back_btn'].pack(side="right", padx=8, pady=2)

        # Plot inicial con todas las aerolíneas seleccionadas
        self._apply_airline_filter()

    def _apply_airline_filter(self):
        """
        Lee los checkboxes, filtra self.aircrafts y embebe el gráfico
        en el panel derecho de la vista dividida.
        """
        if not hasattr(self, '_fl_filter_vars') or not self._fl_filter_vars:
            return
        selected = {a for a, v in self._fl_filter_vars.items() if v.get()}
        if not selected:
            self._log('_fl_log', ["No airlines selected — check at least one airline."], "warning")
            return

        panel    = self._panels['flights']
        filtered = [ac for ac in self.aircrafts if ac.Company in selected]
        if not filtered:
            return

        # Capturar figura (close all se hace dentro de _capture_plot) y aplicar estilo
        fig = self._capture_plot(PlotAirlines, filtered)
        self._style_figure(fig)
        fig.tight_layout()

        # Destruir canvas anterior antes de crear el nuevo
        if panel.get('canvas'):
            try:
                panel['canvas'].get_tk_widget().destroy()
            except Exception:
                pass
            panel['canvas'] = None

        # Embeber en el panel derecho de la split_view
        for w in panel['airline_plot'].winfo_children():
            w.destroy()
        canvas = FigureCanvasTkAgg(fig, master=panel['airline_plot'])
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        panel['canvas'] = canvas

        self._set_status(
            f"Airline chart: {len(selected)} airlines, {len(filtered)} flights", "info")
        self._log('_fl_log',
                  [f"Airline chart — {len(selected)} of {len(self._fl_filter_vars)} airlines selected",
                   f"  {len(filtered)} flights in chart"],
                  "info")

    def map_flights(self):
        """Mapa embebido con todas las trayectorias + genera KML sin abrir GE."""
        if not self.aircrafts:
            self._log('_fl_log', ["No flights loaded — use Load Arrivals first."], "warning"); return
        self._call_no_ge(MapFlights, self.aircrafts)
        self._kml_paths['flights'] = os.path.abspath("flights_map.kml")

        if HAS_WEB_MAP:
            html = self._create_flights_html(self.aircrafts)
            self._show_html(html, 'flights')
            self._set_status("Interactive flights map displayed  (folium)", "info")
        else:
            fig = self._capture_plot(self._create_map_matplotlib, airports=self.airports, flights=self.aircrafts)
            self._show_plot(fig, 'flights')
            self._set_status("Flights map displayed", "info")
        self._log('_fl_log',
                  [f"All trajectories — {len(self.aircrafts)} flights",
                   "  KML saved: flights_map.kml",
                   "  Press 🌍 to open in Google Earth"],
                  "info")

    def map_long_distance(self):
        """Mapa embebido con vuelos >2000 km + genera KML sin abrir GE."""
        if not self.aircrafts:
            self._log('_fl_log', ["No flights loaded — use Load Arrivals first."], "warning"); return
        long_fl = LongDistanceArrivals(self.aircrafts)
        if not long_fl:
            self._log('_fl_log', ["No long-distance flights found (> 2000 km)."], "warning")
            self._set_status("No long-distance flights found", "warning")
            return
        self._call_no_ge(MapFlights, long_fl)
        self._kml_paths['flights'] = os.path.abspath("long_distance_flights.kml")

        if HAS_WEB_MAP:
            html = self._create_flights_html(long_fl)
            self._show_html(html, 'flights')
            self._set_status(f"Map: {len(long_fl)} long-distance flights (> 2000 km)", "info")
        else:
            fig = self._capture_plot(self._create_map_matplotlib, airports=self.airports, flights=long_fl)
            self._show_plot(fig, 'flights')
            self._set_status(f"Long-distance map: {len(long_fl)} flights", "info")
        self._log('_fl_log',
                  [f"Long distance map — {len(long_fl)} flights (> 2000 km)",
                   "  KML saved: long_distance_flights.kml",
                   "  Press 🌍 to open in Google Earth"],
                  "info")

    # ══════════════════════════════════════════════════════════════
    # SISTEMA DE MAPAS EMBEBIDOS
    # ══════════════════════════════════════════════════════════════

    def _show_html(self, html_content: str, tab_key: str):
        """
        Muestra contenido HTML embebido en el panel derecho usando tkinterweb.HtmlFrame.
        Si tkinterweb no está instalado → abre en el navegador del sistema.
        """
        panel = self._panels[tab_key]

        if not HAS_WEB_MAP:
            # Fallback: guardar HTML en un fichero temporal y abrir en el navegador
            import tempfile, webbrowser
            with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                tmp_path = f.name
            webbrowser.open(f"file:///{tmp_path.replace(os.sep, '/')}")
            self._set_status("Map opened in browser — install tkinterweb to embed it", "info")
            return

        # Ocultar tabla y limpiar panel
        panel['table'].pack_forget()
        for w in panel['plot_area'].winfo_children():
            w.destroy()

        # Crear HtmlFrame y cargar el contenido
        hf = HtmlFrame(panel['plot_area'], messages_enabled=False)
        hf.load_html(html_content)
        hf.pack(fill="both", expand=True)

        panel['plot_area'].pack(fill="both", expand=True)
        panel['back_btn'].pack(side="right", padx=8, pady=2)

    def _create_airports_html(self) -> str:
        """
        Crea un mapa interactivo Leaflet (via folium) con todos los aeropuertos.
        Tema oscuro CartoDB Dark Matter para combinar con la interfaz.
        Azul claro = Schengen, cyan = no Schengen.
        """
        m = folium.Map(location=[41.3, 2.1], zoom_start=4,
                       tiles="CartoDB dark_matter")

        for ap in self.airports:
            color = "#60a5fa" if ap.Schengen else "#7dd3fc"
            folium.CircleMarker(
                location=[ap.latitude, ap.longitude],
                radius=5, color=color,
                fill=True, fill_color=color, fill_opacity=0.8,
                popup=folium.Popup(
                    f"<b style='color:#60a5fa'>{ap.ICAO}</b><br>"
                    f"{'🇪🇺 Schengen' if ap.Schengen else '🌍 Non-Schengen'}<br>"
                    f"Lat: {ap.latitude:.4f}° / Lon: {ap.longitude:.4f}°",
                    max_width=220)
            ).add_to(m)

        # Marcador especial para LEBL
        folium.Marker(
            [41.2974, 2.0783],
            popup=folium.Popup("<b style='color:#f87171'>LEBL — Barcelona El Prat</b>", max_width=200),
            icon=folium.Icon(color="red", icon="plane", prefix="fa")
        ).add_to(m)

        return m._repr_html_()

    def _create_flights_html(self, flights: list) -> str:
        """
        Crea un mapa interactivo Leaflet con las trayectorias de vuelo.
        Líneas azules = Schengen, cyan = no Schengen.
        """
        m = folium.Map(location=[41.3, 2.1], zoom_start=3,
                       tiles="CartoDB dark_matter")
        lebl = [41.2974, 2.0783]

        for ac in flights:
            if ac.origin is None:
                continue
            color = "#60a5fa" if ac.origin.Schengen else "#7dd3fc"
            # Línea de trayectoria
            folium.PolyLine(
                [[ac.origin.latitude, ac.origin.longitude], lebl],
                color=color, weight=1.4, opacity=0.55
            ).add_to(m)
            # Marcador origen
            folium.CircleMarker(
                [ac.origin.latitude, ac.origin.longitude],
                radius=4, color=color,
                fill=True, fill_color=color, fill_opacity=0.75,
                popup=folium.Popup(
                    f"<b style='color:#60a5fa'>{ac.origin.ICAO}</b> → LEBL<br>"
                    f"Flight: {ac.Id}  |  {ac.Company or '—'}<br>"
                    f"Arrival: {ac.time or '—'}",
                    max_width=200)
            ).add_to(m)

        # LEBL
        folium.Marker(
            lebl,
            popup=folium.Popup("<b style='color:#f87171'>LEBL — Barcelona El Prat</b>", max_width=200),
            icon=folium.Icon(color="red", icon="plane", prefix="fa")
        ).add_to(m)

        return m._repr_html_()

    def _create_map_matplotlib(self, airports=None, flights=None):
        import contextily as ctx
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D

        fig, ax = plt.subplots(figsize=(13, 7))
        fig.patch.set_facecolor(C["panel"])

        lebl_lat, lebl_lon = 41.2974, 2.0783

        # Convertir coordenadas a Web Mercator (EPSG:3857) que usa contextily
        import math
        def to_mercator(lon, lat):
            x = lon * 20037508.34 / 180
            y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
            y = y * 20037508.34 / 180
            return x, y

        lebl_x, lebl_y = to_mercator(lebl_lon, lebl_lat)

        # Líneas de trayectoria
        if flights:
            for ac in flights:
                if ac.origin:
                    ox, oy = to_mercator(ac.origin.longitude, ac.origin.latitude)
                    color = "#3b82f6" if ac.origin.Schengen else "#22d3ee"
                    ax.plot([ox, lebl_x], [oy, lebl_y],
                            color=color, alpha=0.4, linewidth=0.8, zorder=2)

        # Puntos de aeropuertos
        if airports:
            for ap in airports:
                ax_x, ax_y = to_mercator(ap.longitude, ap.latitude)
                color = "#60a5fa" if ap.Schengen else "#22d3ee"
                ax.scatter(ax_x, ax_y, c=color, s=18, alpha=0.8, zorder=3, edgecolors="none")

        # LEBL
        ax.scatter([lebl_x], [lebl_y], c="#f87171", s=180,
                   marker="*", zorder=5, label="LEBL")
        ax.annotate("  LEBL", (lebl_x, lebl_y),
                    color="#f0f9ff", fontsize=9, fontweight="bold", va="center", zorder=6)

        # Calcular límites del mapa
        if airports:
            xs = [to_mercator(a.longitude, a.latitude)[0] for a in airports]
            ys = [to_mercator(a.longitude, a.latitude)[1] for a in airports]
            pad_x = (max(xs) - min(xs)) * 0.08
            pad_y = (max(ys) - min(ys)) * 0.08
            ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
            ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
        else:
            ax.set_xlim(to_mercator(-30, 20)[0], to_mercator(60, 70)[0])
            ax.set_ylim(to_mercator(-30, 20)[1], to_mercator(60, 70)[1])

        # Añadir mapa de fondo real
        try:
            ctx.add_basemap(ax, crs="EPSG:3857",
                            source=ctx.providers.CartoDB.DarkMatter,
                            zoom="auto")
        except Exception:
            ax.set_facecolor("#061525")

        ax.set_axis_off()

        # Leyenda
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#60a5fa',
                   markersize=8, label='Schengen'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#22d3ee',
                   markersize=8, label='Non-Schengen'),
            Line2D([0], [0], marker='*', color='w', markerfacecolor='#f87171',
                   markersize=12, label='LEBL'),
        ]
        ax.legend(handles=legend_elements, loc="upper left", fontsize=9,
                  facecolor=C["card"], edgecolor=C["border"], labelcolor=C["text"])

        plt.tight_layout()
        return fig

    def _refresh_flights_tree(self):
        """Reconstruye la tabla de vuelos con los datos actuales."""
        for item in self.fl_tree.get_children(): self.fl_tree.delete(item)
        lat_lebl, lon_lebl = 41.29694, 2.07833
        for ac in self.aircrafts:
            origin_icao = ac.origin.ICAO if ac.origin else "—"
            is_sch      = ac.origin is not None and ac.origin.Schengen
            dist_str    = "—"
            tag         = "schengen" if is_sch else "non_schengen"
            if ac.origin:
                try:
                    phi1 = math.radians(ac.origin.latitude)
                    phi2 = math.radians(lat_lebl)
                    dphi = math.radians(lat_lebl - ac.origin.latitude)
                    dlam = math.radians(lon_lebl - ac.origin.longitude)
                    a    = (math.sin(dphi/2)**2 +
                            math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2)
                    dist = 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    dist_str = f"{dist:,.0f} km"
                    if dist > 2000: tag = "long_dist"
                except Exception:
                    pass
            self.fl_tree.insert("", "end", values=(
                ac.Id, origin_icao, ac.time or "—", ac.Company or "—",
                "✅ Yes" if is_sch else "❌ No", dist_str), tags=(tag,))
        n   = len(self.aircrafts)
        sch = sum(1 for ac in self.aircrafts if ac.origin and ac.origin.Schengen)
        self.fl_count_lbl.config(
            text=f"{n} flights  |  ✅ {sch} Schengen  |  ❌ {n-sch} non-Schengen")
        self.count_var.set(f"Flights loaded: {n}")

    # ══════════════════════════════════════════════════════════════
    # TAB 3 — GATE MANAGEMENT (V3 + V4)
    # ══════════════════════════════════════════════════════════════

    def _build_tab_gates(self):
        tab = self.tab_gates

        # ── Panel izquierdo ──────────────────────────────────────
        left = tk.Frame(tab, bg=C["panel"], width=270)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🏢  Gate Management",
                 font=F["h2"], bg=C["panel"], fg=C["text"]).pack(
            pady=(18, 8), padx=16, anchor="w")

        s3 = self._make_section(left, "🏗️  V3 — Airport Structure")
        s3.pack(fill="x", padx=12, pady=5)
        tk.Label(s3, text="  ⏰ Hour selector (right bar) applies here",
                 font=("Segoe UI", 7), bg=C["panel"], fg=C["textdim"]).pack(
            anchor="w", padx=8, pady=(4, 0))
        self._make_btn(s3, "🏗️  Load Airport Structure",  self.load_airport_structure,     C["c_load"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s3, "🚪  Assign Gates to Arrivals", self.assign_gates,               C["c_add"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s3, "🗺️  Gate Map (Visual Plot)",   self.plot_gate_occupancy_visual, C["c_plot"]).pack(pady=(0,6), padx=8, fill="x")

        s4 = self._make_section(left, "🔄  V4 — Dynamic Simulation")
        s4.pack(fill="x", padx=12, pady=5)
        self._make_btn(s4, "📂  Load Departures",           self.load_departures,    C["c_load"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s4, "🔀  Merge Arrivals+Departures", self.merge_movements,    C["c_v4"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s4, "🌙  Assign Night Aircraft",     self.assign_night_gates, C["c_main"]).pack(pady=4,    padx=8, fill="x")
        self._make_btn(s4, "📊  Plot Full Day Occupancy",   self.plot_day_occupancy, C["c_plot"]).pack(pady=(0,6), padx=8, fill="x")

        # ── Operation Log — rellena el espacio restante del panel izquierdo
        self._make_log_panel(left, '_gate_log')

        # ── Panel derecho — construcción manual ──────────────────
        # (no usamos _make_right_panel porque necesitamos la info_bar extra)
        right = tk.Frame(tab, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True, padx=14, pady=14)

        # Barra de info del aeropuerto cargado
        info_bar = tk.Frame(right, bg=C["panel"], height=52)
        info_bar.pack(fill="x", pady=(0, 10))
        info_bar.pack_propagate(False)
        tk.Label(info_bar, text="Airport Structure:", font=F["h3"],
                 bg=C["panel"], fg=C["textdim"]).pack(side="left", padx=14)
        self.gate_info_var = tk.StringVar(value="Not loaded — use 'Load Airport Structure' first")
        tk.Label(info_bar, textvariable=self.gate_info_var, font=F["mono"],
                 bg=C["panel"], fg=C["text"]).pack(side="left", padx=8)

        # Barra de cabecera de tabla
        top = tk.Frame(right, bg=C["bg"])
        top.pack(fill="x", pady=(0, 8))
        tk.Label(top, text="Gate Occupancy", font=F["h2"],
                 bg=C["bg"], fg=C["text"]).pack(side="left")

        # Botón "volver" — no empaquetado ahora
        back_btn = self._make_btn(top, "◀  Back to Table",
                                  lambda: self._back_to_table('gates'), C["c_v4"])

        self.gate_count_lbl = tk.Label(top, text="", font=F["small"],
                                        bg=C["bg"], fg=C["textdim"])
        self.gate_count_lbl.pack(side="right")

        # ── Selector de terminal + control de hora ───────────────
        # Barra horizontal bajo la cabecera, con:
        #   izquierda:  botones de terminal (T1 / T2 ...)
        #   derecha:    Spinbox de hora + botón "▶ Apply Hour"
        self._term_sel_frame = tk.Frame(right, bg=C["card"], height=46)
        self._term_sel_frame.pack(fill="x", pady=(0, 8))
        self._term_sel_frame.pack_propagate(False)
        self._selected_terminal = tk.StringVar(value="")
        self._term_buttons      = {}
        tk.Label(self._term_sel_frame,
                 text="  Load airport structure first to enable terminal selection",
                 font=F["small"], bg=C["card"], fg=C["textdim"]).pack(
            side="left", padx=12, pady=13)

        # Separador vertical (aparece solo cuando se carga la estructura)
        self._term_sep = tk.Frame(self._term_sel_frame, bg=C["border"], width=1)

        # Controles de hora (lado derecho de la barra) — siempre visibles
        hour_ctrl = tk.Frame(self._term_sel_frame, bg=C["card"])
        hour_ctrl.pack(side="right", padx=10)
        tk.Label(hour_ctrl, text="⏰  Hour:",
                 font=F["small"], bg=C["card"], fg=C["textdim"]).pack(side="left", padx=(0, 4))
        tk.Spinbox(hour_ctrl,
                   values=[f"{h:02d}" for h in range(24)],
                   textvariable=self.hour_var,
                   width=4, font=F["mono"],
                   bg=C["entry"], fg=C["text"],
                   buttonbackground=C["card"],
                   relief="flat", bd=3).pack(side="left")
        tk.Button(hour_ctrl,
                  text="▶ Apply",
                  command=self._apply_hour_snapshot,
                  font=F["btn"],
                  bg=C["c_add"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  padx=8, pady=3, bd=0).pack(side="left", padx=(6, 0))

        # Contenedor de contenido
        content = tk.Frame(right, bg=C["bg"])
        content.pack(fill="both", expand=True)

        # Tabla de puertas
        cols   = ["Gate", "Terminal", "Area", "Type", "Status", "Aircraft"]
        widths = [130, 90, 70, 120, 110, 130]
        table_f, self.gate_tree = self._make_treeview(content, cols, widths)
        self.gate_tree.tag_configure("occupied", foreground="#60a5fa")  # Azul brillante
        self.gate_tree.tag_configure("free",     foreground="#7ec8e3")  # Cyan claro
        table_f.pack(fill="both", expand=True)

        # Área de gráfico (oculta inicialmente)
        plot_area = tk.Frame(content, bg=C["panel"])

        # Registrar referencias
        self._panels['gates'] = {
            'table':     table_f,
            'plot_area': plot_area,
            'back_btn':  back_btn,
            'canvas':    None,
        }

    # ── Métodos V3 ──────────────────────────────────────────────

    def load_airport_structure(self):
        fn = filedialog.askopenfilename(
            title="Select Airport Structure File (e.g. Terminals.txt)",
            filetypes=[("Text files", "*.txt"), ("All", "*.*")])
        if not fn: return
        result = LoadAirportStructure(fn)
        if result == -1:
            self._log('_gate_log', ["Error: could not load the airport structure file."], "error")
            self._set_status("Error loading airport structure", "error")
            return
        self.bcn                = result
        self.structure_filename = fn
        total_gates    = sum(len(area.Gates) for t in self.bcn.Terminals for area in t.BoardingAreas)
        total_airlines = sum(len(t.Airlines) for t in self.bcn.Terminals)
        self.gate_info_var.set(
            f"{self.bcn.Code}  |  {len(self.bcn.Terminals)} terminals  |  "
            f"{total_gates} gates  |  {total_airlines} airlines registered")
        self._populate_terminal_selector()   # Rellena los botones T1 / T2 ...
        self._refresh_gate_tree()
        self._set_status(
            f"Loaded: {self.bcn.Code} — {len(self.bcn.Terminals)} terminals, {total_gates} gates", "success")

    def _populate_terminal_selector(self):
        """
        Rellena la barra de selección de terminal con un botón por cada terminal.
        Solo limpia los widgets de terminal (lado izquierdo), deja intactos los controles de hora.
        El primer terminal queda seleccionado por defecto.
        """
        # Eliminar solo etiqueta de "load first" y botones de terminal anteriores
        # (los controles de hora están en hour_ctrl y se preservan)
        for w in list(self._term_sel_frame.winfo_children()):
            # Conservar el Frame hour_ctrl y el separador — son los últimos empaquetados "side=right"
            info = w.pack_info() if w.winfo_manager() == "pack" else {}
            if info.get("side") in ("right",):
                continue
            w.destroy()

        self._term_buttons = {}

        tk.Label(self._term_sel_frame, text="  Terminal:",
                 font=F["h3"], bg=C["card"], fg=C["textdim"]).pack(
            side="left", padx=(10, 6), pady=10)

        first = True
        for terminal in self.bcn.Terminals:
            name = terminal.Name
            btn  = tk.Button(self._term_sel_frame,
                             text=f"  {name}  ",
                             command=lambda n=name: self._select_terminal(n),
                             font=F["btn"],
                             bg=C["c_main"] if first else C["card"],
                             fg=C["text"],
                             relief="flat", cursor="hand2",
                             pady=4, bd=0)
            btn.pack(side="left", padx=3)
            self._term_buttons[name] = btn
            if first:
                self._selected_terminal.set(name)
                first = False

    def _select_terminal(self, name: str):
        """
        Cambia el terminal seleccionado y redibuja el gate map si está visible.
        Actualiza el resaltado de los botones del selector.
        """
        for n, btn in self._term_buttons.items():
            btn.config(bg=C["c_main"] if n == name else C["card"])
        self._selected_terminal.set(name)

        # Si el gate map está activo, redibujarlo para el nuevo terminal
        panel = self._panels.get('gates', {})
        if panel.get('plot_area') and panel['plot_area'].winfo_ismapped():
            self.plot_gate_occupancy_visual()

    def _apply_hour_snapshot(self):
        """
        Nuevo método unificado: procesa la hora seleccionada en la barra superior
        Y muestra inmediatamente el gate map con el estado resultante.
        Reemplaza la combinación de assign_gates_at_time + plot_day_occupancy.
        Escribe el resultado en el panel de log (izquierda inferior) sin popup.
        """
        if self.bcn is None:
            self._log_gate(["Load the airport structure first."], "warning")
            self._set_status("Load airport structure first", "warning")
            return
        source = self.merged if self.merged else self.aircrafts
        if not source:
            self._log_gate(["Load and merge movements first."], "warning")
            self._set_status("Load/merge movements first", "warning")
            return
        if not self.structure_filename:
            self._log_gate(["Cannot reload airport structure — use Load Airport Structure first."], "warning")
            return

        try:
            hour_int = int(self.hour_var.get().strip())
            if not (0 <= hour_int <= 23):
                raise ValueError
        except ValueError:
            self._log_gate(["Invalid hour — choose 00–23."], "error")
            return

        # ── Copia fresca: simular desde 00:00 hasta la hora elegida ──
        bcn_snap = LoadAirportStructure(self.structure_filename)
        if bcn_snap == -1:
            self._log_gate(["Could not reload airport structure file."], "error")
            return

        night = NightAircraft(source)
        if night and night != -1:
            AssignNightGates(bcn_snap, source)

        for h in range(hour_int + 1):
            AssignGatesAtTime(bcn_snap, source, f"{h:02d}:00")

        # Estadísticas de la hora procesada (solo la última)
        dep_this_hour = sum(
            1 for ac in source
            if ac.DepartureTime and int(ac.DepartureTime.split(":")[0]) == hour_int)
        arr_this_hour = sum(
            1 for ac in source
            if ac.time and int(ac.time.split(":")[0]) == hour_int)
        gates_all = sum(len(a.Gates) for t in bcn_snap.Terminals for a in t.BoardingAreas)
        gates_occ = sum(
            1 for t in bcn_snap.Terminals
            for a in t.BoardingAreas
            for g in a.Gates if g.Occupied)

        time_str = f"{hour_int:02d}:00"
        self._log_gate([
            f"Snapshot at {time_str}",
            f"Departures freed:  {dep_this_hour}",
            f"Arrivals assigned: {arr_this_hour}",
            f"Gates occupied:    {gates_occ} / {gates_all}",
            f"Gates free:        {gates_all - gates_occ} / {gates_all}",
        ], "success")
        self._set_status(
            f"Hour {time_str} snapshot — {gates_occ} occupied / {gates_all - gates_occ} free", "success")

        # ── Dibujar el gate map con el estado simulado ────────────
        sel_name = self._selected_terminal.get()
        terminal = next((t for t in bcn_snap.Terminals if t.Name == sel_name),
                        bcn_snap.Terminals[0] if bcn_snap.Terminals else None)
        if not terminal:
            return

        self._draw_gate_map(bcn_snap, terminal,
                            title_extra=f"  ·  {time_str} snapshot")

    def assign_gates(self):
        """
        Asigna puertas a las llegadas hora por hora (simulación simplificada V4).
        Solo necesita la lista de llegadas (no hace falta cargar salidas).
        Usa una copia fresca de la estructura para no contaminar el estado de self.bcn.
        El resultado se muestra en el Gate Map con el selector de hora.
        """
        if self.bcn is None:
            self._log_gate(["Load the airport structure first."], "warning")
            self._set_status("Load airport structure first", "warning")
            return
        if not self.aircrafts:
            self._log_gate(["Load arrivals first (Flights tab)."], "warning")
            self._set_status("Load arrivals first", "warning")
            return
        if not self.structure_filename:
            self._log_gate(["Cannot reload airport structure — use Load Airport Structure first."], "warning")
            return

        try:
            hour_int = int(self.hour_var.get().strip())
            if not (0 <= hour_int <= 23):
                raise ValueError
        except ValueError:
            self._log_gate(["Invalid hour — choose 00–23."], "error")
            return

        # Copia fresca de la estructura para simular desde 00:00 hasta la hora elegida
        bcn_snap = LoadAirportStructure(self.structure_filename)
        if bcn_snap == -1:
            self._log_gate(["Could not reload airport structure file."], "error")
            return

        # Simular hora a hora solo con llegadas (sin salidas)
        for h in range(hour_int + 1):
            time_str_h = f"{h:02d}:00"
            for ac in self.aircrafts:
                if ac.time is not None:
                    try:
                        arr_hour = int(ac.time.split(":")[0])
                        if arr_hour == h:
                            AssignGate(bcn_snap, ac)
                    except (ValueError, AttributeError):
                        continue

        # Estadísticas del estado resultante
        arr_this_hour = sum(
            1 for ac in self.aircrafts
            if ac.time and int(ac.time.split(":")[0]) == hour_int)
        gates_all = sum(len(a.Gates) for t in bcn_snap.Terminals for a in t.BoardingAreas)
        gates_occ = sum(
            1 for t in bcn_snap.Terminals
            for a in t.BoardingAreas
            for g in a.Gates if g.Occupied)

        time_str = f"{hour_int:02d}:00"
        self._log_gate([
            f"Arrivals assigned up to {time_str}",
            f"Arrivals in this hour:  {arr_this_hour}",
            f"Gates occupied:         {gates_occ} / {gates_all}",
            f"Gates free:             {gates_all - gates_occ} / {gates_all}",
        ], "success")
        self._set_status(
            f"Arrivals up to {time_str} — {gates_occ} occupied / {gates_all - gates_occ} free", "success")

        # Dibujar el gate map con el estado resultante
        sel_name = self._selected_terminal.get()
        terminal = next((t for t in bcn_snap.Terminals if t.Name == sel_name),
                        bcn_snap.Terminals[0] if bcn_snap.Terminals else None)
        if terminal:
            self._draw_gate_map(bcn_snap, terminal,
                                title_extra=f"  ·  arrivals up to {time_str}")

    def plot_gate_occupancy_visual(self):
        """
        Muestra el gate map del terminal seleccionado simulado hasta la hora elegida.
        Si hay movements (merged) o arrivals cargados, simula el estado a esa hora.
        Si no hay datos de vuelos, muestra el estado actual de self.bcn sin simulación.
        """
        if self.bcn is None:
            self._log_gate(["Load the airport structure first."], "warning")
            self._set_status("Load airport structure first", "warning")
            return

        sel_name = self._selected_terminal.get()

        # Si hay datos de vuelos, simular hasta la hora seleccionada
        source = self.merged if self.merged else self.aircrafts
        if source and self.structure_filename:
            try:
                hour_int = int(self.hour_var.get().strip())
                if not (0 <= hour_int <= 23):
                    raise ValueError
            except ValueError:
                self._log_gate(["Invalid hour — choose 00–23."], "error")
                return

            bcn_snap = LoadAirportStructure(self.structure_filename)
            if bcn_snap == -1:
                self._log_gate(["Could not reload airport structure file."], "error")
                return

            # Asignar nocturnos si hay lista fusionada
            if self.merged:
                night = NightAircraft(self.merged)
                if night and night != -1:
                    AssignNightGates(bcn_snap, self.merged)

            for h in range(hour_int + 1):
                AssignGatesAtTime(bcn_snap, source, f"{h:02d}:00")

            time_str = f"{hour_int:02d}:00"
            terminal = next((t for t in bcn_snap.Terminals if t.Name == sel_name),
                            bcn_snap.Terminals[0] if bcn_snap.Terminals else None)
            if terminal:
                self._draw_gate_map(bcn_snap, terminal,
                                    title_extra=f"  ·  snapshot at {time_str}")
        else:
            # Sin datos de vuelo: mostrar estado actual de self.bcn
            terminal = next((t for t in self.bcn.Terminals if t.Name == sel_name),
                            self.bcn.Terminals[0] if self.bcn.Terminals else None)
            if terminal:
                self._draw_gate_map(self.bcn, terminal)

    def _draw_gate_map(self, bcn_obj, terminal, title_extra: str = ""):
        """
        Núcleo de renderizado del gate map.
        Dibuja el plano de puertas de UN terminal y lo embebe en el panel derecho.
        bcn_obj   → objeto BarcelonaAP (puede ser self.bcn o una copia simulada)
        terminal  → objeto Terminal a dibujar
        title_extra → cadena opcional añadida al título (ej. '· 07:00 snapshot')
        """
        # ── Geometría adaptativa ─────────────────────────────────
        n_areas   = len(terminal.BoardingAreas)
        max_gates = max((len(a.Gates) for a in terminal.BoardingAreas), default=1)

        if max_gates <= 20:
            GS, GH, GL, FONT_LBL, FONT_AREA = 1.80, 0.65, 1.50, 9, 10
        elif max_gates <= 40:
            GS, GH, GL, FONT_LBL, FONT_AREA = 1.10, 0.45, 1.10, 7, 8
        else:
            GS, GH, GL, FONT_LBL, FONT_AREA = 0.72, 0.30, 0.75, 6, 7

        FW, GO, FS, MX, CH, TOP_M, FINGER_EXTRA = 0.65, 0.90, 6.20, 3.50, 0.65, 0.80, 1.20

        FREE_FC, FREE_EC, FREE_LC = "#14532d", "#22c55e", "#86efac"
        OCC_FC,  OCC_EC,  OCC_LC  = "#7f1d1d", "#ef4444", "#fca5a5"

        data_h = TOP_M + CH + GO + (max_gates - 1) * GS + GH/2 + FINGER_EXTRA + 0.30 + 1.20
        data_w = MX + (n_areas - 1) * FS + MX
        fig_h  = max(8, max_gates * 0.32)
        fig_w  = max(12, fig_h * (data_w / data_h) * 1.1)

        plt.close('all')
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        fig.patch.set_facecolor(C["panel"])
        ax.set_facecolor(C["card"])

        x_centers = [MX + i * FS for i in range(n_areas)]
        corr_bot  = data_h - TOP_M - CH

        # Corredor principal
        ax.add_patch(plt.Rectangle(
            (x_centers[0] - FW/2 - 1.2, corr_bot),
            (x_centers[-1] - x_centers[0]) + FW + 2.4, CH,
            facecolor="#1d6eb0", edgecolor="#7ec8e3", linewidth=2.2, zorder=3))

        ax.text(x_centers[0] - FW/2 - 1.2, corr_bot + CH + 0.15,
                f"T{terminal.Name[-1] if len(terminal.Name) > 1 else terminal.Name}",
                ha="left", va="bottom", fontsize=20, fontweight="bold",
                color=C["text"], zorder=5)

        occ_total, free_total = 0, 0

        for x_c, area in zip(x_centers, terminal.BoardingAreas):
            n_gates    = len(area.Gates)
            last_y     = corr_bot - GO - (n_gates - 1) * GS
            finger_bot = last_y - GH/2 - FINGER_EXTRA
            finger_h   = corr_bot - finger_bot

            ax.add_patch(plt.Rectangle(
                (x_c - FW/2, finger_bot), FW, finger_h,
                facecolor="#1d6eb0", edgecolor="#7ec8e3", linewidth=1.4, zorder=2))

            for j, gate in enumerate(area.Gates):
                g_y = corr_bot - GO - j * GS
                if j % 2 == 0:
                    g_x, lx, lha = x_c + FW/2, x_c + FW/2 + GL + 0.10, "left"
                else:
                    g_x = x_c - FW/2 - GL
                    lx, lha = g_x - 0.10, "right"

                if gate.Occupied:
                    fc, ec, lc = OCC_FC, OCC_EC, OCC_LC
                    label = gate.AircraftID[:7] if gate.AircraftID else "OCC"
                    occ_total += 1
                else:
                    fc, ec, lc = FREE_FC, FREE_EC, FREE_LC
                    gate_num = gate.Name.split("G")[-1] if "G" in gate.Name else gate.Name
                    label    = f"{terminal.Name}BA{area.Name}G{gate_num}"
                    free_total += 1

                ax.add_patch(plt.Rectangle(
                    (g_x, g_y - GH/2), GL, GH,
                    facecolor=fc, edgecolor=ec, linewidth=1.0, zorder=4))
                ax.text(lx, g_y, label, ha=lha, va="center",
                        fontsize=FONT_LBL, color=lc,
                        fontweight="bold" if gate.Occupied else "normal", zorder=5)

            ac_col = "#60a5fa" if area.Type == "Schengen" else "#7dd3fc"
            ax.text(x_c, finger_bot - 0.18, f"{terminal.Name}BA{area.Name}",
                    ha="center", va="top", fontsize=FONT_AREA,
                    color=ac_col, fontweight="bold", zorder=5)

        total_t = occ_total + free_total
        pct = (occ_total / total_t * 100) if total_t else 0
        ax.text(data_w / 2, corr_bot + CH + 0.10,
                f"● {occ_total} occupied ({pct:.0f}%)   ○ {free_total} free   ({total_t} total)",
                ha="center", va="bottom", fontsize=9.5, color=C["textdim"])

        ax.legend(handles=[
            mpatches.Patch(facecolor=FREE_FC, edgecolor=FREE_EC, label="Free gate"),
            mpatches.Patch(facecolor=OCC_FC,  edgecolor=OCC_EC,  label="Occupied gate"),
        ], loc="upper right", fontsize=9,
           facecolor=C["card"], edgecolor=C["border"], labelcolor=C["text"])

        ax.set_xlim(0, data_w)
        ax.set_ylim(0, data_h)
        ax.axis("off")
        fig.suptitle(f"Gate Map — {bcn_obj.Code}  /  Terminal {terminal.Name}{title_extra}",
                     fontsize=13, fontweight="bold", color=C["text"], y=0.99)
        plt.tight_layout(rect=[0, 0, 1, 0.97])

        # Embeber
        panel = self._panels['gates']
        panel['table'].pack_forget()
        if panel.get('canvas'):
            try:
                panel['canvas'].get_tk_widget().destroy()
            except Exception:
                pass
            panel['canvas'] = None
        for w in panel['plot_area'].winfo_children():
            w.destroy()
        canvas = FigureCanvasTkAgg(fig, master=panel['plot_area'])
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        panel['canvas'] = canvas
        panel['plot_area'].pack(fill="both", expand=True)
        panel['back_btn'].pack(side="right", padx=8, pady=2)
        self._set_status(
            f"Gate map: {terminal.Name}  |  {occ_total} occupied / {free_total} free", "info")

    # ── Métodos V4 ──────────────────────────────────────────────

    def load_departures(self):
        fn = filedialog.askopenfilename(title="Select Departures File",
                                        filetypes=[("Text files", "*.txt"), ("All", "*.*")])
        if not fn: return
        data = LoadDepartures(fn)
        self.departures = data if data else []
        n = len(self.departures)
        self._set_status(f"Loaded {n} departure{'s' if n!=1 else ''} from {os.path.basename(fn)}", "success")

    def merge_movements(self):
        if not self.aircrafts:
            self._log_gate(["Load arrivals first (Flights tab)."], "warning")
            self._set_status("Load arrivals first", "warning")
            return
        if not self.departures:
            self._log_gate(["Load departures first (Load Departures button)."], "warning")
            self._set_status("Load departures first", "warning")
            return
        result = MergeMovements(self.aircrafts, self.departures)
        if result == -1:
            self._log_gate(["Merge failed — one or both lists are empty."], "error")
            self._set_status("Error merging movements", "error")
            return
        self.merged  = result
        complete     = sum(1 for ac in self.merged if ac.time is not None and ac.DepartureTime is not None)
        only_arr     = sum(1 for ac in self.merged if ac.time is not None and ac.DepartureTime is None)
        night        = sum(1 for ac in self.merged if ac.time is None and ac.DepartureTime is not None)
        self._log_gate([
            f"Merge Complete — {len(self.merged)} movements",
            f"Arrival + Departure: {complete}",
            f"Arrival only:        {only_arr}",
            f"Night aircraft:      {night}",
        ], "success")
        self._set_status(
            f"Merged {len(self.merged)} movements — {complete} complete, {only_arr} arr-only, {night} night",
            "success")

    def assign_night_gates(self):
        if self.bcn is None:
            self._log_gate(["Load the airport structure first."], "warning")
            self._set_status("Load airport structure first", "warning")
            return
        source = self.merged if self.merged else self.departures
        if not source:
            self._log_gate(["Load and merge movements first."], "warning")
            self._set_status("Load/merge movements first", "warning")
            return
        night = NightAircraft(source)
        if night == -1 or not night:
            self._log_gate(["No night aircraft found in current movements."], "info")
            self._set_status("No night aircraft found", "warning")
            return
        AssignNightGates(self.bcn, night)
        self._refresh_gate_tree()
        self._log_gate([
            "Night Gates Assigned",
            f"{len(night)} aircraft assigned to gates",
            "Start-of-day initial state ready.",
        ], "success")
        self._set_status(f"Night gates assigned for {len(night)} aircraft", "success")

    def assign_gates_at_time(self):
        """Procesa una hora concreta sobre self.bcn (modifica el estado en vivo)."""
        if self.bcn is None:
            self._log_gate(["Load the airport structure first."], "warning")
            self._set_status("Load airport structure first", "warning")
            return
        source = self.merged if self.merged else self.aircrafts
        if not source:
            self._log_gate(["Load/merge movements first."], "warning")
            self._set_status("Load/merge movements first", "warning")
            return
        try:
            hour_int = int(self.hour_var.get().strip())
            if not (0 <= hour_int <= 23): raise ValueError
        except ValueError:
            self._log_gate(["Invalid hour — choose 00–23."], "error")
            return
        time_str   = f"{hour_int:02d}:00"
        unassigned = AssignGatesAtTime(self.bcn, source, time_str)
        self._refresh_gate_tree()
        level = "success" if unassigned == 0 else "warning"
        self._log_gate([
            f"Hour {time_str} processed",
            f"Gates freed for departures",
            f"New arrivals assigned",
            f"Unassigned (no free gates): {unassigned}",
        ], level)
        self._set_status(
            f"Hour {time_str} processed — {unassigned} aircraft could not be assigned", level)


    def plot_day_occupancy(self):
        """
        Muestra el Gate Map con el estado al final de la hora seleccionada.
        Ahora delega en _apply_hour_snapshot para unificar la lógica.
        """
        self._apply_hour_snapshot()



    def _refresh_gate_tree(self):
        """Reconstruye la tabla de puertas con el estado actual de self.bcn."""
        if self.bcn is None: return
        for item in self.gate_tree.get_children(): self.gate_tree.delete(item)
        occupied_n, free_n = 0, 0
        for terminal in self.bcn.Terminals:
            for area in terminal.BoardingAreas:
                for gate in area.Gates:
                    if gate.Occupied:
                        self.gate_tree.insert("", "end",
                                              values=(gate.Name, terminal.Name, area.Name,
                                                      area.Type, "● Occupied", gate.AircraftID),
                                              tags=("occupied",))
                        occupied_n += 1
                    else:
                        self.gate_tree.insert("", "end",
                                              values=(gate.Name, terminal.Name, area.Name,
                                                      area.Type, "○ Free", ""),
                                              tags=("free",))
                        free_n += 1
        total = occupied_n + free_n
        self.gate_count_lbl.config(
            text=f"{total} gates  |  ● {occupied_n} occupied  |  ○ {free_n} free")
        self.count_var.set(f"Gates: {occupied_n} occupied / {free_n} free")


# ═══════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════

def main():
    root = tk.Tk()
    app  = AirportApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
