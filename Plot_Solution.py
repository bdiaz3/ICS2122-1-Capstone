import matplotlib.pyplot as plt
import csv

ID_NODOS = []
COORDENADA_X_NODOS = []
COORDENADA_Y_NODOS = []
COORDENADA_X_CENTROS = []
COORDENADA_Y_CENTROS = []
COORDENADA_X_BASES = []
COORDENADA_Y_BASES = []
COORDENADA_X_EVENTOS = []
COORDENADA_Y_EVENTOS = []

with open('Datos/nodos.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            ID_NODOS.append(row[0])
            COORDENADA_X_NODOS.append(float(row[1]))
            COORDENADA_Y_NODOS.append(float(row[2]))
            line_count += 1

with open('Datos/centros.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            COORDENADA_X_CENTROS.append(float(row[0].replace(',','.')))
            COORDENADA_Y_CENTROS.append(float(row[1].replace(',','.')))
            line_count += 1

with open('Datos/bases.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            COORDENADA_X_BASES.append(float(row[0].replace(',','.')))
            COORDENADA_Y_BASES.append(float(row[1].replace(',','.')))
            line_count += 1

with open('Datos/eventos.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            COORDENADA_X_EVENTOS.append(float(row[0].replace(',','.')))
            COORDENADA_Y_EVENTOS.append(float(row[1].replace(',','.')))
            line_count += 1

SOLUCION_BASE = [0,1,1,0,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,0,0,1,1,0,1,0] #Soluciones aquí
COORDENADA_X_BASES_SOLUCION = []
COORDENADA_Y_BASES_SOLUCION = []
for i in range(len(COORDENADA_X_BASES)):
    if SOLUCION_BASE[i] == 1:
        COORDENADA_X_BASES_SOLUCION.append(COORDENADA_X_BASES[i])
        COORDENADA_Y_BASES_SOLUCION.append(COORDENADA_Y_BASES[i])

    
plt.scatter(COORDENADA_X_NODOS, COORDENADA_Y_NODOS, s=0.5)
#plt.scatter(COORDENADA_X_EVENTOS, COORDENADA_Y_EVENTOS, s=0.1, c = 'orange') # Aca pa plotear eventos
plt.scatter(COORDENADA_X_CENTROS, COORDENADA_Y_CENTROS, c = 'red', s=9)
plt.scatter(COORDENADA_X_BASES, COORDENADA_Y_BASES, c = 'green', s=9)
plt.scatter(COORDENADA_X_BASES_SOLUCION, COORDENADA_Y_BASES_SOLUCION, c = 'blue', s=9)
plt.legend(['Nodos','Centros', 'Bases Desocupadas', 'Bases Solución']) #Leyenda grafico: para eventos usar ['Nodos','Eventos','Centros', 'Bases Desocupadas', 'Bases Solución']

with open('Datos/arcos_coordenados.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            p1x = float(row[0])
            p1y = float(row[1])
            p2x = float(row[2])
            p2y = float(row[3])
            plt.plot([p1x, p2x],[p1y, p2y], c="lightseagreen", linewidth=0.1)
            line_count += 1
ax = plt.axes()
ax.set_facecolor("black")
plt.ylabel('Y')
plt.xlabel('X')
plt.axis([-40, 170, -50, 140])
plt.show()