import matplotlib.pyplot as plt
import os
import math

class Aircraft:
    def __init__(self, id, origin, arrival, airline):
        self.id = id
        self.origin = origin
        self.arrival = arrival
        self.airline = airline

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
                    # Nota: Ajusta la inicialització segons la teva estructura de classe
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
    durant el dia (nombre d'avions per cada franja de una hora).
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
    airlines_vistes = [] # Llista per guardar les airlines (VLG...)

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
            contador.append(1) # Comencem el contador a 1
        i = i + 1

    # Fem la gràfica
    plt.figure(figsize=(12, 6))
    plt.bar(airlines_vistes, contador, color='skyblue', edgecolor='navy')

    plt.title("Vols per Airline")
    plt.xticks(rotation=90, fontsize=8)
    plt.tight_layout() # Per a què a l'eix x les aerolinies no s'amontonin
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
    #Rep una llista d'aeronaus i mostra un stacked bar plot amb el nombre de vols Schengen i no Schengen.
    #Si la llista és buida, mostra error i no dibuixa res.
    if len(aircrafts) == 0:
        print("Error: La llista d'aeronaus està buida. No es pot generar el gràfic.")
        return

    schengen = 0
    non_schengen = 0

    i = 0
    while i < len(aircrafts):
        origen = aircrafts[i].origin

        if IsSchengenAirport(origen):
            schengen = schengen + 1
        else:
            non_schengen = non_schengen + 1

        i = i + 1

    # Stacked bar plot
    categories = ["Flights to LEBL"]

    plt.figure(figsize=(8, 6))
    plt.bar(categories, [schengen], label="Schengen", color="steelblue")
    plt.bar(categories, [non_schengen], bottom=[schengen], label="Non-Schengen", color="orange")

    plt.title("Flights arriving to LEBL by type")
    plt.ylabel("Number of flights")
    plt.legend()
    plt.tight_layout()
    plt.show()

def MapFlights(aircrafts):
    #Mostra a Google Earth les trajectòries dels vols de la llista,de l'aeroport d'origen LEBL.
    #Mostra en diferents colors les trajectòries amb origen en un pais Schengen.

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
            # color diferent segons Schengen
            if IsSchengenAirport(ac.origin):
                color = "ff0000ff"   # vermell/blau segons format KML
            else:
                color = "ff00ff00"   # verd

            f.write('<Placemark>\n')
            f.write('<name>Route ' + ac.origin + ' - LEBL</name>\n')
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

    os.startfile("flights_map.kml")  # Funcionalitat perquè el mapa s'obri directament a l'app google earth, sinó s'hauria de descarregar i obrir el document manualment.

def HaversineDistance(lat1, lon1, lat2, lon2):
    #Calcula la distància Haversine entre dos punts de la Terra.
    # Les latituds i longituds estan en graus.
    # Retorna la distància en km.
    r = 6371  # radi mitjà de la Terra en km

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
    #Retorna una llista amb les aeronaus que arriben a LEBL des d'un aeroport a més de 2000 km de distància.
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
            distancia = (HaversineDistance(airport_origin.latitude,airport_origin.longitude,airport_bcn.latitude,airport_bcn.longitude))
            if distancia > 2000:
                llarga_distancia.append(ac)

        i = i + 1

    return llarga_distancia

if __name__ == "__main__":
    aircrafts = LoadArrivals("arrivals.txt")
    print("Nombre d'aeronaus carregades:", len(aircrafts))

    print("\n--- PlotArrivals ---")
    PlotArrivals(aircrafts)

    print("\n--- PlotAirlines ---")
    PlotAirlines(aircrafts)

    print("\n--- PlotFlightsType ---")
    PlotFlightsType(aircrafts)

    print("\n--- SaveFlights ---")
    SaveFlights(aircrafts, "output.txt")

    print("\n--- MapFlights ---")
    MapFlights(aircrafts)

    print("\n--- LongDistanceArrivals ---")
    long_flights = LongDistanceArrivals(aircrafts)

    print("Nombre de vols a més de 2000 km:", len(long_flights))
    i = 0
    while i < len(long_flights):
        ac = long_flights[i]
        print(ac.id, ac.origin, ac.arrival, ac.airline)
        i = i + 1

