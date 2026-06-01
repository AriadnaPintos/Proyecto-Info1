import os
#Definim les funcions
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
        Actua com a constructor dinàmic. En lloc de definir portes manualment,
        aquesta funció recorre un rang numèric (init_gate a end_gate), instància
        objectes de la classe Gate i els associa a una àrea concreta, garantint
        que el nom de la porta sigui únic.
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
        S'encarrega de la persistència de dades externa. Llegeix un fitxer de text
        associat a cada terminal i normalitza la llista d'aerolínies (terminal.airlines)
        per permetre la cerca ràpida de quina companyia opera on.
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
    És la funció "fàbrica". Analitza un fitxer principal de configuració de l'aeroport
    per construir tota l'estructura d'objectes (Aeroport > Terminals > Àrees > Portes).
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
        Funció de validació lògica. Comprova si el codi ICAO d'una
        aerolínia existeix a la llista d'una terminal, retornant un booleà.
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
        Implementa la lògica de cerca d'ubicació. Utilitza IsAirlineInTerminal
        per escanejar totes les terminals i retornar el nom de la terminal on correspon
        operar a l'aerolínia indicada
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
        És l'algorisme de decisió principal. Aplica una lògica de cerca "Voraç"
        (Greedy): primer filtra per terminal segons l'aerolínia, després per tipus
        d'àrea (Schengen o non-Schengen), i finalment assigna la primera porta (gate)
        que tingui occupied = False.
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
    def __init__(self, aircraft_id, airline, flight_type):
        self.id = aircraft_id
        self.airline = airline
        self.flight_type = flight_type
    #Representa una aeronau que vol aterrar.
    # id          – identificador de l'aeronau (p.ex. 'DALEN')
    # airline     – codi ICAO de l'aerolínia (p.ex. 'VLG')
    # flight_type – 'Schengen' o 'non-Schengen'





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


def AssignNightGates(bcn, aircrafts):
    '''
    Rep un objecte BarcelonaAP i una llista d'aeronaus.
    Assigna una porta a cada aeronau de la llista que sigui
    exclusivament de sortida (sense dades d'arribada).
    Retorna ([], -1) si la llista és buida.
    '''
    # Si la llista és buida, retornem error
    if not aircrafts:
        return [], -1

    errors = 0
    for ac in aircrafts:
        # Saltem les aeronaus que tenen dades d'arribada:
        # les nocturnes han d'tenir origin i arrival buits
        if ac.origin != "" or ac.arrival != "":
            continue

        # Intentem assignar una porta a l'aeronau nocturna
        result = AssignGate(bcn, ac)

        # Si no s'ha pogut assignar (no hi ha portes lliures), comptem l'error
        if result == -1:
            errors += 1

    # Retornem el nombre d'aeronaus que no s'han pogut assignar
    return errors


def FreeGate(bcn, id):
    '''
    Rep un objecte BarcelonaAP i un id d'aeronau.
    Allibera la porta assignada a l'aeronau amb aquest id.
    Retorna 0 si s'ha alliberat correctament, -1 si no s'ha trobat.
    '''
    # Recorrem tota l'estructura: terminals → àrees → portes
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:

                # Quan trobem la porta amb l'id de l'aeronau, l'alliberem
                if gate.aircraft_id == id:
                    gate.occupied = False
                    gate.aircraft_id = None
                    return 0  # Alliberament correcte

    # Si hem recorregut tot l'aeroport i no hem trobat l'aeronau, retornem error
    return -1


def AssignGatesAtTime(bcn, aircrafts, time):
    '''
    Rep un objecte BarcelonaAP, una llista d'aeronaus i una hora exacta
    en format "HH:MM". Primer allibera les portes dels avions que ja han
    sortit abans d'aquesta hora. Després assigna portes als avions que
    aterren durant la franja d'una hora a partir de l'hora rebuda.
    Retorna el nombre d'aeronaus no assignades per manca de portes.
    '''
    from aircrafts import _time_to_minutes

    # Convertim l'hora rebuda a minuts per poder comparar fàcilment
    time_min = _time_to_minutes(time)

    # Calculem el final de la franja horària (1 hora després)
    end_min = time_min + 60

    # ── Pas 1: Alliberar portes dels avions que ja han sortit ──────────────
    for ac in aircrafts:
        # Només processem aeronaus que tenen hora de sortida definida
        if ac.departure != "":
            dep_min = _time_to_minutes(ac.departure)

            # Si l'avió ja ha sortit abans de l'hora actual, alliberem la seva porta
            if dep_min <= time_min:
                FreeGate(bcn, ac.id)

    # ── Pas 2: Assignar portes als avions que aterren en aquesta franja ────
    not_assigned = 0
    for ac in aircrafts:
        # Només processem aeronaus que tenen hora d'arribada definida
        if ac.arrival != "":
            arr_min = _time_to_minutes(ac.arrival)

            # Comprovem si l'arribada cau dins la franja horària [time_min, end_min)
            if time_min <= arr_min < end_min:
                result = AssignGate(bcn, ac)

                # Si no hi ha portes lliures disponibles, comptem l'aeronau no assignada
                if result == -1:
                    not_assigned += 1

    # Retornem el nombre d'aeronaus que no s'han pogut assignar per falta de portes
    return not_assigned


def PlotDayOccupancy(bcn, aircrafts):
    """Mostra una gràfica en text de l'ocupació de les terminals per hores"""
    print(f"\n" + "=" * 55)
    print(f" GRÀFICA D'OCUPACIÓ DIÀRIA DE L'AEROPORT (VERSIÓ 4)")
    print(f"=" * 55)
    print(f"Hora  | Portes T1  | Portes T2  | Avions sense assignar")
    print("-" * 55)

    # Simulem el pas del temps hora per hora (de 00:00 a 23:00)
    for hour in range(0, 24):
        time_str = f"{hour:02d}:00"

        # Executem la lògica d'assignació/alliberació per a aquesta hora
        not_assigned = AssignGatesAtTime(bcn, aircrafts, time_str)

        # Comptem les portes ocupades reals a cada terminal en aquesta hora
        t1_occupied = sum(1 for area in bcn.terminals[0].boarding_areas for gate in area.gates if gate.occupied) if len(
            bcn.terminals) > 0 else 0
        t2_occupied = sum(1 for area in bcn.terminals[1].boarding_areas for gate in area.gates if gate.occupied) if len(
            bcn.terminals) > 1 else 0

        # Pintem les barres visuals de la gràfica emprant caràcters '█'
        bar_t1 = "█" * t1_occupied
        bar_t2 = "█" * t2_occupied
        print(f"{time_str} | {bar_t1:<10} ({t1_occupied}) | {bar_t2:<10} ({t2_occupied}) | {not_assigned}")


# ── SECCIÓ DE TEST (Ben tabulada i aïllada dins del main de manera correcta) ──

if __name__ == "__main__":
    # Nota: Com que aquest bloc s'executa si és el fitxer principal,
    # necessita tenir l'objecte 'airport' inicialitzat prèviament per les funcions de dalt.

    print()
    print("=" * 60)
    print("TEST 6 – AssignNightGates (Noves funcions)")
    print("=" * 60)

    # Configurem els camps requerits per a les proves
    ac_nocturn = Aircraft("NIGHT-99", "VLG", "Schengen")
    ac_nocturn.origin = ""
    ac_nocturn.arrival = ""
    ac_nocturn.departure = "06:30"

    ac_diurn = Aircraft("DAY-01", "VLG", "Schengen")
    ac_diurn.origin = "LEMD"
    ac_diurn.arrival = "08:15"
    ac_diurn.departure = "09:45"

    llista_v4 = [ac_nocturn, ac_diurn]

    # Provem l'assignació nocturna
    err_night = AssignNightGates(airport, llista_v4)
    print(f"  Aeronaus nocturnes no assignades (esperat 0): {err_night}")

    print()
    print("=" * 60)
    print("TEST 7 – FreeGate")
    print("=" * 60)
    res_free = FreeGate(airport, "NIGHT-99")
    print(f"  Resultat d'alliberar 'NIGHT-99' (esperat 0): {res_free}")

    res_err = FreeGate(airport, "INVENTAT")
    print(f"  Resultat amb avió inexistent (esperat -1): {res_err}")

    print()
    print("=" * 60)
    print("TEST 8 – AssignGatesAtTime")
    print("=" * 60)
    # Preparem l'estat d'una porta per al test horari
    airport.terminals[0].boarding_areas[0].gates[0].occupied = True
    airport.terminals[0].boarding_areas[0].gates[0].aircraft_id = "NIGHT-99"

    # Executem la simulació
    not_assigned = AssignGatesAtTime(airport, llista_v4, "08:00")
    print(f"  Avions sense assignar a la franja de les 08:00 (esperat 0): {not_assigned}")
    print(f"  Porta ocupada ara per: {airport.terminals[0].boarding_areas[0].gates[0].aircraft_id} (esperat 'DAY-01')")

    # Llançament de la simulació de la gràfica completa de 24h
    PlotDayOccupancy(airport, llista_v4)


def DetectGateConflicts(bcn, aircrafts):
    """
    Recorre tots els avions del cronograma i detecta si dos avions
    estan assignats a la mateixa porta al mateix temps.
    Un conflicte es dona quan:
        - Dos Aircraft comparteixen gate (aircraft_id diferent però mateixa porta)
        - Els seus intervals [arrival, departure] se solapen

    Retorna una llista de diccionaris, un per cada conflicte:
        {
          'gate':     nom de la porta,
          'ac1':      id del primer avió,
          'ac2':      id del segon avió,
          'overlap_start': inici del solapament (minuts),
          'overlap_end':   fi del solapament (minuts)
        }
    """
    from aircrafts import _time_to_minutes

    # Construïm un diccionari: gate_name -> llista d'Aircraft que hi passen
    gate_map = {}
    for ac in aircrafts:
        # Obtenim la porta assignada recorrent l'aeroport
        for terminal in bcn.terminals:
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    if gate.aircraft_id == ac.id:
                        if gate.name not in gate_map:
                            gate_map[gate.name] = []
                        gate_map[gate.name].append(ac)

    conflicts = []
    for gate_name, acs in gate_map.items():
        # Comparem tots els parells d'avions a la mateixa porta
        i = 0
        while i < len(acs):
            j = i + 1
            while j < len(acs):
                ac1, ac2 = acs[i], acs[j]
                arr1 = _time_to_minutes(ac1.arrival)   if ac1.arrival   else 0
                dep1 = _time_to_minutes(ac1.departure) if ac1.departure else 1439
                arr2 = _time_to_minutes(ac2.arrival)   if ac2.arrival   else 0
                dep2 = _time_to_minutes(ac2.departure) if ac2.departure else 1439

                overlap_start = max(arr1, arr2)
                overlap_end   = min(dep1, dep2)

                if overlap_start < overlap_end:   # Hi ha solapament real
                    conflicts.append({
                        'gate':          gate_name,
                        'ac1':           ac1.id,
                        'ac2':           ac2.id,
                        'overlap_start': overlap_start,
                        'overlap_end':   overlap_end
                    })
                j += 1
            i += 1

    return conflicts


def ProposeAlternativeGate(bcn, ac, exclude_gate):
    """
    Donada una aeronau i la porta conflictiva, busca la primera porta lliure
    del mateix tipus (Schengen/non-Schengen) a la mateixa terminal.
    Retorna el nom de la porta alternativa, o None si no n'hi ha cap.
    """
    terminal_name = SearchTerminal(bcn, ac.airline)
    if not terminal_name:
        return None

    for terminal in bcn.terminals:
        if terminal.name != terminal_name:
            continue
        # Determinem el tipus de vol de l'aeronau
        flight_type = getattr(ac, 'flight_type', None)
        for area in terminal.boarding_areas:
            if flight_type and area.type != flight_type:
                continue
            for gate in area.gates:
                if gate.name != exclude_gate and not gate.occupied:
                    return gate.name
    return None


def CriticalMoments(aircrafts, threshold=5):
    """
    Detecta les franges horàries on hi ha més de `threshold` avions
    simultàniament a terra (entre arrival i departure).
    Retorna una llista de diccionaris:
        { 'hour': "HH:00", 'count': N, 'aircraft_ids': [...] }
    ordenada de més a menys ocupació.
    """
    from aircrafts import _time_to_minutes

    critical = []
    for hour in range(24):
        t_start = hour * 60
        t_end   = t_start + 59
        on_ground = []
        for ac in aircrafts:
            arr = _time_to_minutes(ac.arrival)   if ac.arrival   else -1
            dep = _time_to_minutes(ac.departure) if ac.departure else -1
            # L'avió és a terra si el seu interval se solapa amb la franja
            if arr != -1 and dep != -1 and arr <= t_end and dep >= t_start:
                on_ground.append(ac.id)
            elif arr != -1 and dep == -1 and arr <= t_end:
                on_ground.append(ac.id)
        if len(on_ground) >= threshold:
            critical.append({
                'hour':         f"{hour:02d}:00",
                'count':        len(on_ground),
                'aircraft_ids': on_ground
            })

    critical.sort(key=lambda x: x['count'], reverse=True)
    return critical