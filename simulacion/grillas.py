import random

class Grilla():
    def __init__(self, x_min, x_max, y_min, y_max, events=0):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self. events = events

class Mapa():
    def __init__(self):
        self.grillas = []
        self.pesos = []
        self.cargar_grillas()

    def cargar_grillas(self):
        with open("Datos/grillas.csv", "r") as archivo:
            archivo = archivo.readlines()
            for linea in archivo:
                linea = [float(elem) for elem in linea.strip().split(";")]
                grilla = Grilla(linea[0], linea[1], linea[2], linea[3], linea[4])
                self.grillas.append(grilla)
                self.pesos.append(linea[4])

    def seleccionar_grilla(self):
        grilla = random.choices(self.grillas, weights=tuple(self.pesos), k=1)
        return grilla[0]
        
class Generador():
    def __init__(self):
        self.grillas = []

    def llenar_grillas(self):
        with open("Datos/eventos_excel.csv", 'r', encoding='utf8') as file:
            next(file)
            for line in file:
                linea = [float(elem) for elem in line.strip().split(";")[0:2]]
                for grilla in self.grillas:
                    if grilla.x_min < linea[0] < grilla.x_max and  grilla.y_min < linea[1] < grilla.y_max:
                        grilla.events += 1

    def guardar_grillas(self):
        with open("Datos/grillas.csv", "w") as archivo:
            for grilla in self.grillas:
                archivo.write(f"{grilla.x_min}; {grilla.x_max}; {grilla.y_min}; {grilla.y_max}; {grilla.events}\n")

def crear_mapa():
    MAX_X = 165
    MIN_X = -35
    MAX_Y = 125
    MIN_Y = -45
    mapa = Generador()
    y_min = MIN_Y
    y_max = -40
    while y_max < MAX_Y:
        x_min = MIN_X
        x_max = -30
        while x_max < MAX_X:
            grilla = Grilla(x_min, x_max, y_min, y_max)
            mapa.grillas.append(grilla)
            x_min += 1
            x_max += 1
        y_min += 1
        y_max += 1
    return mapa

if __name__ == '__main__':
    mapa = crear_mapa()
    mapa.llenar_grillas()
    mapa.guardar_grillas()