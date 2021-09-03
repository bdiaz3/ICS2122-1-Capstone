import gurobipy as gp
from gurobipy import GRB
import time

m = 26 # Numero de centros
n = 16383 # LLamadas
a = 20 # Ambulancias

M = range(m)
N = range(n)

#COSTOS
c = [] 
with open("Datos/tabla_distancia.csv","r") as distancia:
    dist = distancia.readlines()
    for linea in dist:
        c.append(linea.strip().split(","))

model = gp.Model('Localización de Ambulancias')
model.setParam('OutputFlag', False) # turns off solver chatter

xf = model.addVars(M,N,vtype=GRB.BINARY) # Binaria si al evento i se le asocia a la base centro j
yf = model.addVars(M, vtype=GRB.BINARY) # Binaria si se ocupa el centro j

rest_demand = model.addConstrs(((sum(xf[i,j] for i in M) == 1) for j in N),name = "DEMANDF")
rest_assign = model.addConstrs(((sum(xf[i,j] for j in N) <= n*yf[i]) for i in M),name = "ASSIGN")
rest_ambulance = model.addConstr((sum(yf[i] for i in M) <= a ), name = "AMBULANCE")

inicio  = time.time()

# Descomentar para correr (demora mucho)
model.setObjective((sum(sum(float(c[j][i])*xf[i,j] for i in M) for j in N)),GRB.MINIMIZE)
model.optimize()

print(time.time()- inicio)

valor_optimo = model.objVal



print( '\n Objectivo modelo completo =', valor_optimo,'\n')