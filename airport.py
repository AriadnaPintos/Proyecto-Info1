class Airport:
    # Classe de definició d'aeroport
    def __init__(self, code, lat, lon):
        self.icao = code
        self.latitude = lat
        self.longitude = lon
        self.schengen = False

def IsSchengenAirport(code):
    # llista de paisos que son schengen
    lista = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM','EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']
    if not code:
        return False

    encontrado = False
    i = 0
    while i < len(lista) and encontrado == False:
        if code[0:2] == lista[i]:
            encontrado = True
        if not encontrado:
            i = i + 1
    return encontrado

def SetSchengen(airport):
    #poso si es schengen o no a l'aeroport com a resultat de la funció pasant-li el codi ICAO de l'aeroport
    airport.schengen = IsSchengenAirport(airport.icao)

def PrintAirport(airport):
    print(airport.__dict__)

def LoadAirports (filename):
    F = open(filename, "r")
    linea = F.readline()
    linea = F.readline()
    lista_ = []
    while linea != "":
        elementos = linea.split()
        codigo_icao = elementos[0]
        lat_txt = elementos[1]
        lon_txt = elementos[2]
        #Fem la conversió de les coordenades a lat
        grados_lat = float(lat_txt[1:3])
        minutos_lat = float(lat_txt[3:5])
        segundos_lat = float(lat_txt[5:7])
        lat_decimal = grados_lat + (minutos_lat/60) + (segundos_lat/3600)
        if lat_txt[0] == "S":
            lat_decimal = -lat_decimal
        # Fem la conversió de les coordenades a lon
        grados_lon = float(lon_txt[1:4])
        minutos_lon = float(lon_txt[4:6])
        segundos_lon = float(lon_txt[6:8])
        lon_decimal = grados_lon + (minutos_lon/60) + (segundos_lon/3600)
        if lon_txt[0] == "W":
            lon_decimal = -lon_decimal

        lista_.append(Airport(codigo_icao, lat_decimal, lon_decimal))
        linea = F.readline()
    F.close()
    return lista_

def SaveSchengenAirports(airports, filename):
    #Si l'aeroport és schengen ho fiquem en un nou doc
    if len(airports) == 0:
        print("Error, la lista está vacia.")
        return "Error"
    F = open(filename, "w")
    F.write("CODE LAT LON \n")
    i = 0
    while i < len(airports):
        if airports[i].schengen == True:
            linea = airports[i].icao + " " + str(airports[i].latitude) + " " + str(airports[i].longitude) + "\n"
            F.write(linea)
        i = i +1
    F.close()
    print("Schengen aeropuerto guardado con éxito.")

def AddAirport(airports, airport):
    # donada una llista d'entrada i un aeroport mirem si està a la llista i sinó l'afegim
    encontrado = False
    i = 0
    while i < len(airports) and not encontrado:
        if airports[i].icao == airport.icao:
            encontrado = True
        i = i + 1

    if not encontrado:
        airports.append(airport)
        return True
    else:
        print("Ese aeropuerto ya se encuentra en la lista.")
        return False

def RemoveAirport(airports, code):
    #Eliminar els aeroports
    encontrado = False
    i = 0
    while i < len(airports) and not encontrado:
        if code == airports[i].icao:
            j = i
            while j < len(airports) - 1:
                airports[j] = airports[j + 1]
                j = j + 1
            airports[:] = airports[:-1]
            encontrado = True
        i = i + 1

    if not encontrado:
        print("Error, no se ha encontrado el icao", code)
        return False

    print("Aeropuerto", code, "eliminado.")
    return True

import matplotlib.pyplot as plt

def PlotAirports(airports):
    schengen_count = 0
    non_schengen_count = 0
    i = 0

    while i < len(airports):
        SetSchengen(airports[i])
        if airports[i].schengen == True:
            schengen_count = schengen_count + 1
        else:
            non_schengen_count = non_schengen_count + 1
        i = i + 1

    labels = ["Airports"] #Nom eix x
    plt.ylabel("Número de aeropuertos") #Nom eix y
    plt.title("Schengen vs Non-Schengen")
    plt.bar(labels , [schengen_count], label = "Schengen", color="lightblue")
    plt.bar(labels, [non_schengen_count], label = "Non-Schengen", bottom=[schengen_count], color = "pink")
    plt.legend()
    plt.show()
