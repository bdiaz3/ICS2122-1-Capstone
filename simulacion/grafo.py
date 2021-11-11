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
        with open(path, "r", encoding="utf-8") as nodos:
            nodos = nodos.readlines()
            nodos.pop(0)
            for n in nodos:
                n = n.strip().split(";")
                self.agregar_nodo(int(n[0]), float(n[1]), float(n[2]))
            
    def cargar_arcos(self, path):
        with open(path, "r", encoding="utf-8") as arcos:
            arcos = arcos.readlines()
            arcos.pop(0)
            for a in arcos:
                a = a.strip().split(";")   
                distancia = self.distancia(float(a[0]),float(a[1]))
                velocidad = sum(float(x) for x in a[2:])/len(a[2:])      
                tiempo = distancia/velocidad
                if distancia != 0:
                    # Multiplicamos por 60 para pasarlo a minutos
                    self.agregar_arco(int(a[0]), int(a[1]), 60*tiempo)
            
    def agregar_nodo(self, id, x, y):
        self.nodos[id] = Nodo(id,x,y)

    def agregar_arco(self, id_origen, id_destino, tiempo):
        n_origen = self.nodos[id_origen] 
        n_origen.vecinos[id_destino] = tiempo

    
    def distancia(self, id_origen, id_destino):
        origen = self.nodos[id_origen]
        destino = self.nodos[id_destino]
        return math.sqrt((origen.x-destino.x)**2 + (origen.y-destino.y)**2)

    # Este metodo usa Dijkstra para encontrar la distancia minima desde "id_inicio" hasta todos los
    # otros nodos del Gráfo. # Networkz
    def tiempo_minimo(self, id_inicio):
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


    def reiniciar_caminos(self):
        for nodo in self.nodos.values():
            nodo.color = "White"
            nodo.tiempo = float("Infinity")
            nodo.elegido = None
    
    def nodo_cercano(self, x, y):
        distancia = float("Infinity")
        cercano = None
        for nodo in  self.nodos.values():
            nueva_dist = math.sqrt((x-nodo.x)**2 + (y-nodo.y)**2)
            if nueva_dist < distancia:
                distancia = nueva_dist
                cercano = nodo
        tiempo = distancia/35 # Asumimos 35 km/h
        return cercano, tiempo
    
    def entregar_ruta(self, origen_id, destino_id):
        if origen_id == destino_id:
            return []
        origen = self.nodos.get(origen_id)
        destino = self.nodos.get(destino_id)
        if origen is None or destino is None:
            return []
        por_visitar = [[origen]]
        visitados = list()
        while len(por_visitar):
            lista_actual = por_visitar.pop(0)
            nodo_actual = lista_actual[-1]
            if nodo_actual not in visitados:
                vecinos = [self.nodos.get(nodo_actual.elegido)]
                for vecino in vecinos:
                    por_visitar.append(list(lista_actual)+[vecino])
                    if vecino == destino:
                        lista_con_nombres = [(nodo.x, nodo.y, nodo.tiempo-self.nodos[nodo.elegido].tiempo) 
                                                 if nodo.elegido != None else (nodo.x, nodo.y , 0) for nodo in por_visitar[-1]]
                        return lista_con_nombres
                visitados.append(nodo_actual)
        return []
    

 