import math

class  Nodo:
    def __init__(self,id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vecinos = {}  # {"id: tiempo"}

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

    def agregar_arco(self, id_origen, id_destino, velocidades):
        n_origen = self.nodos[id_origen]
        n_destino = self.nodos[id_destino]
        
        n_origen.vecinos[id_destino] = velocidades
        n_destino.vecinos[id_origen] = velocidades
    
    def distancia(self, id_origen, id_destino):
        origen = self.nodos[id_origen]
        destino = self.nodos[id_destino]
        return math.sqrt((origen.x-destino.x)**2 + (origen.y-destino.y)**2)
    
    


if __name__ == "__main__":
    grafo = Grafo("Datos/nodos.csv", "Datos/arcos.csv")
