import math
from collections import deque
from copy import copy


class  Nodo:
    def __init__(self,id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vecinos = {}  # {"id: tiempo"}
        self.color = "White"
        self.tiempo = float("Infinity")
        self.elegido = None

    def __repr__(self):
        return str(self.id)

class Grafo:
    def __init__(self, path_nodos, path_arcos):
        self.nodos = {}
        self.bases = {}
        
        self.cargar_nodos(path_nodos)
        self.cargar_arcos(path_arcos)
        
    def cargar_nodos(self, path):
        with open(path) as nodos:
            nodos = nodos.readlines()
            nodos.pop(0)
            for n in nodos:
                n = n.strip().split(";")
                self.agregar_nodo(int(n[0]), float(n[1]), float(n[2]))
            
    def cargar_arcos(self, path):
        with open(path) as arcos:
            arcos = arcos.readlines()
            arcos.pop(0)
            for a in arcos:
                a = a.strip().split(";")
                velocidad = sum(float(x) for x in a[2:])/len(a[2:])
                distancia = self.distancia(int(a[0]),int(a[1]))
                self.agregar_arco(int(a[0]), int(a[1]), distancia/velocidad)
            
    def agregar_nodo(self, id, x, y):
        self.nodos[id] = Nodo(id,x,y)

    def agregar_arco(self, id_origen, id_destino, tiempo):
        n_origen = self.nodos[id_origen]
        n_destino = self.nodos[id_destino]
        
        n_origen.vecinos[id_destino] = tiempo
        n_destino.vecinos[id_origen] = tiempo
    
    def distancia(self, id_origen, id_destino):
        origen = self.nodos[id_origen]
        destino = self.nodos[id_destino]
        return math.sqrt((origen.x-destino.x)**2 + (origen.y-destino.y)**2)

    # Este metodo usa Dijkstra para encontrar la distancia minima desde "id_inicio" hasta todos los
    # otros nodos del Gráfo. Despues retorna la distancia minima "id_destino" y reinicia el grafo.
    def tiempo_minimo(self, id_inicio, id_destino):
        inicio = self.nodos.get(id_inicio)
        if inicio != None:
            por_visitar = deque([inicio])
            inicio.color = "Gray"
            inicio.tiempo = 0

            while len(por_visitar)> 0:
                actual = por_visitar.popleft()
                for id_vecino,tiempo in actual.vecinos.items():
                    vecino = self.nodos[id_vecino]
                    if vecino.color == "White" or vecino.color == "Gray":

                        if vecino.tiempo > actual.tiempo + tiempo:
                            vecino.tiempo = actual.tiempo + tiempo
                            vecino.elegido = actual.id
                        if vecino.color == "White":
                            vecino.color = "Gray"
                            por_visitar.append(vecino)
                actual.color = "Black"

            valor = copy(self.nodos[id_destino].tiempo)
            self.reiniciar_caminos()
            return valor

    def reiniciar_caminos(self):
        for nodo in self.nodos.values():
            nodo.color = "White"
            nodo.tiempo = float("Infinity")
            nodo.elegido = None

if __name__ == "__main__":
    grafo = Grafo("Datos/nodos.csv", "Datos/arcos.csv")
    print(grafo.tiempo_minimo(0, 22))

 