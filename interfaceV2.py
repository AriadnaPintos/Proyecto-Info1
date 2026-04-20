import tkinter as tk
from tkinter import ttk, filedialog
import sys
import warnings

# Bloquegem els avisos de Matplotlib abans d'importar
warnings.filterwarnings("ignore", category=UserWarning)

import matplotlib
matplotlib.use('Agg') # Importació pel Matplotlib, per tal de bloquejar el avisos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from airport import *
from aircrafts import *

# Desactivem plt.show per evitar errors a l'hora de visualitzar els plots
plt.show = lambda: None

airports_list = []
aircrafts_list = []
texto_acumulado = ""

# GESTIÓ DE LA CONSOLA
def log_message(mensaje): # Imprimeix el text de la consola
    if status_display:
        status_display.config(state=tk.NORMAL)
        status_display.insert(tk.END, f"» {mensaje}\n")
        status_display.see(tk.END)
        status_display.config(state=tk.DISABLED)

def procesar_salida(cadena): # Elimina els salts de text innecesaris
    global texto_acumulado
    texto_acumulado += cadena
    if "\n" in texto_acumulado:
        lineas = texto_acumulado.split("\n")
        for linea in lineas[:-1]:
            limpia = linea.strip()
            if limpia:
                log_message(limpia)
        texto_acumulado = lineas[-1]

sys.stdout.write = procesar_salida #Tot el que s'imprimeixi es fica a la interface
sys.stderr.write = lambda s: None

# FUNCIONS DE SUPORT

def update_listbox(): # Refresca la llista de la interface
    listbox_airports.delete(0, tk.END)
    for ap in airports_list:
        listbox_airports.insert(tk.END, f"  {ap.icao}")

def on_select_airport(event):
    selection = listbox_airports.curselection()
    if selection:
        index = selection[0]
        ap = airports_list[index]
        entry_icao.delete(0, tk.END); entry_icao.insert(0, str(ap.icao))
        entry_lat.delete(0, tk.END); entry_lat.insert(0, str(ap.latitude))
        entry_lon.delete(0, tk.END); entry_lon.insert(0, str(ap.longitude))
        print(f"Seleccionat: {ap.icao}")

def embed_plot(func, data): # Per dibuixar els plots dins de la interface del tkinter
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

# COMANDES BOTONS

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

# DISSENY AMB TKINTER

window = tk.Tk()
window.title("Gestor Aeronàutic LEBL - Versió 2.1")
window.geometry("1300x850")
window.configure(bg="#f2f2f2")

# Panell esquerre
f_left = tk.Frame(window, bg="#f2f2f2", padx=20, pady=20)
f_left.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(f_left, text="DADES DE L'AEROPORT", font=("Arial", 11, "bold"), bg="#f2f2f2").pack(pady=10)
tk.Label(f_left, text="Codi ICAO:", bg="#f2f2f2").pack(anchor="w")
entry_icao = ttk.Entry(f_left, width=30); entry_icao.pack(pady=5)
tk.Label(f_left, text="Latitud:", bg="#f2f2f2").pack(anchor="w")
entry_lat = ttk.Entry(f_left, width=30); entry_lat.pack(pady=5)
tk.Label(f_left, text="Longitud:", bg="#f2f2f2").pack(anchor="w")
entry_lon = ttk.Entry(f_left, width=30); entry_lon.pack(pady=5)

btns = tk.Frame(f_left, bg="#f2f2f2")
btns.pack(pady=10)
ttk.Button(btns, text="Afegir", command=cmd_add).pack(side=tk.LEFT, padx=2)
ttk.Button(btns, text="Eliminar", command=cmd_remove).pack(side=tk.LEFT, padx=2)

listbox_airports = tk.Listbox(f_left, width=35, height=18, font=("Courier", 10))
listbox_airports.pack(pady=5)
listbox_airports.bind('<<ListboxSelect>>', on_select_airport)

# Panell dret
f_right = tk.Frame(window, bg="white", padx=20, pady=20)
f_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=20)

# Barra d'eines versió 1
t1 = tk.Frame(f_right, bg="white")
t1.pack(fill=tk.X)
ttk.Button(t1, text="Carregar Arxiu", command=cmd_load_v1).pack(side=tk.LEFT, padx=2)
ttk.Button(t1, text="Guardar Schengen", command=lambda: SaveSchengenAirports(airports_list, "Schengen.txt")).pack(side=tk.LEFT, padx=2)
ttk.Button(t1, text="Gràfic V1", command=lambda: embed_plot(PlotAirports, airports_list)).pack(side=tk.LEFT, padx=2)
ttk.Button(t1, text="Mapa V1", command=lambda: MapAirports(airports_list)).pack(side=tk.LEFT, padx=2)

# Barra d'eines versió 2
t2 = tk.Frame(f_right, bg="white", pady=10)
t2.pack(fill=tk.X)
ttk.Button(t2, text="Carregar Arribades", command=cmd_load_v2).pack(side=tk.LEFT, padx=2)
ttk.Button(t2, text="Gràfic Hores", command=lambda: embed_plot(PlotArrivals, aircrafts_list)).pack(side=tk.LEFT, padx=2)
ttk.Button(t2, text="Gràfic Aerolínies", command=lambda: embed_plot(PlotAirlines, aircrafts_list)).pack(side=tk.LEFT, padx=2)
ttk.Button(t2, text="Gràfic Schengen V2", command=lambda: embed_plot(PlotFlightsType, aircrafts_list)).pack(side=tk.LEFT, padx=2)
ttk.Button(t2, text="Mapa Vols", command=lambda: MapFlights(aircrafts_list)).pack(side=tk.LEFT, padx=2)
ttk.Button(t2, text="Mapa >2000km", command=lambda: MapFlights(LongDistanceArrivals(aircrafts_list))).pack(side=tk.LEFT, padx=2)

# Historial
status_display = tk.Text(f_right, height=10, bg="#fafafa", relief="solid", borderwidth=1, font=("Consolas", 10))
status_display.pack(fill=tk.X, pady=15)
status_display.config(state=tk.DISABLED)

# Panell Gràfic
frame_grafico = tk.Frame(f_right, bg="white", highlightbackground="#cccccc", highlightthickness=1)
frame_grafico.pack(fill=tk.BOTH, expand=True)

window.mainloop()