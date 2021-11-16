import networkx as nx
import math

def dis(x1, x2, y1, y2):
    distancia = math.sqrt((float(x2)-float(x1))**2 + (float(y2)-float(y1))**2)
    return distancia*0.2

def cargar_nodos(path, grafo):
    with open(path, "r", encoding="utf-8") as nodos:
        nodos = nodos.readlines()
        nodos.pop(0)
        for n in nodos:
            n = n.strip().split(";")
            grafo.add_node(int(n[0]))
            grafo.nodes[int(n[0])]["x"] = float(n[1])
            grafo.nodes[int(n[0])]["y"] = float(n[2])

def cargar_arcos(path, grafo):
    with open(path, "r", encoding="utf-8") as arcos:
        arcos = arcos.readlines()
        arcos.pop(0)
        for a in arcos:
            a = a.strip().split(";")
            x1 = grafo.nodes[int(a[0])]['x']
            y1 =grafo.nodes[int(a[0])]['y']
            x2 = grafo.nodes[int(a[1])]['x']
            y2 = grafo.nodes[int(a[1])]['y']
            distancia = dis(x1, x2, y1, y2)
            velocidad = sum(float(x) for x in a[2:])/len(a[2:])      
            tiempo = 60*distancia/velocidad
            if distancia != 0:
                grafo.add_edge(int(a[0]), int(a[1]))
                grafo.edges[int(a[0]), int(a[1])]['weight'] = tiempo

def cargar_grafo(path1, path2):
    grafo = nx.Graph()
    cargar_nodos(path1, grafo)
    cargar_arcos(path2, grafo)
    return grafo

if __name__ == "__main__":
    grafo = cargar_grafo("Datos/nodos.csv", "Datos/arcos.csv")
    length, path = nx.single_source_dijkstra(grafo, 0)
    print(length[2184])