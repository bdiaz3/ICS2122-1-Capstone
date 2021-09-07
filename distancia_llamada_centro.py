import pandas as pd
import math 

#devevent = pd.read_csv("eventos.csv", sep=';')
#dcenter = pd.read_csv("centros.csv", sep=';')

data = []
events = []
center = []
with open("eventos.csv", 'r') as file:
    next(file)
    for line in file:
        linea = line.split(";")
        events.append(linea)
        
with open("bases.csv", 'r') as file1:
    next(file1)
    for line in file1:
        linea = line.split(";")
        center.append(linea)
        
def dis(x1, x2, y1, y2):
    distancia = math.sqrt((float(x2)-float(x1))**2 + (float(y2)-float(y1))**2)
    return distancia

#valor = float('inf')
for i in events:
    list_i = []
    
    for j in center:
        valor = dis(i[0],j[0],i[1],j[1])
        list_i.append(valor)
    
    data.append(list_i)

#with open("distancias_centrs_eventos.csv", "w") as file:
    #for linea in range(len(data)):
        #for elem in range(linea):
            #if elem != linea:
                #file.write(str(data[linea][elem]))
                #file.write(";")
            #else:
                #file.write(str(data[linea][elem]) + "\n")
    
df = pd.DataFrame(data)
df.to_csv("tabla_distancia.csv")
#with open("distancias_centrs_eventos.csv", "w") as file:
    #for linea in data:
        #for elem in linea:
            #file.write(str(elem) + '\n')
    

            