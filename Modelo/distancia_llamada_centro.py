import pandas as pd
import math
from grafo import Grafo
import numpy as np

#devevent = pd.read_csv("eventos.csv", sep=';')
#dcenter = pd.read_csv("centros.csv", sep=';')

data = []
data_2 = list()
events = []
bases = []
grafo = Grafo("Datos/nodos.csv", "Datos/arcos.csv")

with open("Datos/eventos_excel.csv", 'r') as file:
    next(file)
    for line in file:
        linea = line.strip().split(";")
        events.append(linea)
        
with open("Datos/bases.csv", 'r') as file1:
    next(file1)
    for line in file1:
        linea = line.strip().split(";")
        bases.append(linea)
        
def dis(x1, x2, y1, y2):
    distancia = math.sqrt((float(x2)-float(x1))**2 + (float(y2)-float(y1))**2)
    return distancia

#valor = float('inf')
# for i in events:
#     nodo_evento = grafo.nodo_cercano(float(i[0]),float(i[1]))
#     grafo.tiempo_minimo(nodo_evento.id)
#     list_i = []
#     for j in bases:
#         nodo_base = grafo.nodo_cercano(float(j[0]),float(j[1]))
#         list_i.append(nodo_base.tiempo)
#     data.append(list_i)
#     grafo.reiniciar_caminos()

for base in bases:
    nodo_base = grafo.nodo_cercano(float(base[0]), float(base[1]))
    grafo.tiempo_minimo(nodo_base.id)
    list_j = []
    for i in events:
        nodo_evento = grafo.nodo_cercano(float(i[0]),float(i[1]))
        list_j.append(nodo_evento.tiempo)
    data_2.append(list_j)
    grafo.reiniciar_caminos()
    
print("Terminó")
#data_2 = [[row[i] for row in data_2] for i in range(len(data_2[0]))]
data_2_transpose = np.transpose(data_2)
    
df = pd.DataFrame(data_2_transpose)
df.to_csv("tabla_tiempos.csv")
#with open("distancias_centrs_eventos.csv", "w") as file:
    #for linea in range(len(data)):
        #for elem in range(linea):
            #if elem != linea:
                #file.write(str(data[linea][elem]))
                #file.write(";")
            #else:
                #file.write(str(data[linea][elem]) + "\n")
    
# df = pd.DataFrame(data)
# df.to_csv("tabla_tiempos.csv")
#with open("distancias_centrs_eventos.csv", "w") as file:
    #for linea in data:
        #for elem in linea:
            #file.write(str(elem) + '\n')
    

            