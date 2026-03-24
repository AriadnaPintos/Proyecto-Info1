import tkinter as tk
from airport import *

airports = []


#Creem les funcions corresponents
def load_data():
    global airports
    airports = LoadAirports("Airports.txt")
    print("Aeropuertos cargados!")


def add_one():
    try:
        #LLegim el contingut de les "caixes"
        code = entry_icao.get()
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())

        new_ap = Airport(code, lat, lon)
        AddAirport(airports, new_ap)
        print("Aeropuerto", code, "añadido!")

        #Netejar les caixes després de ficar-ho
        entry_icao.delete(0, tk.END)
        entry_lat.delete(0, tk.END)
        entry_lon.delete(0, tk.END)

    except ValueError:
        print("Error: Asegúrate de que la latitud y longitud sean números.")


def remove_one():
    code = entry_icao.get()
    if code:
        RemoveAirport(airports, code)
        print(f"Aeropuerto",code,"eliminado!")
    else:
        print("Introduce un ICAO en la caja de texto")


def save_data():
    SaveSchengenAirports(airports, "schengenairport.txt")
    print("Schengen aeropuertos guardados!")

def show_plot():
    PlotAirports(airports)

def show_map():
    MapAirports(airports)

#Part tkinker
window = tk.Tk()
window.title("GESTIÓN AEROPUERTOS")
window.geometry("450x500")

title_label = tk.Label(window, text="GESTIÓN AEROPUERTOS", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

#Part de les caixes
frame_inputs = tk.Frame(window)
frame_inputs.pack(pady=10)

tk.Label(frame_inputs, text="ICAO:").grid(row=0, column=0, padx=5, sticky="e")
entry_icao = tk.Entry(frame_inputs)
entry_icao.grid(row=0, column=1, pady=2)

tk.Label(frame_inputs, text="Latitud:").grid(row=1, column=0, padx=5, sticky="e")
entry_lat = tk.Entry(frame_inputs)
entry_lat.grid(row=1, column=1, pady=2)

tk.Label(frame_inputs, text="Longitud:").grid(row=2, column=0, padx=5, sticky="e")
entry_lon = tk.Entry(frame_inputs)
entry_lon.grid(row=2, column=1, pady=2)

#Part botons
tk.Button(window, text="Cargar 'Airports.txt'", command=load_data).pack(pady=2)
tk.Button(window, text="Añadir (usa las cajas de arriba)", command=add_one, bg="#e1f5fe").pack(pady=2)
tk.Button(window, text="Eliminar (usa caja ICAO)", command=remove_one).pack(pady=2)
tk.Button(window, text="Guardar Schengen", command=save_data).pack(pady=2)
tk.Button(window, text="Mostrar Gráfica", command=show_plot).pack(pady=2)
tk.Button(window, text="Mostrar Mapa", command=show_map).pack(pady=2)

window.mainloop()