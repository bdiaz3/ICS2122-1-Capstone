import numpy.random as npr
import random
from grafo import Grafo
import time
import copy
from collections import deque
from datetime import datetime, timedelta
from parametros import TIEMPO_SIMULACION, TASA_LLEGADA, TIEMPO_DESPACHO, MU_ATENCION, SIGMA_ATENCION, AMBULANCIAS_X_BASE
from cargar_datos import cargar_bases, cargar_centros
from grafo_networkx import cargar_grafo
import networkx as nx
from grillas import Mapa

# Aca se puede cambiar la seed para probar distintos escenarios

class Ambulancia:
    # Generador de ID
    ID = 0
    @classmethod
    def incr(self):
        self.ID += 1
        return self.ID

    def __init__(self):
        self.id = self.incr()
        self.disponible = True
        self.evento_asignado = None 
        self.hora_llegada = 0
        self.centro_asignado = None
        self.retorno_forzado = False
        self.hora_salida = 0
        self.tiempo_retorno = 0
        self.tiempos = []
        # Setamos variabels para registrar datos
        self.llamadas_atendidas = 0
        self.disponible_en_centro = False

class Base:
    # Generador de ID
    ID = 0
    @classmethod
    def incr(self):
        self.ID += 1
        return self.ID

    def __init__(self, x, y, nodo_cercano):
        self.id = self.incr()
        self.x = x
        self.y = y
        self.nodo_cercano = nodo_cercano
        self.ambulancias = {} # ID, ambulancia 
        self.ambulancias_disponibles = True
        self._ambulancias_utilizadas = 0
        self.disponible_en_centro = False
        
        # Se crea 1 ambulancia por base
        for i in range(AMBULANCIAS_X_BASE):
            ambulancia = Ambulancia()
            self.ambulancias[ambulancia.id] = ambulancia

    @property
    def ambulancias_utilizadas(self):
        return self._ambulancias_utilizadas

    @ambulancias_utilizadas.setter
    def ambulancias_utilizadas(self, other):
        if other >= len(self.ambulancias.values()):
            self._ambulancias_utilizadas = len(self.ambulancias)
            self.ambulancias_disponibles = False

        elif other < len(self.ambulancias.values()):
            self._ambulancias_utilizadas = other
            self.ambulancias_disponibles = True

    def asignar_ambulancia(self, evento, hora_llegada, centro_asignado, hora_salida, id= None):
        if id == None:
            ambulancia_seleccionada = [ambulancia for ambulancia in self.ambulancias.values() if ambulancia.disponible][0]
        else:
            ambulancia_seleccionada = self.ambulancias[id]
        self.ambulancias_utilizadas += 1
        ambulancia_seleccionada.disponible = False
        ambulancia_seleccionada.disponible_en_centro = False
        ambulancia_seleccionada.evento_asignado = evento
        ambulancia_seleccionada.hora_llegada = hora_llegada
        ambulancia_seleccionada.hora_salida = hora_salida
        ambulancia_seleccionada.centro_asignado = centro_asignado
        print(f"A la Ambulancia {ambulancia_seleccionada.id} se le asigna el evento {evento.id}\n")
        return ambulancia_seleccionada.id
    
    def terminar_atencion(self, id_ambulancia, reasignacion =  False):
        if not self.ambulancias[id_ambulancia].retorno_forzado and not reasignacion:
            print(f"La Ambulancia {self.ambulancias[id_ambulancia].id} volvió a la base luego de antender el evento {self.ambulancias[id_ambulancia].evento_asignado.id}\n")
        elif self.ambulancias[id_ambulancia].retorno_forzado and not reasignacion:
            print(f"La Ambulancia {self.ambulancias[id_ambulancia].id} regresó a la base porque había otra más cerca del evento")
        self.ambulancias[id_ambulancia].disponible = True
        self.ambulancias[id_ambulancia].retorno_forzado = False
        self.ambulancias[id_ambulancia].evento_asignado = None
        self.ambulancias[id_ambulancia].centro_asignado = None
        self.ambulancias_utilizadas -= 1
        self.ambulancias[id_ambulancia].tiempos.append((self.ambulancias[id_ambulancia].hora_llegada - self.ambulancias[id_ambulancia].hora_salida)/timedelta(minutes=1))
        self.ambulancias[id_ambulancia].hora_salida = 0
        self.ambulancias[id_ambulancia].hora_llegada = 0
        
    def __repr__(self):
        return f"{str(self.x) ,str(self.y)}"

class Evento:
    # Generador de ID
    ID = 0
    @classmethod
    def incr(self):
        self.ID += 1
        return self.ID

    def __init__(self, tiempo_inicio, grilla):
        self.id = self.incr()
        self.tiempo_inicio = tiempo_inicio
        self.x = npr.uniform(grilla.x_min, grilla.x_max)
        self.y = npr.uniform(grilla.y_min, grilla.y_max)
        self.tiempo_espera = 0
        self.tiempo_despacho = npr.exponential(TIEMPO_DESPACHO) # Desde que ocurre la llamada hasta que se encuentra la ambulancia
        self.tiempo_atencion = npr.lognormal(MU_ATENCION, SIGMA_ATENCION) # Atencion Llega la ambulancia y se atiende 
       
    def __repr__(self):
        return str(self.id)

class CentroMedico:
    def __init__(self, x, y, nodo_cercano):
        self.x = x
        self.y = y
        self.nodo_cercano = nodo_cercano

class Control:
    def __init__(self):
        self.bases = []
        self.centros = []
        self.grafo = Grafo("Datos/nodos.csv", "Datos/arcos.csv")
        self.grafo2 = cargar_grafo("Datos/nodos.csv","Datos/arcos.csv")
        self.base_evento = []
        self.centro_evento = []
        self.rutas = []
        
    def asignar_base(self, evento, tiempo_actual, cola=False):

        # Obtenemos el nodo cercano al evento
        nodo_evento, tiempo_nodo = self.grafo.nodo_cercano(evento.x, evento.y)

        # Corremos Dijsktra para el evento
        length, ruta = nx.single_source_dijkstra(self.grafo2, nodo_evento.id)
                
        # Seleccionamos la base a menor tiempo
        bases_disponibles  = [base for base in self.bases if base.ambulancias_disponibles]

        # Si es que hay ambulancias disponibles
        if bases_disponibles:
            bases_disponibles.sort(key=lambda x: length[x.nodo_cercano.id])
            base_asignada = bases_disponibles[0]
            tiempo_base = copy.copy(length[base_asignada.nodo_cercano.id])
            tiempo_base += tiempo_nodo
            self.base_evento.append((evento.x, evento.y, base_asignada.x, base_asignada.y))
            self.rutas.append(ruta[base_asignada.nodo_cercano.id])

            # Seleccionamos el centro medico de menor tiempo
            centros = [centro for centro in self.centros]
            centros.sort(key=lambda x: length[x.nodo_cercano.id])
            centro_asignado = centros[0]
            tiempo_centro = copy.copy(length[centro_asignado.nodo_cercano.id])
            id_ambulancia = base_asignada.asignar_ambulancia(evento, tiempo_actual + timedelta(minutes = int(tiempo_base)), centro_asignado, tiempo_actual)

            # Corresmos Dijsktra para ir del Centro Medico a la Base
            length, _ = nx.single_source_dijkstra(self.grafo2, centro_asignado.nodo_cercano.id)
            tiempo_retorno = length[base_asignada.nodo_cercano.id]
            base_asignada.ambulancias[id_ambulancia].tiempo_retorno = tiempo_retorno

            return (tiempo_base + evento.tiempo_despacho + 
                     + evento.tiempo_atencion + tiempo_centro, tiempo_retorno, id_ambulancia, base_asignada, tiempo_base)

        bases_centro_disponible = []
        for base in self.bases:
            for id_ambulancia, ambulancia in base.ambulancias.items():
                if ambulancia.disponible_en_centro:
                    bases_centro_disponible.append((ambulancia, base))

        if bases_centro_disponible and cola:
            bases_centro_disponible.sort(key=lambda x: length[x[0].centro_asignado.nodo_cercano.id])
            base_asignada = bases_centro_disponible[0][1]
            ambulancia_asignada = bases_centro_disponible[0][0]
            id_ambulancia = ambulancia_asignada.id
            tiempo_centro_evento = copy.copy(length[ambulancia_asignada.centro_asignado.nodo_cercano.id])
            tiempo_centro_evento += tiempo_nodo
            self.centro_evento.append((evento.x, evento.y, ambulancia_asignada.centro_asignado.x, ambulancia_asignada.centro_asignado.y))
            self.rutas.append(ruta[ambulancia_asignada.centro_asignado.nodo_cercano.id])

            # Seleccionamos el centro medico de menor tiempo
            centros = [centro for centro in self.centros]
            centros.sort(key=lambda x: length[x.nodo_cercano.id])
            centro_asignado = centros[0]
            tiempo_centro = copy.copy(length[centro_asignado.nodo_cercano.id])
            base_asignada.asignar_ambulancia(evento, tiempo_actual + timedelta(minutes = int(tiempo_centro_evento)), centro_asignado, tiempo_actual, ambulancia_asignada.id )

            # Corresmos Dijsktra para ir del Centro Medico a la Base
            length, _ = nx.single_source_dijkstra(self.grafo2, centro_asignado.nodo_cercano.id)
            tiempo_retorno = length[base_asignada.nodo_cercano.id]
            base_asignada.ambulancias[id_ambulancia].tiempo_retorno = tiempo_retorno

            return (tiempo_centro_evento + evento.tiempo_despacho + 
                     + evento.tiempo_atencion + tiempo_centro, tiempo_retorno, id_ambulancia, base_asignada, tiempo_centro_evento)

        # Si no hay ambulancias disponibles
        return (None, None, None, None, None)

    def cargar_entidades(self):
        bases =  cargar_bases()
        for base in bases:
            nodo_cercano, _ = self.grafo.nodo_cercano(base[0],base[1])
            self.bases.append(Base(base[0], base[1], nodo_cercano)) #se asigna nodo más cercano a la base
        for centro in cargar_centros():
            nodo_cercano, _ = self.grafo.nodo_cercano(centro[0],centro[1]) #se asigna nodo más cercano al centro
            self.centros.append(CentroMedico(centro[0],centro[1],nodo_cercano))
        print("SE CARGAN LAS BASES Y LOS CENTROS EN LA CIUDAD\n")

class Simmulacion:

    def __init__(self):
        self.activa =  True 
        self.control = None
        self.mapa = None

        self.crear_entidades()

        date = datetime(2021, 9, 26)
        newdate = date.replace(hour=0)
        
        # Seteamos variable de tiempo
        self.tiempo_actual = newdate
        self.tiempo_maximo = newdate + timedelta(hours = TIEMPO_SIMULACION)

        # Seteamos cola para llamadas
        self.cola = deque()
        
        # Seteamos inputs de distribiciones y estrucutras de la simulación
        self.prox_evento_llega = self.tiempo_actual + timedelta(minutes = int(npr.exponential(1/TASA_LLEGADA)))
        self.tiempos_ambulancias = [] # Lista de la forma [[tiempo, id_mbulancia, base_asignada]]
        self.tiempos_retorno = [] # Lsita con la hora de llegada de retorno
        self.lista_tiempos_respuesta = []
        self.tiempos_sin_cola = []

        # Seteamos datos que utilizaremos para llevar registro 
        self.atenciones = 0 # Se considera el evento entero
        
    @property
    def proxima_accion(self):
        print(self.cola)
        print([[ambulancia.id for _,ambulancia in base.ambulancias.items() if ambulancia.disponible]for base in self.control.bases])
        print([[(ambulancia.id, ambulancia.evento_asignado.id) for _,ambulancia in base.ambulancias.items() if not ambulancia.disponible and ambulancia.evento_asignado != None]for base in self.control.bases])
        if len(self.tiempos_ambulancias) > 0:
            self.tiempos_ambulancias.sort(key = lambda x: x[0])
        if len(self.tiempos_retorno) > 0:
            self.tiempos_retorno.sort(key = lambda x: x[0])
        print(self.tiempos_ambulancias)
        print(self.tiempos_retorno)
        print(self.prox_evento_llega)
        print(f"Proxima Acción")
        if len(self.tiempos_ambulancias) > 0 and len(self.tiempos_retorno) > 0:

            self.tiempos_ambulancias.sort(key = lambda x: x[0])
            self.tiempos_retorno.sort(key = lambda x: x[0])

            if self.tiempos_ambulancias[0][0] <= self.prox_evento_llega:
                if self.tiempos_ambulancias[0][0] < self.tiempos_retorno[0][0]:
                    # Termina una ambulancia
                    min_ambulancias = self.tiempos_ambulancias.pop(0)
                    return ("Fin Atencion", min_ambulancias)

                elif self.tiempos_ambulancias[0] == self.tiempos_retorno[0]:
                    min_retornos = self.tiempos_retorno.pop(0)
                    min_ambulancias = self.tiempos_ambulancias.pop(0)
                    return ("Retorno a Base", min_retornos)

                else:
                    # Retorno de una ambulancia
                    min_retornos = self.tiempos_retorno.pop(0)
                    return("Retorno a Base", min_retornos)

            elif self.tiempos_ambulancias[0][0] > self.prox_evento_llega:
                if self.tiempos_retorno[0][0] < self.prox_evento_llega:
                    # Retorno de una ambulancia
                    min_retornos = self.tiempos_retorno.pop(0)
                    return("Retorno a Base", min_retornos)
                else:
                    return ("Generar evento", None)    
        
        elif len(self.tiempos_ambulancias) > 0 and len(self.tiempos_retorno) == 0:
            self.tiempos_ambulancias.sort(key = lambda x: x[0])
            if self.tiempos_ambulancias[0][0] <= self.prox_evento_llega:
                min_ambulancias = self.tiempos_ambulancias.pop(0)
                return ("Fin Atencion", min_ambulancias)
            else:
                return ("Generar evento", None)

        elif len(self.tiempos_retorno) > 0 and len(self.tiempos_ambulancias) == 0:
            self.tiempos_retorno.sort(key = lambda x: x[0])
            if self.tiempos_retorno[0][0] <= self.prox_evento_llega:
                    min_retornos = self.tiempos_retorno.pop(0)
                    return("Retorno a Base", min_retornos)
            else:
                return ("Generar evento", None)       
            
        # Generación evento
        return ("Generar evento", None)

    def generar_evento(self):
        self.tiempo_actual = self.prox_evento_llega
        self.prox_evento_llega = self.tiempo_actual + timedelta(minutes = int(npr.exponential(1/TASA_LLEGADA)))
        grilla = self.mapa.seleccionar_grilla()
        evento = Evento(self.tiempo_actual, grilla)
        print(f"\nSe genera el evento {evento.id} en la ubicación {(evento.x , evento.y)}\n")
        # NO HABIA COLA
        if  len(self.cola) == 0:
            # Asigna la base más cercana al evento con ambulancias disponiblesS
            tiempo_total, tiempo_retorno, id_ambulancia, base_asignada, tiempo_base = self.control.asignar_base(evento, self.tiempo_actual)  
            # Habían ambulancias disponibles
            if tiempo_total != None:
                for elem in self.tiempos_retorno:
                    if elem[1] == base_asignada.ambulancias[id_ambulancia].id:
                        self.tiempos_retorno.remove(elem)
                self.tiempos_ambulancias.append([self.tiempo_actual + timedelta(minutes = int(tiempo_total)), id_ambulancia, base_asignada])
                self.tiempos_retorno.append([self.tiempo_actual + timedelta(minutes = int(tiempo_total+tiempo_retorno)), id_ambulancia, base_asignada])
            else:
                print(f"Se agrega a la cola el evento {evento.id}\n")
                self.cola.append(evento)
                
        else:
            print(f"Se agrega a la cola el evento {evento.id}\n")
            self.cola.append(evento)

            
    def fin_atencion(self, tiempo, id_ambulancia, base_asignada):
        print(id_ambulancia, base_asignada.ambulancias[id_ambulancia].evento_asignado)
        print(f"La ambulancia {id_ambulancia} ha terminado su atención del evento {base_asignada.ambulancias[id_ambulancia].evento_asignado.id}")
        self.tiempo_actual = tiempo
        mejoras = []
        ambulancia_disponible = base_asignada.ambulancias[id_ambulancia]
        centro =  base_asignada.ambulancias[id_ambulancia].centro_asignado
        if centro != None:
            nodo_centro = centro.nodo_cercano
        # Iteramos sobre las ambulancias 
        for base in self.control.bases:
            for _, ambulancia_viaje in base.ambulancias.items():
                evento = ambulancia_viaje.evento_asignado
                if evento != None:
                    # Obtenemos el nodo cercano al evento
                    nodo_evento, _ = self.control.grafo.nodo_cercano(evento.x, evento.y)
                    # Corremos Dijsktra para el evento
                    length, _ = nx.single_source_dijkstra(self.control.grafo2, nodo_evento.id)

                    tiempo_centro_evento = timedelta(minutes = int(length[nodo_centro.id]))
                    tiempo_viaje_faltante = ambulancia_viaje.hora_llegada - self.tiempo_actual

                    if tiempo_centro_evento < tiempo_viaje_faltante:
                        delta = tiempo_viaje_faltante - tiempo_centro_evento
                        mejoras.append([ambulancia_viaje, length[nodo_centro.id], delta, base, evento])

        # Encontramos una mejora
        if len(mejoras) > 0:
            mejoras.sort(key = lambda x: x[2], reverse = True)
            seleccion =  mejoras.pop(0)
            ambulancia_viaje, tiempo_centro_evento, base_viaje, evento = seleccion[0], seleccion[1], seleccion[3], seleccion[4]
            print(f"La ambulancia {id_ambulancia} puede llegar antes al evento {ambulancia_viaje.evento_asignado.id}, por lo que se reasignó.")
            time.sleep(5)
            # Desocupamos la ambulancia que está en el centro
            elem = [elem for elem in self.tiempos_retorno if elem[1] == id_ambulancia][0]
            self.tiempos_retorno.remove(elem)
            ambulancia_disponible.llamadas_atendidas += 1
            base_asignada.terminar_atencion(id_ambulancia, True)

            # Le asignamos el nuevo evento
            base_asignada.asignar_ambulancia(evento, self.tiempo_actual + 
                                timedelta(minutes = int(tiempo_centro_evento)), ambulancia_viaje.centro_asignado, self.tiempo_actual, id_ambulancia)
            self.tiempos_ambulancias.append([self.tiempo_actual + timedelta(minutes = int(tiempo_centro_evento)), id_ambulancia, base_asignada])
            
            # Ahora necesitamos el tiempo de retorno
            nodo_centro =  base_asignada.ambulancias[id_ambulancia].centro_asignado.nodo_cercano
            # Corremos Dijsktra para el centro
            length, _ = nx.single_source_dijkstra(self.control.grafo2, nodo_centro.id)
            tiempo_retorno = length[base_asignada.nodo_cercano.id]
            self.tiempos_retorno.append([self.tiempo_actual + timedelta(minutes = int(tiempo_centro_evento+tiempo_retorno)), id_ambulancia, base_asignada])
            
            print(f"La ambulancia {ambulancia_viaje.id} va en camino a la base por reasignacion.")
             # Lo eliminamos de la lista de ambulancias
            for elem in self.tiempos_ambulancias:
                if elem[1] == ambulancia_viaje.id:
                    self.tiempos_ambulancias.remove(elem)

            for elem in self.tiempos_retorno:
                if elem[1] == ambulancia_viaje.id:
                    self.tiempos_retorno.remove(elem)

            # Desocupamos la ambulancia en viaje
            ambulancia_viaje.retorno_forzado = True
            tiempo_retorno2 = self.tiempo_actual-ambulancia_viaje.hora_salida
            self.tiempos_retorno.append([self.tiempo_actual + tiempo_retorno2, ambulancia_viaje.id, base_viaje])
            ambulancia_viaje.evento_asignado = None


        else:
            ambulancia_disponible.disponible_en_centro =  True

        print("")

    def retorno_a_base(self, tiempo_retorno, id_ambulancia, base_asignada):
        self.tiempo_actual = tiempo_retorno
        if not base_asignada.ambulancias[id_ambulancia].retorno_forzado:
            base_asignada.ambulancias[id_ambulancia].llamadas_atendidas += 1
        base_asignada.terminar_atencion(id_ambulancia)
    
    def actualizar_cola(self):
        print(f"Se actualiza la cola")
        evento = self.cola.popleft()
        # Asigna la base más cercana al evento con ambulancias disponibles
        evento.tiempo_espera = self.tiempo_actual - evento.tiempo_inicio 
        tiempo_total, tiempo_retorno, id_ambulancia, base_asignada, tiempo_base = self.control.asignar_base(evento, self.tiempo_actual, True)
        if tiempo_total != None:
            for elem in self.tiempos_retorno:
                if elem[1] == base_asignada.ambulancias[id_ambulancia].id:
                    self.tiempos_retorno.remove(elem)
            self.tiempos_ambulancias.append([self.tiempo_actual + timedelta(minutes = int(tiempo_total)), id_ambulancia, base_asignada])
            self.tiempos_retorno.append([self.tiempo_actual + timedelta(minutes = int(tiempo_total)) + timedelta(minutes = int(tiempo_retorno)), id_ambulancia, base_asignada])
        else:
            self.cola.appendleft(evento)

    def simular(self):
        print("COMIENZA LA SIMULACIÓN\n")
        tiempo_inicial = time.time()
        while self.tiempo_actual < self.tiempo_maximo:
            estado, params  = self.proxima_accion
            print(estado)
            if estado == "Fin Atencion":
                tiempo, id_ambulancia, base_asignada = params[0], params[1], params[2]
                self.fin_atencion(tiempo, id_ambulancia, base_asignada)
                if self.cola:
                    self.actualizar_cola()
            elif estado == "Generar evento":
                self.generar_evento()
            elif estado == "Retorno a Base":
                tiempo_retorno, id_ambulancia, base_asignada = params[0], params[1], params[2]
                self.retorno_a_base(tiempo_retorno, id_ambulancia, base_asignada)
                if self.cola:
                    self.actualizar_cola()
        
        for base in self.control.bases:
            contador = 0
            for ambulancia in base.ambulancias.values():
                contador += ambulancia.llamadas_atendidas
                self.atenciones += ambulancia.llamadas_atendidas

            print(f"La base {base.id} atendió {contador} llamadas en total")
        print(f"\nLARGO COLA FINAL {len(self.cola)}")      
        print(f"SE REALIZARON UN TOTAL DE  {self.atenciones} atenciones")

        lista_tiempos_respuesta = []
        for base in self.control.bases:
            for ambulancia in base.ambulancias.values():
                for tiempo in ambulancia.tiempos:
                    lista_tiempos_respuesta.append(tiempo) 
        print(f"TIEMPO DE RESPUESTA PROMEDIO:{sum(tiempo for tiempo in lista_tiempos_respuesta)/len(lista_tiempos_respuesta)}")
        # print(f"TIEMPO DE RESPUESTA PROMEDIO SIN COLA:{sum(tiempo for tiempo in self.tiempos_sin_cola)/len(self.tiempos_sin_cola)}")
        print(f"TIEMPO TOTAL DE LA SIMULACIÓN:{time.time()-tiempo_inicial}")
        print("FIN SIMULACIÓN")
        # self.guardar_tiempo_promedio("Datos Simulacion/tiempo_promedio_viejo.csv", "Datos Simulacion/promedio_sin_cola_viejo.csv")
        # self.guardar_tiempos_respuesta("Datos Simulacion/t_respuesta_modelo_viejo.csv", "Datos Simulacion/t_respuesta_sin_cola_viejo.csv")
        self.guardar_base_evento("Datos Simulacion/base_evento.csv")
        
    def crear_entidades(self):
        self.control = Control()
        self.control.cargar_entidades()
        self.mapa = Mapa()
    
    def guardar_tiempos_respuesta(self, path1, path2):
        with open(path1,"w") as archivo:
            for tiempo in self.lista_tiempos_respuesta:
                archivo.write(f"{tiempo}\n")
        with open(path2,"w") as archivo:
            for tiempo in self.tiempos_sin_cola:
                archivo.write(f"{tiempo}\n")

    def guardar_tiempo_promedio(self, path1, path2):
        tiempo_promedio  = sum(self.lista_tiempos_respuesta)/len(self.lista_tiempos_respuesta)
        with open(path1,"a+") as archivo:
            archivo.write(f"{tiempo_promedio}\n")
            
        promedio_sin_cola  = sum(self.tiempos_sin_cola)/len(self.tiempos_sin_cola)
        with open(path2,"a+") as archivo:
            archivo.write(f"{promedio_sin_cola}\n")

    def guardar_base_evento(self, path):
        with open(path, "w") as archivo:
            for b in self.control.base_evento:
                archivo.write(f"{b[0]};{b[1]};{b[2]};{b[3]}\n")
                
        with open("Datos Simulacion/rutas_base_evento.csv", "w") as archivo:
            for ruta in self.control.rutas:
                for i in range(len(ruta)):
                    if i != (len(ruta)-1):
                        archivo.write(f"{self.control.grafo.nodos[ruta[i]].x}, {self.control.grafo.nodos[ruta[i]].y} ;")
                    else:
                        archivo.write(f"{self.control.grafo.nodos[ruta[i]].x}, {self.control.grafo.nodos[ruta[i]].y}\n")


if __name__ == "__main__":
    inicio = 1
    fin = 1
    n = inicio
    while n <= fin:
        npr.seed(n)
        random.seed(n)
        sim = Simmulacion()
        sim.simular()
        print(f"Fin seed {n}\n")
        Evento.ID = 0
        Base.ID = 0
        Ambulancia.ID = 0
        time.sleep(1)
        n += 1