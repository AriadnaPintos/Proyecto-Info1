import os
#Definim les classes
class BarcelonaAP: #Contindrà un codi i una llista d'objectes de la classe Terminal
    def __init__(self, code):
        self.code = code
        self.terminals = []

class Terminal: # contindrà una llista d'objectes de la classe BoardingArea i una altre llista amb els codis ICAO
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.airlines = []  # Llista de codis ICAO

class BoardingArea: #
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type  # 'Schengen' o 'non-Schengen'
        self.gates = []

class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = None


def SetGates(area, init_gate, end_gate, prefix):
    """
    Inicialitza les portes d'una àrea amb un rang numèric específic.

    Elimina les portes existents a l'àrea i en crea de noves combinant el
    prefix amb els números del rang des de 'init_gate' fins a 'end_gate' (inclòs).
    Utilitza els següents paràmetres:
        area : L'objecte àrea on s'afegiran les portes.
        init_gate (int): Número de la primera porta.
        end_gate (int): Número de l'última porta.
        prefix (str): Text que precedirà el número de cada porta.

    Retorna 0 si s'ha executat correctament, -1 si el rang no és vàlid.
    """
    if end_gate <= init_gate:
        return -1

    area.gates = []  # Buidem la llista prèvia
    for i in range(init_gate, end_gate + 1):
        gate_name = f"{prefix}{i}"
        new_gate = Gate(gate_name)
        area.gates.append(new_gate)
    return 0


def LoadAirlines(terminal, t_name):
    """
    Carrega les línies aèries de la terminal des d'un fitxer de text.

    Neteja la llista existent a la terminal i llegeix un fitxer anomenat
    '{t_name}_Airlines.txt'. De cada línia (separada per tabuladors),
    extreu i afegeix el codi ICAO a la termial.

    Utilitza:
        terminal (Terminal) : Objecte terminal on es desaran les línies aèries
        t_name (str): Nom de la terminal per localitzar el fitxer corresponent
    com a paràmetres

    Retorna 0 si s'ha carregat correctament, -1 si el fitxer no existeix.
    """
    fitxer = f"{t_name}_Airlines.txt"
    if not os.path.exists(fitxer):
        return -1

    terminal.airlines = [] # Buidem la llista prèvia
    f_terminal=open(fitxer, "r")
    line=f_terminal.readlines()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            # Afegim només el codi ICAO (la segona columna)
            terminal.airlines.append(parts[1])
        return 0
    f_terminal.close()

def LoadAirportStructure(filename):
    """
    Carrega l'estructura completa d'un aeroport a partir d'un fitxer de text.

    Llegeix la configuració de l'aeroport (Terminals -> Àrees de l'aeroport -> Portes)
    i construeix l'objecte 'BarcelonaAP' (utilitzant la classe creada anteriorment) corresponent, enllaçant també les aerolínies
    de cada terminal mitjançant fitxers externs.

    L'estructura esperada del fitxer és:
        - 1a línia: Codi_Aeroport Num_Terminals
        - Per cada terminal: Terminal Nom_Terminal Num_Àrees
        - Per cada àrea: Area Nom_Àrea Tipus_Àrea Gates Inici - Final
    El paràmetre que s'utilitza és:
        filename (str): Ruta del fitxer de text amb l'estructura de l'aeroport.

    Retorna o bé BarcelonaAP: L'objecte aeroport instanciat i complet, o bé -1 si el fitxer no existeix.
    """
    if not os.path.exists(filename):
        return -1

    f_load=open(filename, "r")
        # Primera línia: LEBL 2 terminals
    codi = f_load.readline().split()
    airport = BarcelonaAP(codi[0])
    num_terminals = int(codi[1])

    for _ in range(num_terminals):
        # Línia terminal: Terminal T1 5 boarding areas
        t_line = f.readline().split()
        t_name = t_line[1]
        num_areas = int(t_line[2])

        terminal = Terminal(t_name)
        # Carreguem aerolínies des del fitxer extern
        LoadAirlines(terminal, t_name)

        for _ in range(num_areas):
            # Línia àrea: Area A Schengen Gates 1 - 11
            a_line = f.readline().split()
            a_name = a_line[1]
            a_type = a_line[2]
            g_start = int(a_line[4])
            g_end = int(a_line[6])

            area = BoardingArea(a_name, a_type)
            # El prefix serà el nom de la terminal + nom de l'àrea (ex: T1A)
            prefix = f"{t_name}{a_name}"
            SetGates(area, g_start, g_end, prefix)

            terminal.boarding_areas.append(area)

        airport.terminals.append(terminal)
    f_load.close()
    return airport


def GateOccupancy(bcn):
    """
    Donada bcn de la classe BarcelonaAP, retorna una llista de tuples amb
    (nom_porta, estat, id_aeronau) per a totes les portes de l'aeroport.
    estat és 'occupied' o 'free'; id_aeronau és None si la porta és lliure.
    """
    result = []
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                status = 'occupied' if gate.occupied else 'free'
                result.append((gate.name, status, gate.aircraft_id))
    return result

def IsAirlineInTerminal(terminal, name):
    """
    Comprova si una aerolínia específica opera en una terminal donada.

    Paràmetres
        terminal (Terminal): Objecte terminal on es farà la cerca.
        name (str): Codi ICAO de l'aerolínia que es vol buscar.

    Retorna:
            - True si l'aerolínia es troba a la llista de la terminal.
            - False si no hi és o si la llista d'aerolínies està buida.
            - (False, -1) si el paràmetre 'name' està buit
    """
    #Donada una terminal i el nom (codi ICAO) d'una aerolínia, retorna True si l'aerolínia opera en aquesta terminal,False altrament.
    # Retorna (False, -1) si name és una cadena buida.
    # Retorna False si la llista d'aerolínies de la terminal és buida.
    if name == "":
        return False, -1  # Error: nom nul

    if not terminal.airlines:
        return False  # Llista buida

    return name in terminal.airlines


def SearchTerminal(bcn, name):
    """
    Cerca la terminal assignada a una aerolínia de l'aeroport.

    Recorre les terminals de l'aeroport de Barcelona i utilitza la funció
    'IsAirlineInTerminal' per comprovar on opera l'aerolínia indicada.

    Els paràmetres que utilitza son:.
        bcn (BarcelonaAP): L'objecte aeroport que conté les terminals.
        name (str): Codi ICAO de l'aerolínia que es vol buscar.

    Retorna: El nom de la terminal on opera (ex: 'T1') o una cadena buida ('')
    si l'aerolínia no es troba o si el codi no és vàlid.
    """

    #Donada bcn de la classe BarcelonaAP i el nom (codi ICAO) d'una aerolínia,retorna el nom de la terminal on ha d'embarcar.
    # Utilitza IsAirlineInTerminal. Retorna '' si no es troba l'aerolínia.
    for terminal in bcn.terminals:
        found = IsAirlineInTerminal(terminal, name)
        # IsAirlineInTerminal pot retornar (False, -1) en cas d'error
        if found is True:
            return terminal.name
    return ''


def AssignGate(bcn, aircraft):
    """
    Assigna de forma automàtica una porta d'embarcar lliure a un avió.

    El procés d'assignació que segueix té passos:
        1. Identifica la terminal on opera l'aerolínia de l'avió.
        2. Busca les àrees d'embarcament d'aquella terminal que coincideixin amb
           el tipus de vol (ex: 'Schengen' o 'No-Schengen').
        3. Busca la primera porta disponible d'aquella àrea, la marca com a
           ocupada i hi vincula l'identificador de l'avió.

    Els paràmetres usats son:
        bcn (BarcelonaAP): L'objecte aeroport que conté l'estructura de terminals.
        aircraft (Aircraft): L'objecte avió que necessita la porta (conté 'airline',
                             'flight_type' i 'id').

    Retorna 0 si l'assignació s'ha realitzat amb èxit, -1 si l'aerolínia no és vàlida
    o si no hi ha cap porta lliure disponible per a aquest tipus de vol.
    """

    #Donada bcn de la classe BarcelonaAP i un objecte aircraft de la classe
    # Aircraft, busca la primera porta lliure de l'àrea correcta i l'assigna.
    # Actualitza occupied i aircraft_id de la porta triada dins bcn.
    # Retorna 0 si l'assignació ha estat correcta, -1 si no hi ha portes lliures.

    # 1. Trobar la terminal de l'aerolínia
    terminal_name = SearchTerminal(bcn, aircraft.airline)
    if terminal_name == '':
        return -1  # Aerolínia no trobada a cap terminal

    # 2. Localitzar la terminal dins bcn
    target_terminal = None
    for terminal in bcn.terminals:
        if terminal.name == terminal_name:
            target_terminal = terminal
            break

    if target_terminal is None:
        return -1

    # 3. Buscar la primera porta lliure a l'àrea del tipus correcte
    for area in target_terminal.boarding_areas:
        if area.type == aircraft.flight_type:
            for gate in area.gates:
                if not gate.occupied:
                    gate.occupied = True
                    gate.aircraft_id = aircraft.id
                    return 0  # Assignació correcta

    return -1  # No hi ha portes lliures del tipus correcte


# ── Classe Aircraft (necessària per a AssignGate) ─────────────────────────────

class Aircraft:

    #Representa una aeronau que vol aterrar.
    # id          – identificador de l'aeronau (p.ex. 'DALEN')
    # airline     – codi ICAO de l'aerolínia (p.ex. 'VLG')
    # flight_type – 'Schengen' o 'non-Schengen'


    def __init__(self, aircraft_id, airline, flight_type):
        self.id = aircraft_id
        self.airline = airline
        self.flight_type = flight_type


#Secció de test

if __name__ == "__main__":

    # Construcció manual d'un aeroport petit per als tests
    # (no depèn dels fitxers .txt per poder executar el test sense ells)

    airport = BarcelonaAP("LEBL")

    # Terminal T1
    t1 = Terminal("T1")
    t1.airlines = ["VLG", "IBE", "RYR"]  # Codis ICAO de prova

    area_a = BoardingArea("A", "Schengen")
    SetGates(area_a, 1, 5, "T1A")  # Portes T1A1 .. T1A5

    area_d = BoardingArea("D", "non-Schengen")
    SetGates(area_d, 1, 3, "T1D")  # Portes T1D1 .. T1D3

    t1.boarding_areas = [area_a, area_d]
    airport.terminals.append(t1)

    # Terminal T2
    t2 = Terminal("T2")
    t2.airlines = ["AFL", "DAH"]  # Codis ICAO de prova

    area_m = BoardingArea("M", "Schengen")
    SetGates(area_m, 1, 3, "T2M")  # Portes T2M1 .. T2M3

    area_w = BoardingArea("W", "non-Schengen")
    SetGates(area_w, 40, 42, "T2W")  # Portes T2W40 .. T2W42

    t2.boarding_areas = [area_m, area_w]
    airport.terminals.append(t2)

    print("=" * 60)
    print("TEST 1 – GateOccupancy (totes lliures inicialment)")
    print("=" * 60)
    occupancy = GateOccupancy(airport)
    for entry in occupancy:
        print(f"  Porta: {entry[0]:12s}  Estat: {entry[1]:9s}  Aeronau: {entry[2]}")

    print()
    print("=" * 60)
    print("TEST 2 – IsAirlineInTerminal")
    print("=" * 60)
    print(f"  VLG a T1 (esperat True):      {IsAirlineInTerminal(t1, 'VLG')}")
    print(f"  AFL a T1 (esperat False):     {IsAirlineInTerminal(t1, 'AFL')}")
    print(f"  Llista buida (esperat False): {IsAirlineInTerminal(Terminal('TX'), 'VLG')}")
    print(f"  Nom buit (esperat (False,-1)): {IsAirlineInTerminal(t1, '')}")

    print()
    print("=" * 60)
    print("TEST 3 – SearchTerminal")
    print("=" * 60)
    print(f"  VLG (esperat T1): '{SearchTerminal(airport, 'VLG')}'")
    print(f"  AFL (esperat T2): '{SearchTerminal(airport, 'AFL')}'")
    print(f"  XYZ (esperat ''): '{SearchTerminal(airport, 'XYZ')}'")

    print()
    print("=" * 60)
    print("TEST 4 – AssignGate")
    print("=" * 60)

    # Aeronau Schengen que opera amb VLG (T1, àrea Schengen → T1A)
    ac1 = Aircraft("EC-LVS", "VLG", "Schengen")
    res = AssignGate(airport, ac1)
    print(f"  EC-LVS / VLG / Schengen     → resultat: {res}  (esperat 0)")

    # Aeronau non-Schengen que opera amb IBE (T1, àrea non-Schengen → T1D)
    ac2 = Aircraft("EC-MHO", "IBE", "non-Schengen")
    res = AssignGate(airport, ac2)
    print(f"  EC-MHO / IBE / non-Schengen → resultat: {res}  (esperat 0)")

    # Aerolínia no trobada
    ac3 = Aircraft("UNKNWN", "ZZZ", "Schengen")
    res = AssignGate(airport, ac3)
    print(f"  UNKNWN / ZZZ / Schengen     → resultat: {res}  (esperat -1)")

    # Saturem les 3 portes non-Schengen de T1 (T1D1 ja ocupada, omplim T1D2 i T1D3)
    for aircraft_id in ["AA1", "AA2"]:
        ac = Aircraft(aircraft_id, "RYR", "non-Schengen")
        AssignGate(airport, ac)
    # Ara intentem assignar una quarta aeronau non-Schengen a T1 → sense portes
    ac_extra = Aircraft("AA3_overflow", "RYR", "non-Schengen")
    res = AssignGate(airport, ac_extra)
    print(f"  AA3_overflow / T1 plena     → resultat: {res}  (esperat -1)")

    print()
    print("=" * 60)
    print("TEST 5 – GateOccupancy després de les assignacions")
    print("=" * 60)
    occupancy = GateOccupancy(airport)
    for entry in occupancy:
        print(f"  Porta: {entry[0]:12s}  Estat: {entry[1]:9s}  Aeronau: {entry[2]}")