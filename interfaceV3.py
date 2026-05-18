import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sys
import warnings

# Bloquegem els avisos de Matplotlib abans d'importar
warnings.filterwarnings("ignore", category=UserWarning)

import matplotlib

matplotlib.use('Agg')  # Importació pel Matplotlib, per tal de bloquejar el avisos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from airport import *
from aircrafts import *
from LEBL import *

# --- LOGICA V3 (Base de dades de validació) ---
DEPARTURES = {
    "ECLZN": "LGMK", "ECLQK": "LLBG", "ECHFK": "LEPA", "ECMHS": "LPPT",
    "ECMFN": "LEBB", "N327UP": "LEVC", "TCJSO": "LTBA", "EIDAM": "LIME",
    "EIDWK": "EBBR", "EIDCJ": "EGSS", "LYVEO": "LEST", "EIDHT": "EYVI",
    "GEZUM": "LSGG", "ECMLE": "LFRS", "EIDTO": "LIRF", "EIEFW": "LEST",
    "ECMBY": "LDZA", "ECLRG": "EDDP", "EIDAE": "LIRF", "EIFIY": "LEIB",
    "VLG1234": "TEST", "IBE330": "TEST"
}

ARRIVALS = {
    "ECMKV": "LYBE", "ECJGM": "EGCC", "ECLOB": "LMML", "ECLVC": "LGTS",
    "DALEC": "EBBR", "ECMKN": "LGSR", "ECMKT": "LGAV", "N920FD": "LFPG",
    "OEIBZ": "EBLG", "EIDPG": "LEPA", "ECLTG": "LEPA", "EIFJP": "LEPA"
}


def SetGates(area, init_gate, end_gate, prefix):
    for i in range(init_gate, end_gate + 1):
        area.gates.append(Gate(f"{prefix}{i}"))


def create_lebl():
    lebl = BarcelonaAP("LEBL")
    t1 = Terminal("T1")
    areas_t1 = [("Area A", "Schengen", 1, 11), ("Area B", "Schengen", 1, 57), ("Area C", "Schengen", 1, 11),
                ("Area D", "non-Schengen", 1, 11), ("Area E", "non-Schengen", 1, 11)]
    for n, t, s, e in areas_t1:
        ba = BoardingArea(n, t)
        SetGates(ba, s, e, f"T1{n[-1]}G")
        t1.boarding_areas.append(ba)
    t2 = Terminal("T2")
    areas_t2 = [("Area M", "Schengen", 1, 8), ("Area R", "Schengen", 9, 19), ("Area S", "Schengen", 20, 30),
                ("Area U", "Schengen", 30, 39), ("Area W", "non-Schengen", 40, 49), ("Area Y", "non-Schengen", 50, 59)]
    for n, t, s, e in areas_t2:
        ba = BoardingArea(n, t)
        SetGates(ba, s, e, f"T2{n[-1]}G")
        t2.boarding_areas.append(ba)
    lebl.terminals = [t1, t2]
    return lebl


# Desactivem plt.show per evitar errors a l'hora de visualitzar els plots
plt.show = lambda: None

airports_list = []
aircrafts_list = []
texto_acumulado = ""


# GESTIÓ DE LA CONSOLA
def log_message(mensaje):  # Imprimeix el text de la consola
    if status_display:
        status_display.config(state=tk.NORMAL)
        status_display.insert(tk.END, f"» {mensaje}\n")
        status_display.see(tk.END)
        status_display.config(state=tk.DISABLED)


def procesar_salida(cadena):  # Elimina els salts de text innecesaris
    global texto_acumulado
    texto_acumulado += cadena
    if "\n" in texto_acumulado:
        lineas = texto_acumulado.split("\n")
        for linea in lineas[:-1]:
            limpia = linea.strip()
            if limpia:
                log_message(limpia)
        texto_acumulado = lineas[-1]


sys.stdout.write = procesar_salida  # Tot el que s'imprimeixi es fica a la interface


# FUNCIONS DE SUPORT V1/V2
def update_listbox():  # Refresca la llista de la interface
    listbox_airports.delete(0, tk.END)
    for ap in airports_list:
        listbox_airports.insert(tk.END, f"  {ap.icao}")


def on_select_airport(event):
    selection = listbox_airports.curselection()
    if selection:
        index = selection[0]
        ap = airports_list[index]
        entry_icao.delete(0, tk.END);
        entry_icao.insert(0, str(ap.icao))
        entry_lat.delete(0, tk.END);
        entry_lat.insert(0, str(ap.latitude))
        entry_lon.delete(0, tk.END);
        entry_lon.insert(0, str(ap.longitude))
        print(f"Seleccionat: {ap.icao}")


def embed_plot(func, data):  # Per dibuixar els plots dins de la interface del tkinter
    if not data or len(data) == 0:
        func(data)
        return
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    plt.close('all')
    try:
        func(data)
        fig = plt.gcf()
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        print("Gràfic actualitzat.")
    except Exception as e:
        log_message(f"ERROR en graficar: {e}")


# COMANDES BOTONS V1/V2
def cmd_add():
    try:
        icao, lat, lon = entry_icao.get().upper(), float(entry_lat.get()), float(entry_lon.get())
        nuevo_ap = Airport(icao, lat, lon)
        SetSchengen(nuevo_ap)
        if AddAirport(airports_list, nuevo_ap):
            print(f"Afegit: {icao}")
            update_listbox()
    except:
        log_message("Error: Dades invàlides.")


def cmd_remove():
    if RemoveAirport(airports_list, entry_icao.get().upper()):
        update_listbox()


def cmd_load_v1():
    global airports_list
    airports_list = LoadAirports("Airports.txt")
    if airports_list:
        for ap in airports_list:
            SetSchengen(ap)
        print(f"V1: {len(airports_list)} aeroports carregats.")
        update_listbox()


def cmd_load_v2():
    global aircrafts_list
    ruta = filedialog.askopenfilename(title="Seleccionar Arribades", filetypes=[("Arxius de text", "*.txt")])
    if ruta:
        aircrafts_list = LoadArrivals(ruta)
        print(f"V2: {len(aircrafts_list)} aeronaus carregades.")


# --- CONFIGURACIÓ DE PALETA DE COLORS SANZO WADA ---
WADA_BG_MAIN = "#F4F1EA"  # Beige
WADA_BG_SIDEBAR = "#E5E1D8"  # Gris
WADA_ACCENT_BLUE = "#3B5266"  # Blau
WADA_TEXT_DARK = "#2B2A28"  # Carboni suau
WADA_TEXT_LIGHT = "#FDFCFA"  # Blanc
WADA_GATE_FREE = "#C3D3C4"  # Verd
WADA_GATE_OCCUPIED = "#D9A091"  # Coral
WADA_CANVAS_BG = "#EBE7DF"  # Gris

# DISSENY AMB TKINTER
window = tk.Tk()
window.title("Terminal Control ")  # <-- Canviat per un nom més net
window.geometry("1320x880")
window.configure(bg=WADA_BG_MAIN)

# CONFIGURACIÓ ESTILS TTK
style = ttk.Style()
style.theme_use('clam')

# Adaptació de widgets globals
style.configure('.', background=WADA_BG_MAIN, foreground=WADA_TEXT_DARK, font=("Segoe UI", 10))
style.configure('TLabel', background=WADA_BG_MAIN, foreground=WADA_TEXT_DARK, font=("Segoe UI", 10))
style.configure('TEntry', fieldbackground="#FFFFFF", foreground=WADA_TEXT_DARK, bordercolor=WADA_BG_SIDEBAR)

# Estil personalitzat pels botons
style.configure('TButton', background=WADA_ACCENT_BLUE, foreground=WADA_TEXT_LIGHT, font=("Segoe UI", 10, "bold"),
                borderwidth=0, focuscolor="none")
style.map('TButton', background=[('active', '#4D687E'), ('pressed', '#2D3F50')])

# Estil de les Pestanyes
style.configure('TNotebook', background=WADA_BG_MAIN, borderwidth=0)
style.configure('TNotebook.Tab', background=WADA_BG_SIDEBAR, foreground=WADA_TEXT_DARK, font=("Segoe UI", 9, "bold"),
                padding=[12, 6])
style.map('TNotebook.Tab', background=[('selected', WADA_BG_MAIN)], foreground=[('selected', WADA_ACCENT_BLUE)])

# Panell esquerre
f_left = tk.Frame(window, bg=WADA_BG_SIDEBAR, padx=20, pady=20)
f_left.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(f_left, text="DADES DE L'AEROPORT", font=("Segoe UI", 12, "bold"), bg=WADA_BG_SIDEBAR,
         fg=WADA_ACCENT_BLUE).pack(pady=(10, 20))
tk.Label(f_left, text="Codi ICAO:", font=("Segoe UI", 9, "bold"), bg=WADA_BG_SIDEBAR, fg=WADA_TEXT_DARK).pack(
    anchor="w")
entry_icao = ttk.Entry(f_left, width=28);
entry_icao.pack(pady=(2, 12))
tk.Label(f_left, text="Latitud:", font=("Segoe UI", 9, "bold"), bg=WADA_BG_SIDEBAR, fg=WADA_TEXT_DARK).pack(anchor="w")
entry_lat = ttk.Entry(f_left, width=28);
entry_lat.pack(pady=(2, 12))
tk.Label(f_left, text="Longitud:", font=("Segoe UI", 9, "bold"), bg=WADA_BG_SIDEBAR, fg=WADA_TEXT_DARK).pack(anchor="w")
entry_lon = ttk.Entry(f_left, width=28);
entry_lon.pack(pady=(2, 15))

btns = tk.Frame(f_left, bg=WADA_BG_SIDEBAR)
btns.pack(pady=10)
ttk.Button(btns, text="Afegir", command=cmd_add).pack(side=tk.LEFT, padx=4)
ttk.Button(btns, text="Eliminar", command=cmd_remove).pack(side=tk.LEFT, padx=4)

listbox_airports = tk.Listbox(f_left, width=28, height=18, font=("Consolas", 10), bg="#FDFCFA", fg=WADA_TEXT_DARK,
                              selectbackground=WADA_ACCENT_BLUE, selectforeground=WADA_TEXT_LIGHT, relief="flat",
                              highlightthickness=1, highlightbackground=WADA_BG_MAIN)
listbox_airports.pack(pady=15)
listbox_airports.bind('<<ListboxSelect>>', on_select_airport)

# Panell dret amb PESTANYES
f_right = tk.Frame(window, bg=WADA_BG_MAIN, padx=20, pady=20)
f_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

notebook = ttk.Notebook(f_right)
notebook.pack(fill="both", expand=True)

tab_v1v2 = tk.Frame(notebook, bg=WADA_BG_MAIN)
tab_v3 = tk.Frame(notebook, bg=WADA_BG_MAIN)

# Noms de les pestanyes canviats per treure l'estil artificial/robòtic
notebook.add(tab_v1v2, text=" Panell de Trànsit ")
notebook.add(tab_v3, text=" Assignació de Portes ")

# --- CONTINGUT V1/V2 ---
t1 = tk.Frame(tab_v1v2, bg=WADA_BG_MAIN, pady=5)
t1.pack(fill=tk.X)
ttk.Button(t1, text="Carregar Arxiu", command=cmd_load_v1).pack(side=tk.LEFT, padx=3)
ttk.Button(t1, text="Guardar Schengen", command=lambda: SaveSchengenAirports(airports_list, "Schengen.txt")).pack(
    side=tk.LEFT, padx=3)
ttk.Button(t1, text="Gràfic V1", command=lambda: embed_plot(PlotAirports, airports_list)).pack(side=tk.LEFT, padx=3)
ttk.Button(t1, text="Mapa V1", command=lambda: MapAirports(airports_list, frame_grafico)).pack(side=tk.LEFT, padx=3)

t2 = tk.Frame(tab_v1v2, bg=WADA_BG_MAIN, pady=5)
t2.pack(fill=tk.X)
ttk.Button(t2, text="Carregar Arribades", command=cmd_load_v2).pack(side=tk.LEFT, padx=3)
ttk.Button(t2, text="Gràfic Hores", command=lambda: embed_plot(PlotArrivals, aircrafts_list)).pack(side=tk.LEFT, padx=3)
ttk.Button(t2, text="Gràfic Aerolínies", command=lambda: embed_plot(PlotAirlines, aircrafts_list)).pack(side=tk.LEFT,
                                                                                                        padx=3)
ttk.Button(t2, text="Gràfic Type", command=lambda: embed_plot(PlotFlightsType, aircrafts_list)).pack(side=tk.LEFT,
                                                                                                     padx=3)
ttk.Button(t2, text="Mapa Vols", command=lambda: MapFlights(aircrafts_list, frame_grafico)).pack(side=tk.LEFT, padx=3)
ttk.Button(t2, text="Mapa >2000km",
           command=lambda: MapFlights(LongDistanceArrivals(aircrafts_list), frame_grafico)).pack(side=tk.LEFT, padx=3)

frame_grafico = tk.Frame(tab_v1v2, bg="#FFFFFF", highlightbackground=WADA_BG_SIDEBAR, highlightthickness=1)
frame_grafico.pack(fill=tk.BOTH, expand=True, pady=10)


# --- CONTINGUT V3 --
class V3Manager:
    def __init__(self, master):
        self.master = master
        self.airport = create_lebl()
        self.color_free, self.color_occ = WADA_GATE_FREE, WADA_GATE_OCCUPIED
        self.color_accent = WADA_ACCENT_BLUE

        self.stats_lbl = tk.Label(master, text="", font=("Segoe UI", 10, "bold"), bg=WADA_BG_MAIN, fg=WADA_TEXT_DARK)
        self.stats_lbl.pack(pady=8)

        container = tk.Frame(master, bg=WADA_CANVAS_BG)
        container.pack(fill="both", expand=True, padx=10)

        self.canvas = tk.Canvas(container, bg=WADA_CANVAS_BG, highlightthickness=0)

        # Barra de desplaçament VERTICAL afegida per poder baixar i veure totes les files de portes
        sb_y = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        sb_y.pack(side="right", fill="y")

        # Barra de desplaçament HORIZONTAL original
        sb_x = tk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        sb_x.pack(side="bottom", fill="x")

        self.scroll_frame = tk.Frame(self.canvas, bg=WADA_CANVAS_BG)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        # Vinculem les dues barres al Canvas
        self.canvas.configure(xscrollcommand=sb_x.set, yscrollcommand=sb_y.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.info_var = tk.StringVar(value="Clica una porta per validar un vol (Departures/Arrivals)")

        info_lbl = tk.Label(master, textvariable=self.info_var, bg=WADA_BG_SIDEBAR, fg=WADA_TEXT_DARK,
                            font=("Segoe UI", 10, "italic"), relief="flat", pady=12, bd=0)
        info_lbl.pack(fill="x", padx=10, pady=12)
        self.render_all()

    def render_all(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        total, occ = 0, 0
        for terminal in self.airport.terminals:
            t_f = tk.Frame(self.scroll_frame, bg=WADA_CANVAS_BG, padx=15)
            t_f.pack(side="left", fill="y")
            tk.Label(t_f, text=terminal.name, font=("Segoe UI", 13, "bold"), bg=WADA_CANVAS_BG,
                     fg=self.color_accent).pack(anchor="w", pady=(5, 0))
            tk.Frame(t_f, height=3, bg=self.color_accent).pack(fill="x", pady=4)
            p_f = tk.Frame(t_f, bg=WADA_CANVAS_BG)
            p_f.pack()
            for area in terminal.boarding_areas:
                a_f = tk.Frame(p_f, bg=WADA_CANVAS_BG, padx=10)
                a_f.pack(side="left", anchor="n")
                grid = tk.Frame(a_f, bg=WADA_CANVAS_BG)
                grid.pack(pady=5)
                for i, gate in enumerate(area.gates):
                    total += 1
                    if gate.occupied: occ += 1
                    r, c = i // 2, (0 if i % 2 == 0 else 2)
                    bg = self.color_occ if gate.occupied else self.color_free
                    fg_btn = WADA_TEXT_DARK

                    btn = tk.Button(grid, text=gate.name.split("G")[-1], width=4, bg=bg, fg=fg_btn,
                                    font=("Segoe UI", 8, "bold"), relief="flat", activebackground=bg,
                                    command=lambda g=gate: self.manage(g))
                    btn.grid(row=r, column=c, pady=2, padx=2)
                    if c == 0: tk.Frame(grid, width=3, bg=self.color_accent).grid(row=r, column=1, sticky="ns")
                tk.Label(a_f, text=area.name, font=("Segoe UI", 9, "bold"), bg=WADA_CANVAS_BG, fg=WADA_TEXT_DARK).pack(
                    pady=4)
        self.stats_lbl.config(text=f"Portes Totals: {total}  |  Ocupades: {occ}  |  Lliures: {total - occ}")

    def manage(self, gate):
        if not gate.occupied:
            f_id = simpledialog.askstring("Validació", "Introdueix codi AIRCRAFT:")
            if f_id:
                f_id = f_id.upper()
                if f_id in DEPARTURES:
                    gate.occupied, gate.aircraft_id = True, f_id
                    self.info_var.set(f" VALIDAT: {f_id} cap a {DEPARTURES[f_id]}")
                elif f_id in ARRIVALS:
                    gate.occupied, gate.aircraft_id = True, f_id
                    self.info_var.set(f" VALIDAT: {f_id} des de {ARRIVALS[f_id]}")
                else:
                    messagebox.showerror("Error", "Codi no trobat.")
        else:
            if messagebox.askyesno("Alliberar", f"Alliberar porta {gate.name}?"):
                gate.occupied = False
                self.info_var.set(f"Porta {gate.name} lliure.")
        self.render_all()


v3_app = V3Manager(tab_v3)

# HISTORIAL / CONSOLA (COMÚ)
status_display = tk.Text(f_right, height=8, bg="#FDFCFA", fg=WADA_TEXT_DARK, relief="flat",
                         highlightthickness=1, highlightbackground=WADA_BG_SIDEBAR, font=("Consolas", 10), padx=8,
                         pady=8)
status_display.pack(fill=tk.X, pady=(15, 0))
status_display.config(state=tk.DISABLED)

import tkintermapview


# --- FUNCIÓN MAPAIRPORTS ---
def MapAirports(airports, frame=None):
    if not airports:
        log_message("No hi ha aeroports per mostrar.")
        return
    if frame is None:
        log_message("Error: No s'ha definit un frame per al mapa.")
        return
    for widget in frame.winfo_children():
        widget.destroy()
    plt.close('all')
    avg_lat = sum(a.latitude for a in airports) / len(airports)
    avg_lon = sum(a.longitude for a in airports) / len(airports)
    map_widget = tkintermapview.TkinterMapView(frame, corner_radius=0)
    map_widget.pack(fill="both", expand=True)
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    map_widget.set_position(avg_lat, avg_lon)
    map_widget.set_zoom(5)

    for ap in airports:
        color = "#8FA89B" if ap.schengen else "#D18A7D"
        map_widget.set_marker(ap.latitude, ap.longitude, text=ap.icao, marker_color_circle=color,
                              marker_color_outside="#F4F1EA", text_color="#2B2A28", font=("Segoe UI", 10, "bold"))
    log_message(f"Mapa generat amb {len(airports)} aeroports.")


window.mainloop()