from itertools import product
from math import sqrt

import gurobipy as gp
from gurobipy import GRB

# tested with Gurobi v9.1.0 and Python 3.7.0

# Parameters
customers = [(0,1.5), (2.5,1.2)]
facilities = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]
setup_cost = [3,2,3,1,3,3,4,3,2]
costo = []
num_facilities = 20
with open("Datos/tabla_tiempos_nueva.csv","r", encoding="UTF-8") as distancia:
    dist = distancia.readlines()
    for linea in dist:
        costo.append(linea.strip().split(",")[1:])

m = gp.Model('facility_location')
select = m.addVars(num_facilities, vtype=GRB.BINARY, name='Select')
assign = m.addVars(cartesian_prod, ub=1, vtype=GRB.CONTINUOUS, name='Assign')