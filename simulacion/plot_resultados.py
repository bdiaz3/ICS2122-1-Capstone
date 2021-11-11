import matplotlib.pyplot as plt
import csv
import sys

ID_NODOS = []
COORDENADA_X_NODOS = []
COORDENADA_Y_NODOS = []
COORDENADA_X_BASES = []
COORDENADA_Y_BASES = []
COORDENADA_X_EVENTOS = []
COORDENADA_Y_EVENTOS = []
TUPLA_EVENTO_BASE = []
BASES_ASIGNADAS_X = []
BASES_ASIGNADAS_Y = []
RUTAS = []

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

with open("Datos Simulacion/rutas_base_evento.csv", "r") as archivo:
    lineas = archivo.readlines()
    for linea in lineas:
        linea = linea.strip().split(";")
        for l in range(len(linea)):
            elemento = linea[l].strip().split(",")
            linea[l] = (float(elemento[0]), float(elemento[1]))
        RUTAS.append(linea)

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

with open('Datos Simulacion/base_evento.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            COORDENADA_X_EVENTOS.append(float(row[0].replace(',','.')))
            COORDENADA_Y_EVENTOS.append(float(row[1].replace(',','.')))
            BASES_ASIGNADAS_X.append(float(row[2].replace(',','.')))
            BASES_ASIGNADAS_Y.append(float(row[3].replace(',','.')))
            line_count += 1

SOLUCION_BASE = [1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,0,1,0,0] #Soluciones aquí
COORDENADA_X_BASES_SOLUCION = []
COORDENADA_Y_BASES_SOLUCION = []
for i in range(len(COORDENADA_X_BASES)):
    if SOLUCION_BASE[i] == 1:
        COORDENADA_X_BASES_SOLUCION.append(COORDENADA_X_BASES[i])
        COORDENADA_Y_BASES_SOLUCION.append(COORDENADA_Y_BASES[i])

if __name__ == "__main__":
    plt.scatter(COORDENADA_X_BASES_SOLUCION, COORDENADA_Y_BASES_SOLUCION, c = 'black', s=15)
    plt.scatter(COORDENADA_X_EVENTOS, COORDENADA_Y_EVENTOS, c = 'red', s=12)
    plt.scatter(COORDENADA_X_NODOS, COORDENADA_Y_NODOS, c = 'blue', s=0.5)
    plt.legend(['Bases','Eventos','Nodos']) #Leyenda grafico: para eventos usar ['Nodos','Eventos','Centros', 'Bases Desocupadas', 'Bases Solución']

        
    for ruta in RUTAS:
        l = 0
        while l < len(ruta)-1:
            origen = ruta[l]
            destino =ruta[l+1]
            plt.plot([origen[0], destino[0]],[origen[1],destino[1]], color="green")
            l += 1

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
    plt.ylabel('Y')
    plt.xlabel('X')
    plt.show()
    plt.axis([-40, 170, -50, 140])
 