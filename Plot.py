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
    print(line_count)

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


    
#plt.plot(COORDENADA_X_ARCOS, COORDENADA_Y_ARCOS)
plt.scatter(COORDENADA_X_NODOS, COORDENADA_Y_NODOS, s=0.5)
#plt.scatter(COORDENADA_X_EVENTOS, COORDENADA_Y_EVENTOS, s=0.1, c = 'orange')
plt.scatter(COORDENADA_X_CENTROS, COORDENADA_Y_CENTROS, c = 'red', s=3)
plt.scatter(COORDENADA_X_BASES, COORDENADA_Y_BASES, c = 'blue', s=3)
plt.legend(['Nodos','Eventos','Centros','Bases'])

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
            #print(p2x,p2y)
            plt.plot([p1x, p2x],[p1y, p2y], c="lightseagreen", linewidth=0.1)
            line_count += 1
ax = plt.axes()
ax.set_facecolor("black")
plt.ylabel('Y')
plt.xlabel('X')
plt.axis([-40, 170, -50, 140])
plt.show()