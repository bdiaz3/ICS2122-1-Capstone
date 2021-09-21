import gurobipy as gp
from gurobipy import GRB
import time

m = 26 # Numero de centros
n = 22117 # LLamadas
a = 20 # Ambulancias

M = range(m)
N = range(n)

#COSTOS
c = [] 
with open("Datos/tabla_distancia.csv","r") as distancia:
    dist = distancia.readlines()
    for linea in dist:
        c.append(linea.strip().split(",")[1:])

model = gp.Model('Localización de Ambulancias')
model.setParam('OutputFlag', False) # Turns off solver chatter

xf = model.addVars(M,N,vtype=GRB.BINARY) # Binaria si a la base i se le asocia evento j
yf = model.addVars(M, vtype=GRB.BINARY) # Binaria si se ocupa la base i

rest_demand = model.addConstrs(((sum(xf[i,j] for i in M) == 1) for j in N),
name = "DEMANDF")

rest_assign = model.addConstrs(((sum(xf[i,j] for j in N) <= n*yf[i]) for i in M),
name = "ASSIGN")

rest_ambulance = model.addConstr((sum(yf[i] for i in M) <= a ), 
name = "AMBULANCE")

inicio  = time.time()


model.setObjective((sum(sum(float(c[j][i])*xf[i,j] for i in M) for j in N)),GRB.MINIMIZE)
model.optimize()

print(time.time()- inicio)

valor_optimo = model.objVal



print( '\n Objectivo modelo completo =', valor_optimo,'\n')