# Projecte Informàtica 1

<div align="center">
  <img src="https://img.shields.io/badge/language-Python-blue?style=flat-square&logo=python&logoColor=white" alt="Language">
  <img src="https://img.shields.io/badge/IDE-PyCharm-black?style=flat-square&logo=pycharm" alt="IDE">
</div>

---

## AUTORS I CONTINGUTS
Aquest projecte ha estat desenvolupat pels membres del Grup 5: Ariadna Pintos, Pau Tondo i Júlia Adrubau; amb l'objectiu de desenvolupar un programa de gestió aeroportuària per tal d'analitzar els vols de l'Aeroport Josep Tarradelles Barcelona-El Prat (LEBL)

<img src="ImatgeDeGrup.jpeg" width="500">

## DESENVOLUPAMENT DEL PROJECTE
El programa s'ha fet en quatre versions diferents, on en cada versió s'han anat millorant i implementant noves fucions progressivament més complexes.


## Versió 1 
En la versió 1 del projecte s’han desenvolupat els fitxers airport.py, test_airport.py i interface.py, implementant la classe Airport amb els   seus atributs bàsics i les funcionalitats per gestionar aeroports (carregar, afegir, eliminar i modificar l’estat Schengen). Mitjançant un altre programa anomenat test_airport.py, hem pogut comprovar exitosament el funcionament de les funcions creades al fitxer airport.py i les hem afegit a la interfície. A la interfície (interface.py) s'hi han integrat les diferents funcionalitats dels botons, però faltaria afegir la llista corresponent amb l'informació del avions, del fitxer (airports.txt), i la integració dels gràfics i el Google Earth dins de la mateixa pestanya.

[Link al vídeo de la versió 1](https://drive.google.com/file/d/1behWJ3YxZa6cuwD9R_OPxWJ-vII4jdmq/view?usp=sharing)

## Versió 2
Respecte la versió 1 s'ha millorat la interfície, integrant els plots i els missatges de confirmació, faltaria per integrar la vista de Google Earth. 
En la versió 2 del projecte s’ha desenvolupat el fitxer aircraft.py, on s’ha definit la classe Aircraft amb la informació dels vols que arriben a LEBL, i s’han implementat funcions per carregar dades des de fitxers, analitzar-les i representar-les gràficament (freqüència d’aterratges, vols per aerolínia i classificació Schengen/no Schengen). També s’ha incorporat la generació de fitxers per visualitzar les trajectòries dels vols a Google Earth i una funció per identificar vols de llarga distància mitjançant la fórmula de Haversine. Les funcions creades es comproven mitjançant una secció de test integrada dins del mateix fitxer.

[Link al video de la versió 2](https://drive.google.com/file/d/1fmZLGcbT3g-fjuj8RVmSJddWe17uQ-pr/view?usp=drive_link)

## Versió 3
En aquesta versió s'han millorat i integrat un mapa del Google Earth a la interficie. S'han creat quatre classes (BarcelonaAP, Terminal, BoardingAreas i Gates) i vuit funcions noves.
Aquest conjunt de funcions ens permet gestionar l'estructura i l'operativitat diària de l'aeroport de Barcerlona (LEBL). Primer es configuren els elements mitjançant la funció "SetGates", que crea i inicialitza les portes d'embarcament assigant-les-hi un prefix i marcant-les om a lliures o ocupades i amb "LoadAirlines" carrega les aerolínies d'una terminal des d'un fitxer de text. Aquestes dues funcions mencionades anteriorment, son utilitzades per una tercera funció anomenada "LoadAirportsStructure" que s'encarrega de configurar tot l'aeroport a partir d'un únic fitxer centralitzat.
Pel que fa a la gestió de la informació la funció "GateOccupancy" genera una llista amb el nom i l'estat d'ocupació de cadap porta. D'altra banda, "IsAirlineInTerminal" comprova si una companyia opera una terminal concreta. "SearchTerminal" busca i retorna la terminal assignada a cada aerolínia. Per últim, "AssignGate" coordina les funcions anteriors i troba la zona d'embarcament correcta, assignant la porta que estigui lliure.

[Link al video de la versió 3](https://drive.google.com/file/d/1JY11WIZbC04W4K5eMxFr69Em97oxXDHS/view?usp=drive_link)

## Versió 4
En aquesta versió s'han millorat i integrat les sortides de vols a la interfície per a aconseguir un simulador dinàmic en temps real. S'ha ampliat la classe `Aircraft` per afegir nous camps de sortida i s'han creat sis funcions noves.

Aquest conjunt de funcions ens permet gestionar l'alliberament i la reassignació contínua de les portes de l'aeroport de Barcelona (LEBL) al llarg de la jornada. Primer es processen els fitxers d'enlairament mitjançant la funció `LoadDepartures` , i amb `MergeMovements` es combinen els vols que tenen el mateix identificador i horaris compatibles (tenint en compte els fitxers d'"arrivals" i "departures"). Per als avions que passen la nit a l'aeroport, la funció `NightAircraft` els identifica perquè `AssignNightGates` pugui assignar-los una porta inicialment.

Pel que fa a la simulació temporal, la funció `FreeGate` s'encarrega d'alliberar de manera automàtica les portes dels avions que ja han sortit. D'altra banda, `AssignGatesAtTime` coordina el procés realitzant l'assignació dinàmica de portes en franges horàries d'una hora i comptabilitzant els vols no assignats per manca d'espai. Per últim, `PlotDayOccupancy` analitza totes les dades anteriors per generar gràfics complets que mostren l'ocupació diària per terminals a cada franja horària, integrant a la interfície funcionalitats extres i creatives com a valor afegit.

## Funcionalitats extres
Per a complementar el funcionament del programa, hem considerat oportú millorar la capacitat d'anàlisi i control de l'aeroport mitjançant la integració de quatre funcions innovadores que afegeixen dinamisme, detall i sostenibilitat al projecte.

En primer lloc, s'ha implementat un mode de simulació/reproducció del temps real, una funcionalitat que transforma la visualització estàtica en un panell interactiu amb botons de reproducció, pausa i un control lliscant de velocitat; un rellotge digital avança minut a minut a la pantalla mentre les portes canvien dinàmicament de color (verd per a lliure i vermell per a ocupat) reflectint els aterratges i enlairaments. Per a facilitar l'accés a la informació, s'ha afegit un buscador d'informació detallada que permet cercar vols o portes concretes a la interfície; en seleccionar una porta (fent clic sobre ella), es desplega un panell lateral amb la seva agenda completa per a tot el dia, mostrant tant els avions que ja hi han passat com els que estan programats per a arribar.

Pel que fa a la conscienciació ambiental, la funció de càlcul d'emprempta de Carboni utilitza la fórmula de Haversine per a calcular la distància recorreguda pels vols, associant a cada aeronau un consum estimat de combustible per quilòmetre per a generar gràfics interactius de l'impacte ecològic total per dia o per aerolínia. Finalment, per a optimitzar la gestió operativa, s'ha desenvolupat la funció d'anàlisi de retards i moments crítics del dia, la qual detecta automàticament conflictes quan dos vols es solapen en una mateixa porta, proposa una alternativa de manera immediata i genera un informe amb els moments crítics i de major congestió de la jornada. 

Finalment, s'ha incorporat un Assistent de Connexions i Transbords enfocat a l'experiència de l'usuari, el qual avalua la viabilitat d'enllaçar dos vols consecutius calculant automàticament el temps real necessari per al desplaçament en contrast amb el temps disponible; la funció detalla els minuts restants de marge i determina si el passatger ha de passar o no per un control de passaports segons la naturalesa i procedència dels vols (tipus Schengen o No-Schengen).




