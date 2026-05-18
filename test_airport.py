from airport import *
airport = Airport ("LEBL", 41.297445, 2.0832941)
SetSchengen(airport)
PrintAirport (airport)

airports = LoadAirports("Airports.txt")
SaveSchengenAirports(airports, "schengenairport.txt")
AddAirport(airports, airport)
RemoveAirport(airports, "LEBL")
PlotAirports(airports)
MapAirports(airports)






