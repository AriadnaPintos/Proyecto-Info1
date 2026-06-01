import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sys
import warnings
import os
import threading
import math
import wave
import struct

# Bloquegem els avisos de Matplotlib abans d'importar
warnings.filterwarnings("ignore", category=UserWarning)

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkintermapview

# Mòduls del projecte
from airport import *
from aircrafts import *
from LEBL import *


# ─── FUNCIÓ AUXILIAR DE SEGURETAT REQUERIDA ───
def _time_to_minutes(time_str):
    """Converteix format 'HH:MM' o 'H:MM' a minuts totals des de mitjanit"""
    if not time_str or time_str == "":
        return -1
    try:
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return -1


# ─── FUNCIÓ DE MAPA DE AEROPORTS MOVUDA A DALT DE TOT (CORREGIDA) ───
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
                              marker_color_outside="#F4F1EA", text_color="#2B2A28", font=("Helvetica", 10, "bold"))
    log_message(f"Mapa generat amb {len(airports)} aeroports.")


# ─── MOTOR DE SO (sense dependències externes) ───────────────────────────────
# Genera sons WAV en memòria i els reprodueix en un thread secundari.
# Funciona a Windows (winsound), macOS (afplay/aplay) i Linux (aplay/paplay).

def _write_wav_bytes(freq: float, duration: float, volume: float = 0.5,
                     wave_type: str = "sine", sample_rate: int = 44100) -> bytes:
    """Genera un buffer WAV PCM 16-bit mono en memòria."""
    n_samples = int(sample_rate * duration)
    import io
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            # Envelope ADSR simple per evitar clics
            attack  = min(1.0, t / 0.01) if duration > 0.02 else 1.0
            release = min(1.0, (duration - t) / 0.05) if t > duration - 0.05 else 1.0
            env = attack * release

            if wave_type == "sine":
                sample = math.sin(2 * math.pi * freq * t)
            elif wave_type == "square":
                sample = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            elif wave_type == "triangle":
                phase = (t * freq) % 1.0
                sample = 4 * phase - 1 if phase < 0.5 else 3 - 4 * phase
            elif wave_type == "noise":
                import random
                sample = random.uniform(-1, 1)
            else:
                sample = math.sin(2 * math.pi * freq * t)

            val = int(sample * env * volume * 32767)
            val = max(-32768, min(32767, val))
            frames += struct.pack('<h', val)
        wf.writeframes(bytes(frames))
    return buf.getvalue()


def _play_wav_bytes(wav_bytes: bytes):
    """Reprodueix un buffer WAV en el sistema operatiu disponible."""
    import tempfile, subprocess, platform
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_bytes)
            tmp_path = tmp.name
        plat = platform.system()
        if plat == "Windows":
            import winsound
            winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
        elif plat == "Darwin":
            subprocess.run(["afplay", tmp_path], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # Linux
            for player in ("aplay", "paplay", "ffplay"):
                try:
                    subprocess.run([player, tmp_path], check=False,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    break
                except FileNotFoundError:
                    continue
    except Exception:
        pass
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def _play_sequence(notes: list):
    """Toca una seqüència de (freq, duration, volume, wave_type) en un thread."""
    def _run():
        import io
        buf = io.BytesIO()
        all_samples = bytearray()
        sample_rate = 44100
        for freq, dur, vol, wtype in notes:
            wav = _write_wav_bytes(freq, dur, vol, wtype, sample_rate)
            # Extraiem els frames (saltem la capçalera WAV de 44 bytes)
            all_samples += wav[44:]
        # Construïm un WAV únic
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(bytes(all_samples))
        _play_wav_bytes(buf.getvalue())
    threading.Thread(target=_run, daemon=True).start()


# ─── SONS DEL SISTEMA ─────────────────────────────────────────────────────────

def sound_ok():
    """So positiu: dos tons ascendents (Do–Mi). Connexió viable, èxit."""
    _play_sequence([
        (523.25, 0.12, 0.45, "sine"),   # C5
        (659.25, 0.20, 0.45, "sine"),   # E5
    ])

def sound_error():
    """So negatiu: dos tons descendents (La–Fa). Error, connexió inviable."""
    _play_sequence([
        (440.00, 0.15, 0.45, "sine"),   # A4
        (349.23, 0.28, 0.45, "sine"),   # F4
    ])

def sound_warning():
    """So d'advertència: to doble ràpid (piu-piu)."""
    _play_sequence([
        (880.00, 0.08, 0.30, "square"),
        (880.00, 0.08, 0.30, "square"),
    ])

def sound_load():
    """So de càrrega: to suau i ràpid."""
    _play_sequence([
        (392.00, 0.10, 0.30, "sine"),   # G4
        (523.25, 0.12, 0.30, "sine"),   # C5
    ])

def sound_save():
    """So de desat correcte: arpegio ascendent."""
    _play_sequence([
        (392.00, 0.08, 0.35, "sine"),   # G4
        (523.25, 0.08, 0.35, "sine"),   # C5
        (659.25, 0.15, 0.35, "sine"),   # E5
    ])

def sound_delete():
    """So d'eliminació: to curt descendent."""
    _play_sequence([
        (440.00, 0.10, 0.30, "triangle"),
        (330.00, 0.15, 0.30, "triangle"),
    ])

def sound_conflict():
    """So de conflicte detectat: alarma breu de dos tons baixos."""
    _play_sequence([
        (220.00, 0.18, 0.50, "square"),
        (196.00, 0.28, 0.50, "square"),
    ])

def sound_sim_start():
    """So d'inici de simulació: to ascendent llarg."""
    _play_sequence([
        (330.00, 0.10, 0.30, "sine"),
        (440.00, 0.10, 0.30, "sine"),
        (523.25, 0.18, 0.30, "sine"),
    ])

def sound_sim_stop():
    """So de pausa/reset: to descendent curt."""
    _play_sequence([
        (440.00, 0.12, 0.28, "sine"),
        (330.00, 0.18, 0.28, "sine"),
    ])

# ─────────────────────────────────────────────────────────────────────────────

# --- BASE DE DADES DE VALIDACIÓ COHESIONADA V4 ---
DEPARTURES = {
    "ECLZN": "LGMK", "ECLQK": "LLBG", "ECHFK": "LEPA", "ECMHS": "LPPT",
    "ECMFN": "LEBB", "N327UP": "LEVC", "TCJSO": "LTBA", "EIDAM": "LIME",
    "EIDWK": "EBBR", "EIDCJ": "EGSS", "LYVEO": "LEST", "EIDHT": "EYVI",
    "GEZUM": "LSGG", "ECMLE": "LFRS", "EIDTO": "LIRF", "EIEFW": "LEST",
    "ECMBY": "LDZA", "ECLRG": "EDDP", "EIDAE": "LIRF", "EIFIY": "LEIB"
}

ARRIVALS = {
    "ECMKV": "LYBE", "ECJGM": "EGCC", "ECLOB": "LMML", "ECLVC": "LGTS",
    "DALEC": "EBBR", "N327UP": "LEVC", "TCJSO": "LTBA", "EIDAM": "LIME",
    "EIDWK": "EBBR", "EIDCJ": "EGSS", "LYVEO": "LEST", "EIDHT": "EYVI",
    "GEZUM": "LSGG", "ECMLE": "LFRS", "EIDTO": "LIRF", "EIEFW": "LEST",
    "ECMBY": "LDZA", "ECLRG": "EDDP", "EIDAE": "LIRF", "EIFIY": "LEIB"
}


def SetGates(area, init_gate, end_gate, prefix):
    for i in range(init_gate, end_gate + 1):
        area.gates.append(Gate(f"{prefix}{i}"))


# ─── MOTOR DE CREACIÓ PROTEGIT CONTRA EL BUG DE L'ARXIU DE COMPANYS ───
def create_lebl():
    lebl = BarcelonaAP("LEBL")

    # Terminal T1
    t1 = Terminal("T1")
    t1.airlines = []
    fitxer_t1 = "T1_Airlines.txt"
    if os.path.exists(fitxer_t1):
        with open(fitxer_t1, "r") as f_in:
            for line in f_in:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    t1.airlines.append(parts[1])
    else:
        t1.airlines = ["VLG", "IBE"]

    areas_t1 = [
        ("Area A", "Schengen", 1, 11),
        ("Area B", "Schengen", 1, 57),
        ("Area C", "Schengen", 1, 11),
        ("Area D", "non-Schengen", 1, 11),
        ("Area E", "non-Schengen", 1, 11)
    ]
    for n, t, s, e in areas_t1:
        ba = BoardingArea(n, t)
        SetGates(ba, s, e, f"T1{n[-1]}G")
        t1.boarding_areas.append(ba)

    # Terminal T2
    t2 = Terminal("T2")
    t2.airlines = []
    fitxer_t2 = "T2_Airlines.txt"
    if os.path.exists(fitxer_t2):
        with open(fitxer_t2, "r") as f_in:
            for line in f_in:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    t2.airlines.append(parts[1])
    else:
        t2.airlines = ["RYR", "EZY"]

    areas_t2 = [
        ("Area M", "Schengen", 1, 8),
        ("Area R", "Schengen", 9, 19),
        ("Area S", "Schengen", 20, 30),
        ("Area U", "Schengen", 30, 39),
        ("Area W", "non-Schengen", 40, 49),
        ("Area Y", "non-Schengen", 50, 59)
    ]
    for n, t, s, e in areas_t2:
        ba = BoardingArea(n, t)
        SetGates(ba, s, e, f"T2{n[-1]}G")
        t2.boarding_areas.append(ba)

    lebl.terminals = [t1, t2]
    return lebl


plt.show = lambda: None

airports_list = []
aircrafts_list = []
texto_acumulado = ""


def log_message(mensaje):
    if status_display:
        status_display.config(state=tk.NORMAL)
        status_display.insert(tk.END, f"» {mensaje}\n")
        status_display.see(tk.END)
        status_display.config(state=tk.DISABLED)


def procesar_salida(cadena):
    global texto_acumulado
    texto_acumulado += cadena
    if "\n" in texto_acumulado:
        lineas = texto_acumulado.split("\n")
        for linea in lineas[:-1]:
            limpia = linea.strip()
            if limpia:
                log_message(limpia)
        texto_acumulado = lineas[-1]


sys.stdout.write = procesar_salida

# PALETA SANZO WADA
WADA_BG_MAIN = "#F4F1EA"
WADA_BG_SIDEBAR = "#E5E1D8"
WADA_ACCENT_BLUE = "#3B5266"
WADA_TEXT_DARK = "#2B2A28"
WADA_TEXT_LIGHT = "#FDFCFA"
WADA_GATE_FREE = "#C3D3C4"
WADA_GATE_OCCUPIED = "#D9A091"
WADA_CANVAS_BG = "#EBE7DF"

window = tk.Tk()
window.title("Terminal Control ")
window.geometry("1450x900")
window.configure(bg=WADA_BG_MAIN)

style = ttk.Style()
style.theme_use('clam')
style.configure('.', background=WADA_BG_MAIN, foreground=WADA_TEXT_DARK, font=("Segoe UI", 10))
style.configure('TLabel', background=WADA_BG_MAIN, foreground=WADA_TEXT_DARK, font=("Segoe UI", 10))
style.configure('TEntry', fieldbackground="#FFFFFF", foreground=WADA_TEXT_DARK, bordercolor=WADA_BG_SIDEBAR)
style.configure('TButton', background=WADA_ACCENT_BLUE, foreground=WADA_TEXT_LIGHT, font=("Segoe UI", 10, "bold"),
                borderwidth=0, focuscolor="none")
style.map('TButton', background=[('active', '#4D687E'), ('pressed', '#2D3F50')])
style.configure('TNotebook', background=WADA_BG_MAIN, borderwidth=0)
style.configure('TNotebook.Tab', background=WADA_BG_SIDEBAR, foreground=WADA_TEXT_DARK, font=("Segoe UI", 9, "bold"),
                padding=[12, 6])
style.map('TNotebook.Tab', background=[('selected', WADA_BG_MAIN)], foreground=[('selected', WADA_ACCENT_BLUE)])


def update_listbox():
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


def embed_plot(func, data, modo_filtro=None):
    if not data or len(data) == 0:
        func(data)
        return
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    plt.close('all')
    try:
        if modo_filtro == "top10" or modo_filtro == "top20":
            limite = 10 if modo_filtro == "top10" else 20
            frecuencias = {}
            for ac in data:
                frecuencias[ac.airline] = frecuencias.get(ac.airline, 0) + 1
            top_airlines = sorted(frecuencias, key=frecuencias.get, reverse=True)[:limite]
            data_filtrada = [x for x in data if x.airline in top_airlines]
            func(data_filtrada)

        elif modo_filtro == "especifico":
            icao_target = simpledialog.askstring("Filtre Companyia",
                                                 "Introdueix el codi ICAO de l'aerolínia que vols veure (Ex: VLG, RYR):")
            if i_id := icao_target:
                data_filtrada = [x for x in data if x.airline == i_id.upper()]
                if len(data_filtrada) == 0:
                    messagebox.showwarning("Atenció",
                                           f"No s'han trobat vols de la companyia {i_id.upper()} en aquesta llista.")
                    return
                func(data_filtrada)
            else:
                return
        else:
            func(data)

        fig = plt.gcf()
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        print("Gràfic actualitzat.")
    except Exception as e:
        log_message(f"ERROR en graficar: {e}")


def abri_menu_filtros_airlines():
    if not aircrafts_list:
        messagebox.showwarning("Atenció", "Primer has de carregar les dades d'arribades a la Pestanya 1.")
        return

    filtro_win = tk.Toplevel(window)
    filtro_win.title("Filtre d'Aerolínies")
    filtro_win.geometry("350x200")
    filtro_win.configure(bg=WADA_BG_MAIN)
    filtro_win.resizable(False, False)

    tk.Label(filtro_win, text="Com vols visualitzar el gràfic?", font=("Segoe UI", 10, "bold"), bg=WADA_BG_MAIN,
             fg=WADA_ACCENT_BLUE).pack(pady=15)

    ttk.Button(filtro_win, text="Veure Top 10 Principals", width=25,
               command=lambda: [embed_plot(PlotAirlines, aircrafts_list, "top10"), filtro_win.destroy()]).pack(pady=4)
    ttk.Button(filtro_win, text="Veure Top 20 Principals", width=25,
               command=lambda: [embed_plot(PlotAirlines, aircrafts_list, "top20"), filtro_win.destroy()]).pack(pady=4)
    ttk.Button(filtro_win, text="Cercar Companyia Específica", width=25,
               command=lambda: [embed_plot(PlotAirlines, aircrafts_list, "especifico"), filtro_win.destroy()]).pack(
        pady=4)


def cmd_add():
    try:
        icao, lat, lon = entry_icao.get().upper(), float(entry_lat.get()), float(entry_lon.get())
        nuevo_ap = Airport(icao, lat, lon)
        SetSchengen(nuevo_ap)
        if AddAirport(airports_list, nuevo_ap):
            print(f"Afegit: {icao}")
            update_listbox()
            sound_ok()
        else:
            sound_warning()
    except:
        log_message("Error: Dades invàlides.")
        sound_error()


def cmd_remove():
    if RemoveAirport(airports_list, entry_icao.get().upper()):
        update_listbox()
        sound_delete()
    else:
        sound_error()


def cmd_load_v1():
    global airports_list
    airports_list = LoadAirports("Airports.txt")
    if airports_list:
        for ap in airports_list:
            SetSchengen(ap)
        print(f"V1: {len(airports_list)} aeroports carregats.")
        update_listbox()
        sound_load()
    else:
        sound_error()


def cmd_load_v2():
    global aircrafts_list
    ruta = filedialog.askopenfilename(title="Seleccionar Arribades", filetypes=[("Arxius de text", "*.txt")])
    if ruta:
        aircrafts_list = LoadArrivals(ruta)
        print(f"V2: {len(aircrafts_list)} aeronaus carregades.")
        sound_load()
        if 'v4_app' in globals():
            v4_app.refresh_flights_listbox()


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

f_right = tk.Frame(window, bg=WADA_BG_MAIN, padx=20, pady=20)
f_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

notebook = ttk.Notebook(f_right)
notebook.pack(fill="both", expand=True)

tab_v1v2 = tk.Frame(notebook, bg=WADA_BG_MAIN)
tab_v4 = tk.Frame(notebook, bg=WADA_BG_MAIN)
tab_connection = tk.Frame(notebook, bg=WADA_BG_MAIN)
tab_conflicts  = tk.Frame(notebook, bg=WADA_BG_MAIN)


tab_carbon = tk.Frame(notebook, bg=WADA_BG_MAIN)

notebook.add(tab_v1v2,       text=" Panell de Trànsit ")
notebook.add(tab_v4,         text=" Control de Portes i Simulació (V4) ")
notebook.add(tab_connection, text=" Connexions ")
notebook.add(tab_conflicts,  text=" Conflictes i Informe ")

notebook.add(tab_carbon, text=" Emprempta de Carboni ")

notebook.add(tab_v1v2, text=" Panell de Trànsit ")
notebook.add(tab_v4, text=" Control de Portes i Simulació (V4 Unificada) ")
notebook.add(tab_connection, text=" Connexions ")
class ConflictAnalyzer:
    def __init__(self, master):
        self.master = master
        self._build_ui()

    def _build_ui(self):
        tk.Label(self.master, text="Anàlisi de Conflictes i Cuellos de Botella",
                 font=("Segoe UI", 13, "bold"),
                 bg=WADA_BG_MAIN, fg=WADA_ACCENT_BLUE).pack(pady=(14, 6))

        btn_frame = tk.Frame(self.master, bg=WADA_BG_MAIN)
        btn_frame.pack(pady=6)

        ttk.Button(btn_frame, text="Detectar Conflictes de Porta",
                   command=self._detect).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Moments Crítics del Dia",
                   command=self._critical).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Generar Informe .txt",
                   command=self._report).pack(side=tk.LEFT, padx=6)

        self.text = tk.Text(self.master, bg="#FDFCFA", fg=WADA_TEXT_DARK,
                            font=("Consolas", 9), relief="flat",
                            highlightthickness=1,
                            highlightbackground=WADA_BG_SIDEBAR,
                            padx=10, pady=10)
        self.text.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

    def _write(self, text, clear=True):
        self.text.config(state=tk.NORMAL)
        if clear:
            self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)
        self.text.config(state=tk.DISABLED)

    def _detect(self):
        if not v4_app.cronograma_complet:
            messagebox.showwarning("Atenció", "Primer carrega el cronograma a la pestanya V4.")
            return

        conflicts = DetectGateConflicts(v4_app.airport, v4_app.cronograma_complet)

        if not conflicts:
            self._write("✅ Cap conflicte de porta detectat al cronograma actual.\n")
            sound_ok()
            return

        lines = [f"⚠️  {len(conflicts)} conflicte(s) detectat(s):\n", "─" * 55 + "\n"]
        for c in conflicts:
            t_ini = f"{c['overlap_start']//60:02d}:{c['overlap_start']%60:02d}"
            t_fi  = f"{c['overlap_end']//60:02d}:{c['overlap_end']%60:02d}"
            alt   = ProposeAlternativeGate(v4_app.airport,
                        next((a for a in v4_app.cronograma_complet
                              if a.id == c['ac1']), None),
                        c['gate'])
            alt_txt = f"→ Porta alternativa suggeria: {alt}" if alt else "→ No hi ha portes alternatives lliures"
            lines.append(
                f"Porta {c['gate']}: {c['ac1']} i {c['ac2']} "
                f"solapen {t_ini}–{t_fi}\n   {alt_txt}\n\n"
            )
        self._write("".join(lines))
        sound_conflict()

    def _critical(self):
        if not v4_app.cronograma_complet:
            messagebox.showwarning("Atenció", "Primer carrega el cronograma a la pestanya V4.")
            return

        moments = CriticalMoments(v4_app.cronograma_complet, threshold=5)

        if not moments:
            self._write("✅ Cap moment crític detectat (threshold: 5 avions simultanis).\n")
            sound_ok()
            return

        lines = [f"🔴 {len(moments)} franja(es) crítiques:\n", "─" * 55 + "\n"]
        for m in moments:
            lines.append(
                f"{m['hour']}  →  {m['count']} avions a terra\n"
                f"   IDs: {', '.join(m['aircraft_ids'][:8])}"
                f"{'...' if len(m['aircraft_ids']) > 8 else ''}\n\n"
            )
        self._write("".join(lines))
        sound_warning()

    def _report(self):
        if not v4_app.cronograma_complet:
            messagebox.showwarning("Atenció", "Primer carrega el cronograma a la pestanya V4.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fitxer de text", "*.txt")],
            title="Guardar informe"
        )
        if not path:
            return

        conflicts = DetectGateConflicts(v4_app.airport, v4_app.cronograma_complet)
        moments   = CriticalMoments(v4_app.cronograma_complet, threshold=5)

        with open(path, "w") as f:
            f.write("=" * 55 + "\n")
            f.write("  INFORME DE CONFLICTES I MOMENTS CRÍTICS — LEBL\n")
            f.write("=" * 55 + "\n\n")

            f.write(f"CONFLICTES DE PORTA ({len(conflicts)})\n")
            f.write("-" * 40 + "\n")
            if not conflicts:
                f.write("Cap conflicte detectat.\n")
            for c in conflicts:
                t_ini = f"{c['overlap_start']//60:02d}:{c['overlap_start']%60:02d}"
                t_fi  = f"{c['overlap_end']//60:02d}:{c['overlap_end']%60:02d}"
                alt   = ProposeAlternativeGate(v4_app.airport,
                            next((a for a in v4_app.cronograma_complet
                                  if a.id == c['ac1']), None),
                            c['gate'])
                f.write(f"Porta {c['gate']}: {c['ac1']} i {c['ac2']} "
                        f"solapen {t_ini}-{t_fi}\n")
                f.write(f"  Alternativa: {alt if alt else 'No disponible'}\n\n")

            f.write(f"\nMOMENTS CRÍTICS ({len(moments)})\n")
            f.write("-" * 40 + "\n")
            if not moments:
                f.write("Cap moment crític.\n")
            for m in moments:
                f.write(f"{m['hour']}: {m['count']} avions simultanis\n")
                f.write(f"  {', '.join(m['aircraft_ids'])}\n\n")

        log_message(f"Informe guardat a: {path}")
        messagebox.showinfo("Informe generat", f"Guardat correctament a:\n{path}")
        sound_save()


conflict_analyzer = ConflictAnalyzer(tab_conflicts)

# --- PESTANYA 1 (Trànsit) ---
t1 = tk.Frame(tab_v1v2, bg=WADA_BG_MAIN, pady=5)
t1.pack(fill=tk.X)
ttk.Button(t1, text="Carregar Arxiu", command=cmd_load_v1).pack(side=tk.LEFT, padx=3)
ttk.Button(t1, text="Guardar Schengen", command=lambda: [SaveSchengenAirports(airports_list, "Schengen.txt"), sound_save()]).pack(
    side=tk.LEFT, padx=3)
ttk.Button(t1, text="Gràfic V1", command=lambda: embed_plot(PlotAirports, airports_list)).pack(side=tk.LEFT, padx=3)

# MODIFICAT: S'ha passat el paràmetre frame_grafico perquè la funció pugui obrir-se dins del contenidor correctament
ttk.Button(t1, text="Mapa V1", command=lambda: MapAirports(airports_list, frame_grafico)).pack(side=tk.LEFT, padx=3)

t2 = tk.Frame(tab_v1v2, bg=WADA_BG_MAIN, pady=5)
t2.pack(fill=tk.X)
ttk.Button(t2, text="Carregar Arribades", command=cmd_load_v2).pack(side=tk.LEFT, padx=3)
ttk.Button(t2, text="Gràfic Hores", command=lambda: embed_plot(PlotArrivals, aircrafts_list)).pack(side=tk.LEFT, padx=3)
ttk.Button(t2, text="Gràfic Aerolínies", command=abri_menu_filtros_airlines).pack(side=tk.LEFT, padx=3)
ttk.Button(t2, text="Gràfic Tipus de Vol", command=lambda: embed_plot(PlotFlightsType, aircrafts_list)).pack(
    side=tk.LEFT, padx=3)
ttk.Button(t2, text="Mapa Vols", command=lambda: MapFlights(aircrafts_list, frame_grafico)).pack(side=tk.LEFT, padx=3)

frame_grafico = tk.Frame(tab_v1v2, bg="#FFFFFF", highlightbackground=WADA_BG_SIDEBAR, highlightthickness=1)
frame_grafico.pack(fill=tk.BOTH, expand=True, pady=10)


# ─── GESTOR COMPLET UNIFICAT VERSIÓ 4 ───
class V4UnifiedManager:
    def __init__(self, master):
        self.master = master
        self.airport = create_lebl()
        self.cronograma_complet = []
        self.simulacio_activa = False
        self.cambios_manuales = {}
        self.sim_running = False
        self.sim_minute = 480
        self.speed_var = tk.IntVar(value=1)
        self._sim_job = None

        self.paned = tk.PanedWindow(master, orient=tk.HORIZONTAL, bg=WADA_BG_MAIN, sashrelief=tk.FLAT, sashwidth=4)
        self.paned.pack(fill=tk.BOTH, expand=True, pady=5)

        self.f_vols_side = tk.Frame(self.paned, bg=WADA_BG_SIDEBAR, padx=10, pady=10, width=325)

        self.f_time_header = tk.Frame(self.f_vols_side, bg=WADA_BG_SIDEBAR)
        self.f_time_header.pack(fill=tk.X, pady=(0, 5))

        tk.Label(self.f_time_header, text="CRONOGRAMA", font=("Segoe UI", 10, "bold"), bg=WADA_BG_SIDEBAR,
                 fg=WADA_ACCENT_BLUE).pack(side=tk.LEFT, anchor="w")

        self.hour_var = tk.StringVar(value="08:00")
        self.hour_combo = ttk.Combobox(self.f_time_header, textvariable=self.hour_var,
                                       values=[f"{h:02d}:00" for h in range(24)], width=7, state="readonly")
        self.hour_combo.pack(side=tk.RIGHT, anchor="e")
        self.hour_combo.bind("<<ComboboxSelected>>", self.on_time_changed)

        self.listbox_vols = tk.Listbox(self.f_vols_side, font=("Consolas", 9), bg="#FFFFFF", fg=WADA_TEXT_DARK,
                                       relief="flat", highlightthickness=1, highlightbackground=WADA_BG_MAIN, width=42)
        self.listbox_vols.pack(fill=tk.BOTH, expand=True, pady=5)
        self.listbox_vols.bind('<<ListboxSelect>>', self.on_select_flight_from_list)

        # ── BUSCADOR DE VOLS ──
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._filter_flights)
        search_frame = tk.Frame(self.f_vols_side, bg=WADA_BG_SIDEBAR)
        search_frame.pack(fill=tk.X, pady=(4, 2))
        tk.Label(search_frame, text="🔍", bg=WADA_BG_SIDEBAR).pack(side=tk.LEFT)
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="✕", width=2,
                   command=lambda: self.search_var.set("")).pack(side=tk.LEFT)




        self.f_map_side = tk.Frame(self.paned, bg=WADA_BG_MAIN, padx=5, pady=5)

        self.paned.add(self.f_vols_side, stretch="never")
        self.paned.add(self.f_map_side, stretch="always")

        ctrl_frame = tk.Frame(self.f_map_side, bg=WADA_BG_MAIN, pady=5)
        ctrl_frame.pack(fill=tk.X)

        ttk.Button(ctrl_frame, text="1a. Carregar Arribades", command=self.load_arrivals_v4).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="1b. Carregar Sortides i Fusionar", command=self.load_and_merge_v4).pack(
            side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="2. Auto-Assignar Cronograma", command=self.auto_assign_all_day).pack(side=tk.LEFT,
                                                                                                          padx=3)
        ttk.Button(ctrl_frame, text="3. Gràfica Ocupació 24h", command=self.show_v4_chart).pack(side=tk.LEFT, padx=3)

        sim_ctrl = tk.Frame(self.f_map_side, bg=WADA_BG_MAIN, pady=4)
        sim_ctrl.pack(fill=tk.X)
        self.clock_lbl = tk.Label(sim_ctrl, text="⏱ 08:00",
                                  font=("Segoe UI", 13, "bold"), bg=WADA_BG_MAIN, fg=WADA_ACCENT_BLUE)
        self.clock_lbl.pack(side=tk.LEFT, padx=8)
        ttk.Button(sim_ctrl, text="▶ Play", command=self.sim_play).pack(side=tk.LEFT, padx=3)
        ttk.Button(sim_ctrl, text="⏸ Pausa", command=self.sim_pause).pack(side=tk.LEFT, padx=3)
        ttk.Button(sim_ctrl, text="⏹ Reset", command=self.sim_reset).pack(side=tk.LEFT, padx=3)
        tk.Label(sim_ctrl, text="Velocitat:", bg=WADA_BG_MAIN).pack(side=tk.LEFT, padx=(12, 4))
        speed_slider = ttk.Scale(sim_ctrl, from_=1, to=20,
                                 variable=self.speed_var, orient=tk.HORIZONTAL, length=140)
        speed_slider.pack(side=tk.LEFT)
        self.speed_lbl = tk.Label(sim_ctrl, text="x1", bg=WADA_BG_MAIN, width=4)
        self.speed_lbl.pack(side=tk.LEFT)
        speed_slider.bind("<Motion>", lambda e: self.speed_lbl.config(text=f"x{self.speed_var.get()}"))

        self.stats_lbl = tk.Label(self.f_map_side, text="Estat: Esperant càrrega de dades d'arribades o sortides.",
                                  font=("Segoe UI", 10, "bold"), bg=WADA_BG_MAIN, fg=WADA_TEXT_DARK)
        self.stats_lbl.pack(pady=4)

        container = tk.Frame(self.f_map_side, bg=WADA_CANVAS_BG)
        container.pack(fill="both", expand=True, padx=5)

        self.canvas = tk.Canvas(container, bg=WADA_CANVAS_BG, highlightthickness=0)
        sb_y = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        sb_y.pack(side="right", fill="y")
        sb_x = tk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        sb_x.pack(side="bottom", fill="x")

        self.scroll_frame = tk.Frame(self.canvas, bg=WADA_CANVAS_BG)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=sb_x.set, yscrollcommand=sb_y.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.info_var = tk.StringVar(
            value="Instruccions: Controla el trànsit de l'aeroport de forma manual clicant portes o mitjançant el simulador de franges hores.")
        info_lbl = tk.Label(self.f_map_side, textvariable=self.info_var, bg=WADA_BG_SIDEBAR, fg=WADA_TEXT_DARK,
                            font=("Segoe UI", 10, "italic"), pady=8)
        info_lbl.pack(fill="x", pady=5)

        self.render_airport_layout()

    def refresh_flights_listbox(self):
        self.listbox_vols.delete(0, tk.END)
        target_list = self.cronograma_complet if self.cronograma_complet else aircrafts_list
        for ac in target_list:
            arr = getattr(ac, 'arrival', '')
            dep = getattr(ac, 'departure', '')
            lbl = f"✈ {ac.id} ["
            if arr: lbl += f"A:{arr}"
            if dep: lbl += f" D:{dep}"
            lbl += "]"
            self.listbox_vols.insert(tk.END, lbl)

    # ── MÈTODE FILTRE
    def _filter_flights(self, *args):
        query = self.search_var.get().upper().strip()
        self.listbox_vols.delete(0, tk.END)
        target_list = self.cronograma_complet if self.cronograma_complet else aircrafts_list
        for ac in target_list:
            arr = getattr(ac, 'arrival', '')
            dep = getattr(ac, 'departure', '')
            lbl = f"✈ {ac.id} ["
            if arr: lbl += f"A:{arr}"
            if dep: lbl += f" D:{dep}"
            lbl += "]"
            if query in ac.id.upper() or query in getattr(ac, 'airline', '').upper() or not query:
                self.listbox_vols.insert(tk.END, lbl)

    def on_select_flight_from_list(self, event):
        selection = self.listbox_vols.curselection()
        if not selection: return
        idx = selection[0]
        target_list = self.cronograma_complet if self.cronograma_complet else aircrafts_list
        if idx < len(target_list):
            ac = target_list[idx]
            msg = f"Aeronau: {ac.id} | Tipus: {getattr(ac, 'flight_type', 'Schengen')} | Codi Companyia: {ac.airline}\n"
            msg += f"Arribada: {getattr(ac, 'arrival', 'No té')} | Sortida: {getattr(ac, 'departure', 'No té')}"
            self.info_var.set(msg)

    def load_arrivals_v4(self):
        global aircrafts_list
        ruta = filedialog.askopenfilename(title="Seleccionar Fitxer d'Arribades (Arrivals.txt)",
                                          filetypes=[("Arxius de text", "*.txt")])
        if ruta:
            aircrafts_list = LoadArrivals(ruta)
            for a in aircrafts_list:
                if not hasattr(a, 'flight_type'): a.flight_type = "Schengen"
                if not hasattr(a, 'destination'): a.destination = ""
                if not hasattr(a, 'departure'): a.departure = ""
            print(f"V4: Arribades carregades directament ({len(aircrafts_list)} vols).")
            sound_load()
            self.info_var.set(
                f"S'han carregat {len(aircrafts_list)} arribades. Ara pots carregar les sortides per fusionar.")
            self.refresh_flights_listbox()

    def load_and_merge_v4(self):
        global aircrafts_list
        ruta = filedialog.askopenfilename(title="Seleccionar Fitxer de Sortides (Departures.txt)",
                                          filetypes=[("Arxius de text", "*.txt")])
        if ruta:
            sortides, err = LoadDepartures(ruta)
            if err == 0:
                for s in sortides:
                    if not hasattr(s, 'flight_type'): s.flight_type = "Schengen"
                    if not hasattr(s, 'origin'): s.origin = ""
                    if not hasattr(s, 'arrival'): s.arrival = ""

                if aircrafts_list:
                    for a in aircrafts_list:
                        if not hasattr(a, 'flight_type'): a.flight_type = "Schengen"
                        if not hasattr(a, 'destination'): a.destination = ""
                        if not hasattr(a, 'departure'): a.departure = ""

                    cronograma_net = []
                    sortides_actives = list(sortides)

                    for arr_ac in aircrafts_list:
                        arr_min = _time_to_minutes(arr_ac.arrival)
                        salida_vinculada = None

                        for dep_ac in sortides_actives:
                            if dep_ac.id == arr_ac.id:
                                dep_min = _time_to_minutes(dep_ac.departure)
                                if arr_min < dep_min:
                                    salida_vinculada = dep_ac
                                    break

                        if salida_vinculada:
                            arr_ac.destination = salida_vinculada.destination
                            arr_ac.departure = salida_vinculada.departure
                            sortides_actives.remove(salida_vinculada)
                        else:
                            mm_totals = arr_min + 60
                            hh = (mm_totals // 60) % 24
                            mm = mm_totals % 60
                            arr_ac.departure = f"{hh:02d}:{mm:02d}"
                            arr_ac.destination = "TEMP"

                        cronograma_net.append(arr_ac)

                    for dep_ac in sortides_actives:
                        dep_ac.origin = ""
                        dep_ac.arrival = ""
                        cronograma_net.append(dep_ac)

                    self.cronograma_complet = cronograma_net

                    for x in self.cronograma_complet:
                        if not hasattr(x, 'flight_type'): x.flight_type = "Schengen"
                        if not hasattr(x, 'origin'): x.origin = ""
                        if not hasattr(x, 'arrival'): x.arrival = ""
                        if not hasattr(x, 'departure'): x.departure = ""
                        if not hasattr(x, 'destination'): x.destination = ""

                    print(
                        f"V4: Fusió de rotacions feta. Total moviments reals independents: {len(self.cronograma_complet)}")
                    self.info_var.set(
                        f"Llistes fusionades mitjançant l'algorisme de rotació contínua. Total estades: {len(self.cronograma_complet)}")
                    sound_load()
                else:
                    self.cronograma_complet = sortides
                    self.info_var.set(
                        "Sortides carregades directament. Recorda carregar arribades primer per fer la fusió completa.")
                    sound_warning()

                self.refresh_flights_listbox()
                self.render_all_gates_colors()
            else:
                messagebox.showerror("Error", "Error llegint el fitxer de sortides.")
                sound_error()

    def auto_assign_all_day(self):
        if not self.cronograma_complet:
            messagebox.showwarning("Atenció", "Primer has de carregar les dades per fer l'auto-assignació.")
            return
        self.simulacio_activa = True
        self.cambios_manuales = {}
        self.sync_simulation_to_time()
        self.info_var.set("Simulació diària executada: Portes de de nit i franges de trànsit sincronitzades.")
        sound_sim_start()

    def sync_simulation_to_time(self):
        if not self.simulacio_activa:
            return

        current_time = self.hour_var.get()
        target_minutes = _time_to_minutes(current_time)

        for t in self.airport.terminals:
            for area in t.boarding_areas:
                for gate in area.gates:
                    gate.occupied = False
                    gate.aircraft_id = None

        nocturns = NightAircraft(self.cronograma_complet)
        if nocturns and nocturns != -1:
            AssignNightGates(self.airport, nocturns)

        sense_porta = 0
        for ac in self.cronograma_complet:
            arr_min = _time_to_minutes(ac.arrival) if ac.arrival != "" else -1
            dep_min = _time_to_minutes(ac.departure) if ac.departure != "" else -1

            if target_minutes == 0:
                if arr_min == -1 and dep_min > 0:
                    if dep_min == 0:
                        continue
                    trobat = False
                    for t in self.airport.terminals:
                        for area in t.boarding_areas:
                            for gate in area.gates:
                                if gate.aircraft_id == ac.id:
                                    gate.occupied = True
                                    trobat = True
                    if not trobat:
                        if AssignGate(self.airport, ac) == -1: sense_porta += 1
                continue

            if arr_min != -1 and dep_min != -1:
                if arr_min <= target_minutes and target_minutes < dep_min:
                    if AssignGate(self.airport, ac) == -1: sense_porta += 1

            elif arr_min == -1 and dep_min != -1:
                if target_minutes < dep_min:
                    trobat = False
                    for t in self.airport.terminals:
                        for area in t.boarding_areas:
                            for gate in area.gates:
                                if gate.aircraft_id == ac.id:
                                    gate.occupied = True
                                    trobat = True
                    if not trobat:
                        if AssignGate(self.airport, ac) == -1: sense_porta += 1
                else:
                    for t in self.airport.terminals:
                        for area in t.boarding_areas:
                            for gate in area.gates:
                                if gate.aircraft_id == ac.id:
                                    gate.occupied = False
                                    gate.aircraft_id = None

            elif arr_min != -1 and dep_min == -1:
                if arr_min <= target_minutes:
                    if AssignGate(self.airport, ac) == -1: sense_porta += 1

        for gate_name, aircraft_id in self.cambios_manuales.items():
            for t in self.airport.terminals:
                for area in t.boarding_areas:
                    for gate in area.gates:
                        if gate.name == gate_name:
                            if aircraft_id is None:
                                gate.occupied = False
                                gate.aircraft_id = None
                            else:
                                gate.occupied = True
                                gate.aircraft_id = aircraft_id

        self.render_all_gates_colors()

    def on_time_changed(self, event):
        if not self.cronograma_complet: return
        self.sync_simulation_to_time()

    def render_airport_layout(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.buttons_references = {}

        for terminal in self.airport.terminals:
            t_f = tk.Frame(self.scroll_frame, bg=WADA_CANVAS_BG, padx=15, pady=5)
            t_f.pack(side="left", fill="y")

            tk.Label(t_f, text=f"TERMINAL {terminal.name}", font=("Segoe UI", 12, "bold"), bg=WADA_CANVAS_BG,
                     fg=WADA_ACCENT_BLUE).pack(anchor="w", pady=(5, 0))
            tk.Frame(t_f, height=3, bg=WADA_ACCENT_BLUE).pack(fill="x", pady=4)

            p_f = tk.Frame(t_f, bg=WADA_CANVAS_BG)
            p_f.pack()

            for area in terminal.boarding_areas:
                a_f = tk.Frame(p_f, bg=WADA_CANVAS_BG, padx=8, pady=5)
                a_f.pack(side="left", anchor="n")

                lbl_restriccio = f"{area.name}\n({area.type})"
                tk.Label(a_f, text=lbl_restriccio, font=("Segoe UI", 9, "bold"), bg=WADA_ACCENT_BLUE,
                         fg=WADA_TEXT_LIGHT, justify="center", width=12, pady=4).pack(pady=(0, 6))

                grid = tk.Frame(a_f, bg=WADA_CANVAS_BG)
                grid.pack()

                for i, gate in enumerate(area.gates):
                    r, c = i // 2, (0 if i % 2 == 0 else 2)
                    btn = tk.Button(grid, text=gate.name.split("G")[-1], width=8, height=2,
                                    font=("Segoe UI", 7, "bold"), relief="flat",
                                    command=lambda t=terminal, a=area, g=gate: self._show_gate_agenda(g))
                    btn.grid(row=r, column=c, pady=2, padx=2)


                    self.buttons_references[gate.name] = btn
                    if c == 0: tk.Frame(grid, width=3, bg=WADA_ACCENT_BLUE).grid(row=r, column=1, sticky="ns")
        self.render_all_gates_colors()

    def render_all_gates_colors(self):
        total_gates = 0
        occupied_gates = 0

        for terminal in self.airport.terminals:
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    total_gates += 1
                    btn = self.buttons_references.get(gate.name)
                    if btn:
                        if gate.occupied and gate.aircraft_id:
                            occupied_gates += 1
                            btn.config(bg=WADA_GATE_OCCUPIED, text=f"{gate.name.split('G')[-1]}\n({gate.aircraft_id})")
                        else:
                            btn.config(bg=WADA_GATE_FREE, text=gate.name.split("G")[-1])

        free_gates = total_gates - occupied_gates
        current_time = self.hour_var.get()
        if self.simulacio_activa:
            self.stats_lbl.config(
                text=f"Hora: {current_time}  |  Portes Totals: {total_gates}  |  Ocupades: {occupied_gates}  |  Lliures: {free_gates}")
        else:
            self.stats_lbl.config(
                text=f"Estat: Cronograma carregat. Portes Totals: {total_gates}  |  Lliures: {total_gates}")

    # ── PANEL D'AGENDA DE PORTA (inserir a la línia 887, abans de manage_manual_gate) ──
    def _show_gate_agenda(self, gate):
        # Primer fem la gestió manual habitual
        self.manage_manual_gate(
            next((t for t in self.airport.terminals
                  for a in t.boarding_areas if gate in a.gates), None),
            next((a for t in self.airport.terminals
                  for a in t.boarding_areas if gate in a.gates), None),
            gate
        )
        # Ara obrim el panel lateral d'agenda
        if hasattr(self, '_agenda_win') and self._agenda_win and self._agenda_win.winfo_exists():
            self._agenda_win.destroy()

        self._agenda_win = tk.Toplevel(self.master)
        self._agenda_win.title(f"Agenda Porta {gate.name}")
        self._agenda_win.geometry("420x520")
        self._agenda_win.configure(bg=WADA_BG_MAIN)
        self._agenda_win.resizable(False, True)

        tk.Label(self._agenda_win,
                 text=f"📋 Agenda del dia — Porta {gate.name}",
                 font=("Segoe UI", 12, "bold"),
                 bg=WADA_BG_MAIN, fg=WADA_ACCENT_BLUE).pack(pady=(14, 4))

        tk.Frame(self._agenda_win, height=2, bg=WADA_ACCENT_BLUE).pack(fill="x", padx=14)

        frame_llista = tk.Frame(self._agenda_win, bg=WADA_BG_MAIN)
        frame_llista.pack(fill="both", expand=True, padx=14, pady=10)

        scrollbar = tk.Scrollbar(frame_llista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_agenda = tk.Text(frame_llista, font=("Consolas", 10), bg="#FDFCFA",
                              fg=WADA_TEXT_DARK, relief="flat", yscrollcommand=scrollbar.set,
                              padx=8, pady=8, wrap=tk.WORD)
        text_agenda.pack(fill="both", expand=True)
        scrollbar.config(command=text_agenda.yview)

        source = self.cronograma_complet if self.cronograma_complet else aircrafts_list
        vols_porta = [ac for ac in source if getattr(ac, 'assigned_gate', None) == gate.name]

        # Si no hi ha atribut assigned_gate, busquem per nom al gate actual
        if not vols_porta and gate.aircraft_id:
            vols_porta = [ac for ac in source if ac.id == gate.aircraft_id]

        if not vols_porta:
            text_agenda.insert(tk.END, "Cap vol assignat a aquesta porta avui.\n\n")
            text_agenda.insert(tk.END, "ℹ️ Executa 'Auto-Assignar Cronograma'\nper veure l'agenda completa.")
        else:
            vols_porta_sorted = sorted(
                vols_porta,
                key=lambda ac: _time_to_minutes(getattr(ac, 'arrival', '') or getattr(ac, 'departure', ''))
            )
            for ac in vols_porta_sorted:
                arr = getattr(ac, 'arrival', '—')
                dep = getattr(ac, 'departure', '—')
                ori = getattr(ac, 'origin', '—')
                dst = getattr(ac, 'destination', '—')
                now = self.hour_var.get()
                dep_min = _time_to_minutes(dep if dep != '—' else '')
                now_min = _time_to_minutes(now)
                estat = "✅ Completat" if dep_min != -1 and dep_min < now_min else "🟡 En curs / Pendent"
                text_agenda.insert(tk.END,
                                   f"{'─' * 35}\n"
                                   f"✈  {ac.id}  ({ac.airline})\n"
                                   f"   Arribada : {arr}   Sortida: {dep}\n"
                                   f"   Origen   : {ori}   Destí  : {dst}\n"
                                   f"   Estat    : {estat}\n\n"
                                   )

        text_agenda.config(state=tk.DISABLED)
        ttk.Button(self._agenda_win, text="Tancar",
                   command=self._agenda_win.destroy).pack(pady=10)

    def manage_manual_gate(self, terminal, area, gate):
        if gate.occupied:
            if messagebox.askyesno("Gestió Manual V4",
                                   f"Porta {gate.name} occupied per {gate.aircraft_id}.\nVols alliberar la porta manualment?"):
                self.cambios_manuales[gate.name] = None
                self.sync_simulation_to_time()
                if not self.simulacio_activa:
                    gate.occupied = False
                    gate.aircraft_id = None
                    self.render_all_gates_colors()
        else:
            f_id = simpledialog.askstring("Gestió Manual V4",
                                          "Introdueix el codi AIRCRAFT per forçar la seva assignació en aquesta porta:")
            if f_id:
                f_id = f_id.upper()

                target_list = self.cronograma_complet if self.cronograma_complet else aircrafts_list
                ac = next((x for x in target_list if x.id == f_id), None)

                if ac is None:
                    messagebox.showerror("Error de Validació",
                                         f"L'aeronau {f_id} no existeix a les dades de vols carregades per a avui.")
                    return

                if ac.airline not in terminal.airlines:
                    messagebox.showerror("Error de Validació",
                                         f"L'aerolínia {ac.airline} d'aquest vol no té permís per operar a la Terminal {terminal.name}.\n(Aquesta terminal només admits companyies del seu fitxer extern de configuració).")
                    return

                if ac.flight_type != area.type:
                    messagebox.showerror("Error de Validació",
                                         f"Restricció de Passaports: El vol {f_id} és de tipus {ac.flight_type}, però l'àrea {area.name} és exclusivament {area.type}.")
                    return

                self.cambios_manuales[gate.name] = f_id
                self.sync_simulation_to_time()
                if not self.simulacio_activa:
                    gate.occupied = True
                    gate.aircraft_id = f_id
                    self.render_all_gates_colors()

    def show_v4_chart(self):
        if not self.cronograma_complet:
            messagebox.showwarning("Atenció", "No hi ha un cronograma actiu per calcular la gràfica diària.")
            return

        chart_win = tk.Toplevel(self.master)
        chart_win.title("Gràfica d'Ocupació Diària per Hores (V4)")
        chart_win.geometry("750x450")
        chart_win.configure(bg="#FFFFFF")

        fig, ax = plt.subplots(figsize=(7, 4))
        hores = [f"{h:02d}:00" for h in range(24)]
        ocupades_t1 = []
        ocupades_t2 = []

        test_airport = create_lebl()
        for h_str in hores:
            AssignGatesAtTime(test_airport, self.cronograma_complet, h_str)
            t1_o = sum(1 for a in test_airport.terminals[0].boarding_areas for g in a.gates if g.occupied)
            t2_o = sum(1 for a in test_airport.terminals[1].boarding_areas for g in a.gates if g.occupied) if len(
                test_airport.terminals) > 1 else 0
            ocupades_t1.append(t1_o)
            ocupades_t2.append(t2_o)

        ax.bar(hores, ocupades_t1, label="Terminal T1", color=WADA_ACCENT_BLUE, alpha=0.9)
        ax.bar(hores, ocupades_t2, bottom=ocupades_t1, label="Terminal T2", color=WADA_GATE_OCCUPIED, alpha=0.9)
        ax.set_xticklabels(hores, rotation=45, ha='right', fontsize=8)
        ax.set_title("Evolució Dinàmica de Portes Assignades (24h)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Portes Ocupades")
        ax.legend()
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    def sim_play(self):
        if not self.cronograma_complet:
            messagebox.showwarning("Atenció", "Primer carrega el cronograma.")
            sound_warning()
            return
        self.simulacio_activa = True
        self.sim_running = True
        sound_sim_start()
        self._sim_tick()

    def sim_pause(self):
        self.sim_running = False
        if self._sim_job:
            self.master.after_cancel(self._sim_job)
            self._sim_job = None
        sound_sim_stop()

    def sim_reset(self):
        self.sim_pause()
        self.sim_minute = 0
        self.clock_lbl.config(text="⏱ 00:00")
        self.hour_var.set("00:00")
        self.sync_simulation_to_time()

    def _sim_tick(self):
        if not self.sim_running:
            return
        self.sim_minute = (self.sim_minute + 1) % 1440
        hh = self.sim_minute // 60
        mm = self.sim_minute % 60
        self.clock_lbl.config(text=f"⏱ {hh:02d}:{mm:02d}")
        self.hour_var.set(f"{hh:02d}:00")
        self.sync_simulation_to_time()
        interval = max(50, 800 // self.speed_var.get())
        self._sim_job = self.master.after(interval, self._sim_tick)


# AFEGIR A PARTIR DE LA LÍNIA 937:
class CarbonFootprintPanel:
    CO2_PER_KM = 5.0
    LEBL_LAT, LEBL_LON = 41.2971, 2.0785

    def __init__(self, master):
        self.master = master
        self._build_ui()

    def _build_ui(self):
        tk.Label(self.master, text="Emprempta de Carboni dels Vols",
                 font=("Segoe UI", 13, "bold"),
                 bg=WADA_BG_MAIN, fg=WADA_ACCENT_BLUE).pack(pady=(14, 6))

        # ── Fila de cerca per vol ──────────────────────────────────────────
        search_frame = tk.Frame(self.master, bg=WADA_BG_MAIN)
        search_frame.pack(pady=(0, 4))
        tk.Label(search_frame, text="Cercar vol (ID):",
                 bg=WADA_BG_MAIN, fg=WADA_ACCENT_BLUE,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var,
                 width=18, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(search_frame, text="Buscar",
                   command=self._search_flight).pack(side=tk.LEFT)

        # ── Botons principals ─────────────────────────────────────────────
        btn_frame = tk.Frame(self.master, bg=WADA_BG_MAIN)
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text="Top 20 Vols",
                   command=self._plot_by_flight).pack(side=tk.LEFT, padx=6)

        # Botó aerolínies + selector 10/20
        airline_frame = tk.Frame(btn_frame, bg=WADA_BG_MAIN)
        airline_frame.pack(side=tk.LEFT, padx=6)
        ttk.Button(airline_frame, text="Calcular per Aerolínia",
                   command=self._plot_by_airline).pack(side=tk.LEFT)
        tk.Label(airline_frame, text="Top:", bg=WADA_BG_MAIN,
                 fg=WADA_ACCENT_BLUE, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(6, 2))
        self.airline_top_var = tk.IntVar(value=10)
        ttk.Combobox(airline_frame, textvariable=self.airline_top_var,
                     values=[10, 20], width=4, state="readonly").pack(side=tk.LEFT)

        self.chart_frame = tk.Frame(self.master, bg="#FFFFFF")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

    # ── Càlcul d'emissions ────────────────────────────────────────────────
    def _compute_emissions(self):
        if not airports_list:
            messagebox.showwarning("Atenció", "Primer carrega els aeroports (Panell Trànsit).")
            return []
        source = v4_app.cronograma_complet if v4_app.cronograma_complet else aircrafts_list
        if not source:
            messagebox.showwarning("Atenció", "Primer carrega el cronograma de vols.")
            return []

        def find_ap(code):
            for ap in airports_list:
                if ap.icao == code:
                    return ap
            return None

        results = []
        for ac in source:
            origin_code = getattr(ac, 'origin', '')
            if not origin_code:
                continue
            ap = find_ap(origin_code)
            if ap is None:
                continue
            dist_km = HaversineDistance(ap.latitude, ap.longitude, self.LEBL_LAT, self.LEBL_LON)
            results.append((ac.id, ac.airline, dist_km * self.CO2_PER_KM))
        return results

    # ── Cerca per ID de vol ───────────────────────────────────────────────
    def _search_flight(self):
        query = self.search_var.get().strip().upper()
        if not query:
            messagebox.showwarning("Atenció", "Introdueix un ID de vol per cercar.")
            return
        data = self._compute_emissions()
        if not data:
            return
        matches = [(fid, airline, co2) for fid, airline, co2 in data
                   if query in fid.upper()]
        if not matches:
            messagebox.showinfo("Cerca", f"No s'ha trobat cap vol amb ID '{query}'.")
            return

        for w in self.chart_frame.winfo_children():
            w.destroy()
        plt.close('all')

        matches.sort(key=lambda x: x[2], reverse=True)
        fig, ax = plt.subplots(figsize=(8, max(3, len(matches) * 0.45)))
        colors = [WADA_GATE_OCCUPIED if i == 0 else WADA_ACCENT_BLUE
                  for i in range(len(matches))]
        ax.barh([d[0] for d in matches], [d[2] / 1000 for d in matches], color=colors)
        ax.set_xlabel("CO₂ estimat (tones)")
        ax.set_title(f"Resultats de cerca: '{query}' — {len(matches)} vol(s)")
        ax.invert_yaxis()
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ── Top 20 vols ───────────────────────────────────────────────────────
    def _plot_by_flight(self):
        data = self._compute_emissions()
        if not data:
            return
        data.sort(key=lambda x: x[2], reverse=True)
        top = data[:20]
        for w in self.chart_frame.winfo_children():
            w.destroy()
        plt.close('all')
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh([d[0] for d in top], [d[2] / 1000 for d in top],
                color=WADA_GATE_OCCUPIED)
        ax.set_xlabel("CO₂ estimat (tones)")
        ax.set_title("Top 20 vols per emprempta de carboni")
        ax.invert_yaxis()
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ── Gràfic per aerolínia (top 10 o 20) ───────────────────────────────
    def _plot_by_airline(self):
        data = self._compute_emissions()
        if not data:
            return
        totals = {}
        for _, airline, co2 in data:
            totals[airline] = totals.get(airline, 0) + co2 / 1000

        n = self.airline_top_var.get()          # 10 o 20
        airlines = sorted(totals, key=totals.get, reverse=True)[:n]

        for w in self.chart_frame.winfo_children():
            w.destroy()
        plt.close('all')
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(airlines, [totals[a] for a in airlines],
               color=WADA_ACCENT_BLUE, alpha=0.85)
        ax.set_xticklabels(airlines, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel("CO₂ total (tones)")
        ax.set_title(f"Top {n} aerolínies per emprempta de carboni")
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


carbon_panel = CarbonFootprintPanel(tab_carbon)

v4_app = V4UnifiedManager(tab_v4)
class ConnectionChecker:
    def __init__(self, master):
        self.master = master
        self._build_ui()

    def _build_ui(self):
        tk.Label(self.master, text="Verificador de Connexions",
                 font=("Segoe UI", 13, "bold"),
                 bg=WADA_BG_MAIN, fg=WADA_ACCENT_BLUE).pack(pady=(18, 8))

        form = tk.Frame(self.master, bg=WADA_BG_MAIN)
        form.pack(pady=6)

        labels = ["Vol d'arribada (ID):", "Vol de sortida (ID):"]
        self.entries = []
        for i, text in enumerate(labels):
            tk.Label(form, text=text, bg=WADA_BG_MAIN,
                     font=("Segoe UI", 10)).grid(row=i, column=0, sticky="e", padx=10, pady=6)
            e = ttk.Entry(form, width=20)
            e.grid(row=i, column=1, padx=10, pady=6)
            self.entries.append(e)

        ttk.Button(self.master, text="Comprovar connexió",
                   command=self._check).pack(pady=12)

        self.result_lbl = tk.Label(self.master, text="", bg=WADA_BG_MAIN,
                                   font=("Segoe UI", 11), justify="left",
                                   wraplength=600)
        self.result_lbl.pack(pady=10)

    def _check(self):
        arr_id = self.entries[0].get().strip().upper()
        dep_id = self.entries[1].get().strip().upper()

        # Busquem els vols a la llista global (o al cronograma si existeix)
        source = aircrafts_list
        arr_ac = next((a for a in source if a.id == arr_id and a.arrival), None)
        dep_ac = next((a for a in source if a.id == dep_id and a.departure), None)

        if not arr_ac:
            self.result_lbl.config(text=f"No s'ha trobat el vol d'arribada '{arr_id}'.", fg="#B04040")
            sound_error()
            return
        if not dep_ac:
            self.result_lbl.config(text=f"No s'ha trobat el vol de sortida '{dep_id}'.", fg="#B04040")
            sound_error()
            return

        res = CheckConnection(arr_ac, dep_ac, airports_list)
        if res is None:
            self.result_lbl.config(text="Dades de temps incompletes per a algun dels vols.", fg="#B04040")
            sound_warning()
            return

        passport_txt = "✔ Cal control de passaports (Schengen ↔ non-Schengen)" \
                       if res['requires_passport'] else "✔ Sense control de passaports (mateixa zona Schengen)"
        viable_txt   = "✅ CONNEXIÓ VIABLE" if res['viable'] else "❌ CONNEXIÓ INVIABLE"
        color        = "#2E6B3E" if res['viable'] else "#B04040"

        if res['viable']:
            sound_ok()
        else:
            sound_error()

        msg = (f"{viable_txt}\n\n"
               f"Arribada: {arr_ac.arrival}  |  Sortida: {dep_ac.departure}\n"
               f"Temps disponible: {(res['margin_min'] + res['min_required'])} min\n"
               f"Temps mínim requerit: {res['min_required']} min\n"
               f"Marge: {res['margin_min']:+d} min\n\n"
               f"{passport_txt}")
        self.result_lbl.config(text=msg, fg=color)


connection_checker = ConnectionChecker(tab_connection)


# ─── CONSOLA HISTORIAL INFERIOR BLINDADA (PROPAGACIÓ GEOMÈTRICA EMBED) ───
f_cons_container = tk.Frame(f_right, height=130, bg=WADA_BG_MAIN)
f_cons_container.pack(fill=tk.X, pady=(15, 0))
f_cons_container.pack_propagate(False)  # BLINDATGE TOTAL: El Matplotlib mai més deformarà el tamany d'aquest objecte

status_display = tk.Text(f_cons_container, bg="#FDFCFA", fg=WADA_TEXT_DARK, relief="flat", highlightthickness=1,
                         highlightbackground=WADA_BG_SIDEBAR, font=("Consolas", 10), padx=8, pady=8)
status_display.pack(fill=tk.BOTH, expand=True)
status_display.config(state=tk.DISABLED)

window.mainloop()