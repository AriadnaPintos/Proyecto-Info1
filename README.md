# Projecte Informàtica 1

<div align="center">
  <img src="https://img.shields.io/badge/language-Python-blue?style=flat-square&logo=python&logoColor=white" alt="Language">
  <img src="https://img.shields.io/badge/IDE-PyCharm-black?style=flat-square&logo=pycharm" alt="IDE">
</div>

---

## AUTORS I CONTINGUTS
Aquest projecte ha estat desenvolupat pels membres del Grup 5: Ariadna Pintos, Pau Tondo i Júlia Adrubau; amb l'objectiu de desenvolupar un programa de gestió aeroportuària per tal d'analitzar els vols de l'Aeroport Josep Tarradelles Barcelona-El Prat (LEBL)
## DESENVOLUPAMENT DEL PROJECTE
El programa s'ha fet en quatre versions diferents (de les quals només dues estan actives actualment). 

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




