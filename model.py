import gurobipy as gp
from gurobipy import GRB
import sys
import numpy as np
import copy

NITER = 1000

m = 67 # Numero de centros
n = 16383 # LLamadas
a = 20 # Ambulancias

M = range(m)
N = range(n)

# PARAMETROS
B = 1
Tk = 10000
alpha = 0.99


#COSTOS
c = [] 
with open("Datos/tabla_distancia.csv","r") as distancia:
    for linea in distancia:
        c.append(linea.strip().split(","))


model = gp.Model('Localización de Ambulancias')
model.setParam('OutputFlag', False) # turns off solver chatter

xf = model.addVars(M,N,vtype=GRB.BINARY) # Binaria si al evento i se le asocia el centro j

# CONFIGURACIÓN INICIAL
y = [0.0]*m
j0 = np.random.randint(0,m-1)
y[j0] = 1.0


# REESTRICCIONES

rest_demand = model.addConstrs(((sum(xf[i,j] for i in M) == 1) for j in N),name = "DEMANDF")
rest_assign = model.addConstrs(((sum(xf[i,j] for j in N) <= n*y[i]) for i in M),name = "ASSIGN")
# rest_ambulance = model.addConstr(a >= (sum(y[i] for i in M) ), name = "AMBULANCE")

# MODELO

model.setObjective((sum(sum(float(c[j][i])*xf[i,j] for i in M) for j in N)),GRB.MINIMIZE)
model.optimize()

valor = model.objVal
best = valor

# Simmulated Annealing

for k in range(1, NITER):

# Se crea un vecino, agregando o quitando ambulancias de un centro aleatorio

    yvecino = copy.deepcopy(y) 
    j0 = np.random.randint(0,m-1) #ID del vecino
    yvecino[j0] = 1-yvecino[j0] # Nuevo valor 
    
    # Cambiamos el valor en la reestrición
    rest_assign[j0].RHS = n*yvecino[j0]

    #Actualizamos el modelo
    model.update()
    model.optimize()
    valor_vecino = model.objVal


    # Coondiciones de aceptacion 
    valor_old = valor
    if valor_vecino <= valor and a >= sum(yvecino[i] for i in M):
        # Cambiamos la solucion
        y = copy.deepcopy(yvecino) 
        valor = valor_vecino
        
    else:
        probT = np.exp(-(valor_vecino - valor)/(B*Tk)) # Funcion de probabilidad
        prob = np.random.rand()
        if probT > prob and a >= sum(yvecino[i] for i in M):
            y = copy.deepcopy(yvecino) # Aceptamos un vecino con "peor" valor 
            valor = valor_vecino

        else:
            # Se rechaza el vecino y revierte el cambio
            rest_assign[j0].RHS = n*(1-yvecino[j0]) 
            model.update()
            
        
    if valor < best:
        best = valor
        
    print("%8.0f %8.4f %8.4f %10.4f  %10.4f %4.0f" % (k, valor_old, valor_vecino, Tk))

    # Se actualiza la temperatura
    Tk = alpha*Tk
    
print('\n mejor valor encontrado: ',best)
print(y)

with open("Datos/output.csv","w") as output:
    for i in range(len(y)):
        if i != len(y)-1:
            output.write(str(y[i]))
            output.write(";")
        else:
            output.write(str(y[i]))




