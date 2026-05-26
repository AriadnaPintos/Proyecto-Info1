import matplotlib.pyplot as plt
import os
import math

class Aircraft:
    def __init__(self, id, origin, arrival, airline, destination="", departure=""):
        self.id = id
        self.origin = origin
        self.arrival = arrival
        self.airline = airline
        self.destination = destination  # Codi ICAO de l'aeroport de destinació (4 caràcters)
        self.departure = departure      # Hora de sortida de LEBL (format hh:mm)

def LoadArrivals(filename):
    '''
    Obre el fitxer amb el nom rebut i retorna una llista d'aeronaus
    inicialitzades amb les dades del fitxer.
    '''
    # Si el fitxer no existeix, retorna una llista buida
    if not os.path.exists(filename):
        return []

    llista_aircrafts = []

    try:
        with open(filename, 'r') as f:
            # Saltem la línia de la capçalera
            header = f.readline()

            for linia in f:
                parts = linia.strip().split()

                # Comprovem que la línia tingui l'estructura esperada (4 columnes)
                if len(parts) != 4:
                    continue

                id_codi, origen, hora_arribada, aerolinia = parts

                # Validem el format de l'hora (H:MM o HH:MM)
                try:
                    h_m = hora_arribada.split(':')
                    if len(h_m) != 2:
                        raise ValueError

                    hora = int(h_m[0])
                    minut = int(h_m[1])

                    if not (0 <= hora < 24 and 0 <= minut < 60):
                        raise ValueError
                except ValueError:
                    # Si l'hora no és correcta, ignorem la línia
                    continue

                # Només actualitzem els camps disponibles al fitxer
                try:
                    nova_aeronau = Aircraft(
                        id=id_codi,
                        origin=origen,
                        arrival=hora_arribada,
                        airline=aerolinia
                    )
                    llista_aircrafts.append(nova_aeronau)
                except Exception:
                    continue

    except Exception as e:
        print(f"Error en llegir el fitxer: {e}")
        return []

    return llista_aircrafts


def PlotArrivals(aircrafts):
    '''
    Rep una llista d'aeronaus i mostra un gràfic de la freqüència d'aterratges
    durant el dia (nombre d'avions per cada franja d'una hora).
    '''

    if not aircrafts:
        print("Error: La llista d'aeronaus està buida. No es pot generar el gràfic.")
        return

    # Inicialitzem un comptador per a cada hora del dia (0-23)
    comptador_hores = [0] * 24

    for ac in aircrafts:
        try:
            # Extraiem l'hora de l'atribut 'arrival'
            hora = int(ac.arrival.split(':')[0])
            if 0 <= hora < 24:
                comptador_hores[hora] += 1
        except (ValueError, AttributeError, IndexError):
            continue

    # Configuració del gràfic
    hores = list(range(24))

    plt.figure(figsize=(12, 6))
    plt.bar(hores, comptador_hores, color='skyblue', edgecolor='navy')

    plt.title('Freqüència d\'Aterratges a LEBL')
    plt.xlabel('Hora del Dia')
    plt.ylabel('Nombre d\'Aeronaus')
    plt.xticks(hores)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.show()

def SaveFlights(aircrafts, filename):
    '''
    Guarda la llista d'aeronaus en un fitxer de text nou. Recorre l'arxiu Arrivals.txt i si qualsevol camp està buit,
    el substitueix per un guió ("-") o per "00:00" en el cas de l'hora d'arribada.
    '''

    if len(aircrafts) == 0:
        print("Error: La llista de vols està buida.")
        return "Error"

    f = open(filename, 'w')
    f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")  # Capçalera de cada columna

    i = 0
    while i < len(aircrafts):
        ac = aircrafts[i]

        # Comprovació de cada criteri
        if ac.id == "":
            id_final = "-"
        else:
            id_final = ac.id

        if ac.origin == "":
            origin_final = "-"
        else:
            origin_final = ac.origin

        if ac.arrival == "":
            arrival_final = "00:00"
        else:
            arrival_final = ac.arrival

        if ac.airline == "":
            airline_final = "-"
        else:
            airline_final = ac.airline

        f.write(id_final + " " + origin_final + " " + arrival_final + " " + airline_final + "\n")

        i = i + 1

    f.close()
    print("Arxiu guardat!")


def PlotAirlines(aircrafts):
    '''
    Compta quants vols té cada aerolínia en la llista i mostra un gràfic de barres
    comparatiu amb el volum de vols per companyia.
    '''

    if len(aircrafts) == 0:
        print("Error: No hi ha avions pel gràfic.")
        return

    contador = []
    airlines_vistes = []  # Llista per guardar les airlines (VLG...)

    # Busquem si la airline ja està a la llista
    i = 0
    while i < len(aircrafts):
        airline_actual = aircrafts[i].airline
        encontrado = False
        j = 0
        while j < len(airlines_vistes):
            if airlines_vistes[j] == airline_actual:
                contador[j] = contador[j] + 1
                encontrado = True
            j = j + 1

        # Si després de mirar tota la llista NO l'hem trobat, l'afeguim a la llista
        if encontrado == False:
            airlines_vistes.append(airline_actual)
            contador.append(1)  # Comencem el contador a 1
        i = i + 1

    # Fem la gràfica
    plt.figure(figsize=(12, 6))
    plt.bar(airlines_vistes, contador, color='skyblue', edgecolor='navy')

    plt.title("Vols per Aerolínia")
    plt.xticks(rotation=90, fontsize=8)
    plt.tight_layout()  # Per a què a l'eix x les aerolinies no s'amontonin
    plt.show()

def IsSchengenAirport(icao):
    '''
    Retorna True si l'aeroport (segons el prefix ICAO del país) és Schengen.
    Si no, retorna False.
    '''
    prefix = icao[:2]

    schengen_prefixes = [
        "LE",  # Espanya
        "LF",  # França
        "ED",  # Alemanya
        "EH",  # Països Baixos
        "LI",  # Itàlia
        "LP",  # Portugal
        "EB",  # Bèlgica
        "LS",  # Suïssa
        "LO",  # Àustria
        "LK",  # Txèquia
        "LH",  # Hongria
        "EP",  # Polònia
        "LZ",  # Eslovàquia
        "LJ",  # Eslovènia
        "LD",  # Croàcia
        "LG",  # Grècia
        "ES",  # Suècia
        "EK",  # Dinamarca
        "EF",  # Finlàndia
        "EE",  # Estònia
        "EV",  # Letònia
        "EY",  # Lituània
        "LM",  # Malta
        "LU",  # Luxemburg
        "EN",  # Noruega
        "BI"   # Islàndia
    ]

    if prefix in schengen_prefixes:
        return True
    else:
        return False

def PlotFlightsType(aircrafts):
    '''
    Rep una llista d'avions on mostra un gràfic (plot) amb el nombre de vols Schengen
    i els no Schengen. Si la llista és buida, mostra un error i no dibuixa res.
    Utilitza els paràmetres:
        aircrafts : list
            [Llista d'objectes d'aeronaus (cada una ha de tenir l'atribut '.origin'
            amb el codi ICAO de l'aeroport de sortida)].
    Retorna: None
        [No retorna cap valor, mostra el gràfic directament a la pantalla].
    '''

    if len(aircrafts) == 0:
        print("Error: La llista d'aeronaus està buida. No es pot generar el gràfic.")
        return

    schengen = 0
    no_schengen = 0

    i = 0
    while i < len(aircrafts):
        origen = aircrafts[i].origin

        if IsSchengenAirport(origen):
            schengen = schengen + 1
        else:
            no_schengen = no_schengen + 1

        i = i + 1

    # Gràfic de barres apilades
    categories = ["Vols a LEBL"]

    plt.figure(figsize=(8, 6))
    plt.bar(categories, [schengen], label="Schengen", color="steelblue")
    plt.bar(categories, [no_schengen], bottom=[schengen], label="No Schengen", color="orange")

    plt.title("Vols amb destinació LEBL per tipus")
    plt.ylabel("Nombre de vols")
    plt.legend()
    plt.tight_layout()
    plt.show()

def MapFlights(aircrafts):
    '''
    Genera un arxiu KML per mostrar a un mapa de Google Earth les trajectòries
    dels vols amb destinació LEBL (Barcelona), diferenciant amb colors les rutes
    depenent si pertanyen a l'espai Schengen o no.
    Utilitza els següents paràmetres:
        aircrafts (list): Llista d'objectes d'aeronaus (cada una ha de tenir
                          l'atribut '.origin' amb el codi ICAO de l'aeroport de sortida).
    Retorna:
        None. No retorna cap valor, genera el fitxer 'flights_map.kml' en el disc
        i l'obre automàticament.
    '''
    # Mostra a Google Earth les trajectòries dels vols de la llista, de l'aeroport d'origen a LEBL.
    # Mostra en diferents colors les trajectòries amb origen en un país Schengen.

    if len(aircrafts) == 0:
        print("Error: La llista d'aeronaus està buida.")
        return

    try:
        from airport import LoadAirports
    except ImportError:
        print("Error: No s'ha pogut importar airport.py")
        return

    airports = LoadAirports("airports.txt")

    if len(airports) == 0:
        print("Error: No s'han pogut carregar els aeroports.")
        return

    def FindAirport(code, airports):
        i = 0
        while i < len(airports):
            if airports[i].icao == code:
                return airports[i]
            i = i + 1
        return None

    airport_bcn = FindAirport("LEBL", airports)

    if airport_bcn == None:
        print("Error: No s'ha trobat LEBL al fitxer d'aeroports.")
        return

    f = open("flights_map.kml", "w", encoding="utf-8")

    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')

    i = 0
    while i < len(aircrafts):
        ac = aircrafts[i]
        airport_origin = FindAirport(ac.origin, airports)

        if airport_origin != None:
            # Color diferent segons Schengen
            if IsSchengenAirport(ac.origin):
                color = "ff0000ff"   # Blau (format KML)
            else:
                color = "ff00ff00"   # Verd

            f.write('<Placemark>\n')
            f.write('<name>Ruta ' + ac.origin + ' - LEBL</name>\n')
            f.write('<Style>\n')
            f.write('<LineStyle>\n')
            f.write('<color>' + color + '</color>\n')
            f.write('<width>2</width>\n')
            f.write('</LineStyle>\n')
            f.write('</Style>\n')
            f.write('<LineString>\n')
            f.write('<altitudeMode>clampToGround</altitudeMode>\n')
            f.write('<extrude>1</extrude>\n')
            f.write('<tessellate>1</tessellate>\n')
            f.write('<coordinates>\n')
            f.write(str(airport_origin.longitude) + ',' + str(airport_origin.latitude) + '\n')
            f.write(str(airport_bcn.longitude) + ',' + str(airport_bcn.latitude) + '\n')
            f.write('</coordinates>\n')
            f.write('</LineString>\n')
            f.write('</Placemark>\n')

        i = i + 1

    f.write('</Document>\n')
    f.write('</kml>\n')
    f.close()

    print("Arxiu flights_map.kml creat correctament.")

    os.startfile("flights_map.kml")  # Obre el mapa directament a l'aplicació Google Earth.

def HaversineDistance(lat1, lon1, lat2, lon2):
    '''
    Calcula la distància geodèsica de Haversine entre dos punts de la Terra.
    Utilitza els següents paràmetres:
        lat1 (float): Latitud del primer punt en graus.
        lon1 (float): Longitud del primer punt en graus.
        lat2 (float): Latitud del segon punt en graus.
        lon2 (float): Longitud del segon punt en graus.
    Retorna:
        float: La distància calculada entre els dos punts expressada en quilòmetres (km).
    '''
    # Calcula la distància Haversine entre dos punts de la Terra.
    # Les latituds i longituds estan en graus.
    # Retorna la distància en km.
    r = 6371  # Radi mitjà de la Terra en km

    # Convertim a radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    lambda1 = math.radians(lon1)
    lambda2 = math.radians(lon2)

    delta_phi = abs(phi1 - phi2)
    delta_lambda = abs(lambda1 - lambda2)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    d = r * c
    return d


def LongDistanceArrivals(aircrafts):
    '''
    Filtra i retorna una llista amb les aeronaus que tenen el seu aeroport
    d'origen a una distància superior a 2000 km respecte a Barcelona (LEBL).
    Utilitza la fórmula de Haversine per calcular la distància geodèsica
    entre les coordenades dels aeroports.
    Utilitza els següents paràmetres:
        aircrafts (list): Llista d'objectes d'aeronaus (cada una ha de tenir
                          l'atribut '.origin' amb el codi ICAO de l'aeroport de sortida).
    Retorna una llista que conté només els objectes d'aeronaus que superen
    els 2000 km de distància, o una llista buida [] en cas d'error o no haver-hi coincidències.
    '''
    # Retorna una llista amb les aeronaus que arriben a LEBL des d'un aeroport a més de 2000 km de distància.
    if len(aircrafts) == 0:
        return []

    try:
        from airport import LoadAirports
    except ImportError:
        print("Error: No s'ha pogut importar airport.py")
        return []

    airports = LoadAirports("airports.txt")

    if len(airports) == 0:
        print("Error: No s'han pogut carregar els aeroports.")
        return []

    def FindAirport(code, airports):
        i = 0
        while i < len(airports):
            if airports[i].icao == code:
                return airports[i]
            i = i + 1
        return None

    airport_bcn = FindAirport("LEBL", airports)

    if airport_bcn == None:
        print("Error: No s'ha trobat LEBL al fitxer d'aeroports.")
        return []

    llarga_distancia = []

    i = 0
    while i < len(aircrafts):
        ac = aircrafts[i]
        airport_origin = FindAirport(ac.origin, airports)

        if airport_origin != None:
            distancia = HaversineDistance(
                airport_origin.latitude, airport_origin.longitude,
                airport_bcn.latitude, airport_bcn.longitude
            )
            if distancia > 2000:
                llarga_distancia.append(ac)

        i = i + 1

    return llarga_distancia

def LoadDepartures(filename):
    '''
    Obre el fitxer amb el nom rebut, que conté informació de sortides,
    i retorna una llista d'objectes Aircraft inicialitzats amb les dades
    de sortida trobades al fitxer (destinació, hora de sortida i aerolínia).
    Els camps relacionats amb les arribades (origin, arrival) es deixen
    com a cadenes buides perquè no estan presents al fitxer de sortides.
    Si el fitxer no existeix, la funció retorna una llista buida i el
    codi d'error -1 com a tupla: ([], -1).
    El format esperat del fitxer és:
        AIRCRAFT  DESTINATION  DEPARTURE  AIRLINE
        ECMKV     LYBE         00:04      VLG
    '''
    if not os.path.exists(filename):
        return [], -1

    llista_sortides = []

    try:
        with open(filename, 'r') as f:
            f.readline()  # Saltem la línia de la capçalera

            for linia in f:
                parts = linia.strip().split()

                # Una línia de sortida vàlida té exactament 4 columnes; ignorem les mal formades
                if len(parts) != 4:
                    continue

                id_codi, destinacio, hora_sortida, aerolinia = parts

                # Validem el format de l'hora (H:MM o HH:MM)
                try:
                    h_m = hora_sortida.split(':')
                    if len(h_m) != 2:
                        raise ValueError
                    hora = int(h_m[0])
                    minut = int(h_m[1])
                    if not (0 <= hora < 24 and 0 <= minut < 60):
                        raise ValueError
                except ValueError:
                    continue

                # Creem un Aircraft només amb els camps de sortida emplenats
                nova_aeronau = Aircraft(
                    id=id_codi,
                    origin="",
                    arrival="",
                    airline=aerolinia,
                    destination=destinacio,
                    departure=hora_sortida
                )
                llista_sortides.append(nova_aeronau)

    except Exception as e:
        print(f"Error en llegir el fitxer de sortides: {e}")
        return [], -1

    return llista_sortides, 0


def _time_to_minutes(t):
    '''Auxiliar: converteix una cadena "HH:MM" o "H:MM" a minuts totals (int).
    Retorna -1 si la cadena és buida o té un format incorrecte.'''
    if not t:
        return -1
    try:
        h, m = t.split(':')
        return int(h) * 60 + int(m)
    except Exception:
        return -1


def MergeMovements(arrivals, departures):
    '''
    Rep dues llistes d'objectes Aircraft (arribades i sortides) i
    retorna una llista fusionada on les aeronaus que comparteixen el mateix id
    i tenen temps compatibles (arribada estrictament abans de la sortida)
    es combinen en una única estructura Aircraft amb les dades d'ambdós moviments.

    Les aeronaus que només apareixen a la llista d'arribades mantenen els camps
    de sortida buits (""). Les aeronaus que només apareixen a la llista de sortides
    (aeronaus nocturnes o sense arribada coincident) mantenen els camps d'arribada
    buits ("").

    Una aeronau pot aterrar i enlairar-se MÉS D'UNA VEGADA a LEBL durant el mateix dia.
    Cada arribada s'aparella, doncs, amb la sortida cronològicament més propera
    i posterior que encara no hagi estat assignada.

    Retorna ([], -1) si qualsevol de les llistes d'entrada és buida.
    Retorna la llista fusionada en cas contrari.
    '''
    if not arrivals or not departures:
        return [], -1

    # Construïm una còpia de treball de les sortides amb un indicador "used"
    # perquè cada entrada de sortida només es consumeixi una vegada.
    dep_pool = []
    for d in departures:
        dep_pool.append({'ac': d, 'used': False})

    merged = []

    # --- Passada 1: aparellem cada arribada amb la seva millor sortida ---
    for arr in arrivals:
        arr_min = _time_to_minutes(arr.arrival)

        # Cerquem la sortida no usada més primerenca amb el mateix id i amb
        # hora de sortida estrictament posterior a l'hora d'arribada.
        best_idx = -1
        best_dep_min = 99999
        for idx, entry in enumerate(dep_pool):
            if entry['used']:
                continue
            dep_ac = entry['ac']
            if dep_ac.id != arr.id:
                continue
            dep_min = _time_to_minutes(dep_ac.departure)
            if dep_min < 0:
                continue
            if arr_min >= 0 and dep_min > arr_min and dep_min < best_dep_min:
                best_dep_min = dep_min
                best_idx = idx

        if best_idx >= 0:
            dep_pool[best_idx]['used'] = True
            dep_ac = dep_pool[best_idx]['ac']
            combinat = Aircraft(
                id=arr.id,
                origin=arr.origin,
                arrival=arr.arrival,
                airline=arr.airline,
                destination=dep_ac.destination,
                departure=dep_ac.departure
            )
        else:
            # No s'ha trobat cap sortida coincident – conservem només les dades d'arribada
            combinat = Aircraft(
                id=arr.id,
                origin=arr.origin,
                arrival=arr.arrival,
                airline=arr.airline,
                destination="",
                departure=""
            )
        merged.append(combinat)

    # --- Passada 2: afegim les sortides no aparellades (aeronaus nocturnes o sense coincidència) ---
    for entry in dep_pool:
        if not entry['used']:
            dep_ac = entry['ac']
            nocturna = Aircraft(
                id=dep_ac.id,
                origin="",
                arrival="",
                airline=dep_ac.airline,
                destination=dep_ac.destination,
                departure=dep_ac.departure
            )
            merged.append(nocturna)

    return merged


def NightAircraft(aircrafts):
    '''
    Rep una llista d'objectes Aircraft i retorna una nova llista que conté
    només aquelles aeronaus que NO tenen informació d'arribada (origin i arrival
    són cadenes buides) però SÍ tenen informació de sortida.
    Aquestes són aeronaus que han passat la nit a l'aeroport i surten durant el dia
    sense un vol d'entrada corresponent a l'horari.

    Retorna ([], -1) si la llista d'entrada és buida.
    '''
    if not aircrafts:
        return [], -1

    llista_nocturnes = []
    for ac in aircrafts:
        sense_arribada = (ac.origin == "" and ac.arrival == "")
        te_sortida = (ac.destination != "" or ac.departure != "")
        if sense_arribada and te_sortida:
            llista_nocturnes.append(ac)

    return llista_nocturnes


if __name__ == "__main__":
    # ── Proves originals ─────────────────────────────────────────────────────
    arrivals = LoadArrivals("Arrivals.txt")
    print("Nombre d'aeronaus carregades (arribades):", len(arrivals))

    print("\n--- PlotArrivals ---")
    PlotArrivals(arrivals)

    print("\n--- PlotAirlines ---")
    PlotAirlines(arrivals)

    print("\n--- PlotFlightsType ---")
    PlotFlightsType(arrivals)

    print("\n--- SaveFlights ---")
    SaveFlights(arrivals, "output.txt")

    print("\n--- LongDistanceArrivals ---")
    vols_llarga_distancia = LongDistanceArrivals(arrivals)
    print("Nombre de vols a més de 2000 km:", len(vols_llarga_distancia))
    for ac in vols_llarga_distancia:
        print(ac.id, ac.origin, ac.arrival, ac.airline)

    # ── Noves proves ─────────────────────────────────────────────────────────
    SEP = "=" * 65

    # --- LoadDepartures ---
    print(f"\n{SEP}")
    print("PROVA – LoadDepartures")
    print(SEP)

    departures, err = LoadDepartures("Departures.txt")
    if err == -1:
        print("  ERROR: No s'ha pogut carregar Departures.txt")
    else:
        print(f"  Sortides carregades: {len(departures)}")
        # Mostrem les primeres 5 entrades
        for ac in departures[:5]:
            print(f"  {ac.id:10s}  dest={ac.destination:4s}  sortida={ac.departure:5s}  aerolinia={ac.airline}")

    # Cas especial: fitxer que no existeix
    resultat, codi = LoadDepartures("fitxer_inexistent.txt")
    print(f"\n  Fitxer inexistent → llista={resultat}, codi={codi}  (esperat [], -1)")

    # --- MergeMovements ---
    print(f"\n{SEP}")
    print("PROVA – MergeMovements")
    print(SEP)

    # Cas d'error: llista buida
    merged_err, codi = MergeMovements([], departures)
    print(f"  Arribades buides     → codi={codi}  (esperat -1)")
    merged_err, codi = MergeMovements(arrivals, [])
    print(f"  Sortides buides      → codi={codi}  (esperat -1)")

    # Fusió normal
    merged = MergeMovements(arrivals, departures)
    print(f"\n  Total de registres fusionats : {len(merged)}")

    # Comptem quants tenen tant arribada com sortida
    ambdos = [ac for ac in merged if ac.arrival != "" and ac.departure != ""]
    nomes_arr = [ac for ac in merged if ac.arrival != "" and ac.departure == ""]
    nomes_dep = [ac for ac in merged if ac.arrival == "" and ac.departure != ""]
    print(f"  Amb arribada i sortida       : {len(ambdos)}")
    print(f"  Només arribada               : {len(nomes_arr)}")
    print(f"  Només sortida (nocturnes)    : {len(nomes_dep)}")

    # Comprovació puntual: N327UP hauria d'aparèixer dues vegades (dues rotacions)
    n327 = [ac for ac in merged if ac.id == "N327UP"]
    print(f"\n  Registres N327UP (esperats 2 rotacions): {len(n327)}")
    for ac in n327:
        print(f"    arr={ac.arrival:5s}  dep={ac.departure:5s}  "
              f"origen={ac.origin:4s}  dest={ac.destination:4s}")

    # Verifiquem l'ordre temporal: tot registre amb ambdós temps ha de tenir
    # l'arribada abans de la sortida
    incorrectes = [ac for ac in ambdos
                   if _time_to_minutes(ac.arrival) >= _time_to_minutes(ac.departure)]
    print(f"\n  Registres on arr >= dep (hauria de ser 0): {len(incorrectes)}")

    # --- NightAircraft ---
    print(f"\n{SEP}")
    print("PROVA – NightAircraft")
    print(SEP)

    # Cas d'error: entrada buida
    nocturnes_err, codi = NightAircraft([])
    print(f"  Llista buida → codi={codi}  (esperat -1)")

    nocturnes = NightAircraft(merged)
    print(f"\n  Aeronaus nocturnes trobades: {len(nocturnes)}")
    for ac in nocturnes[:10]:   # Mostrem fins a 10 exemples
        print(f"  {ac.id:10s}  dest={ac.destination:4s}  sortida={ac.departure:5s}  aerolinia={ac.airline}")