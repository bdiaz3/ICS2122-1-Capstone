import numpy.random as npr
from grafo import Grafo
import copy
from datetime import datetime, time, timedelta
from parametros import TIEMPO_SIMULACION, TASA_LLEGADA
from cargar_datos import cargar_bases, cargar_centros


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

class Base:
    def __init__(self, x, y, nodo_cercano):
        self.x = x
        self.y = y
        self.nodo_cercano = nodo_cercano
        self.ambulancias = {} # ID, ambulancia 
        self.ambulancias_disponibles = True
        self._ambulancias_utilizadas = 0
        
        # Se crea 1 ambulancia por base
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

    def asignar_ambulancia(self, evento):
        ambulancia_seleccionada = [ambulancia for ambulancia in self.ambulancias.values() if ambulancia.disponible][0]
        self.ambulancias_utilizadas += 1
        ambulancia_seleccionada.disponible = False
        ambulancia_seleccionada.evento_asignado = evento
        print(f"A la Ambulancia {ambulancia_seleccionada.id} se le asignó el evento {evento.id}")
        return ambulancia_seleccionada.id
    
    def terminar_atencion(self, id_ambulancia):
        print(f"Terminó la Ambulancia {self.ambulancias[id_ambulancia].id} el evento {self.ambulancias[id_ambulancia].evento_asignado.id}")
        self.ambulancias[id_ambulancia].disponible = True
        self.ambulancias[id_ambulancia].evento_asignado = None
        self.ambulancias_utilizadas -= 1

    def __repr__(self):
        return f"{str(self.x) ,str(self.y)}"

class Evento:
    # Generador de ID
    ID = 0
    @classmethod
    def incr(self):
        self.ID += 1
        return self.ID

    def __init__(self, tiempo_inicio):
        self.id = self.incr()
        self.tiempo_inicio = tiempo_inicio
        self.x = npr.uniform(-30.8300527, 162.663711)
        self.y = npr.uniform(-43.3526225, 121.858924)

        self.tiempo_despacho = npr.exponential(0.275455) # Desde que ocurre la llamada hasta que se encuentra la ambulancia
        self.tiempo_derivacion = npr.exponential(0.13123) # Tiempo de traslado al centro de salud 
        self.tiempo_atencion = npr.lognormal(2.5642, 0.65462) # AtencLlega la ambulancia y se atiende 

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

    def asignar_base(self, evento):

        # Obtenemos el nodo cercano al evento
        nodo_evento = self.grafo.nodo_cercano(evento.x, evento.y)

        # Corremos Dijsktra
        self.grafo.tiempo_minimo(nodo_evento.id)

        # Seleccionamos la base a menor tiempo
        bases_disponibles  = [base for base in self.bases if base.ambulancias_disponibles]

        bases_disponibles.sort(key=lambda x: x.nodo_cercano.tiempo)
        base_asignada = bases_disponibles[0]
        tiempo_base = copy.copy(base_asignada.nodo_cercano.tiempo)


        # Seleccionamos el centro medico de menor tiempo
        centros = [centro for centro in self.centros]
        centros.sort(key=lambda x: x.nodo_cercano.tiempo)
        centro_asignado = centros[0]
        tiempo_centro = copy.copy(centro_asignado.nodo_cercano.tiempo)


        id_ambulancia = base_asignada.asignar_ambulancia(evento)
        self.grafo.reiniciar_caminos()

        # Corresmos Dijsktra para ir del Centro Medico a la Base
        self.grafo.tiempo_minimo(centro_asignado.nodo_cercano.id)
        tiempo_retorno = base_asignada.nodo_cercano.tiempo
        self.grafo.reiniciar_caminos()

        # Falta asignar tiempo Evento-->Centro-->Base
        return (tiempo_base + evento.tiempo_despacho + 
                evento.tiempo_derivacion + evento.tiempo_atencion + tiempo_centro + tiempo_retorno
                                                                    , id_ambulancia, base_asignada)
    def cargar_entidades(self):
        bases =  cargar_bases()
        for base in bases:
            nodo_cercano = self.grafo.nodo_cercano(base[0],base[1])
            self.bases.append(Base(base[0], base[1], nodo_cercano))
        for centro in cargar_centros():
            nodo_cercano = self.grafo.nodo_cercano(centro[0],centro[1])
            self.centros.append(CentroMedico(centro[0],centro[1],nodo_cercano))

class Simmulacion:

    def __init__(self):
        self.activa =  True 
        self.control = None

        self.crear_entidades()

        date = datetime(2021, 9, 26)
        newdate = date.replace(hour=0)
        
        # Seteamos variable de tiempo
        self.tiempo_actual = newdate
        self.tiempo_maximo = newdate + timedelta(hours = TIEMPO_SIMULACION)

        # Seteamos inputs de distribiciones y estrucutras de la simulación
        self.prox_evento_llega = self.tiempo_actual + timedelta(minutes = int(npr.exponential(1/TASA_LLEGADA)))
        self.tiempos_ambulancias = [] # Lista de la forma [[tiempo, id_mbulancia, base_asignada]]

    @property
    def proxima_accion(self):
        if len(self.tiempos_ambulancias) > 0 :
            self.tiempos_ambulancias.sort(key = lambda x: x[0])
            min_ambulancias = self.tiempos_ambulancias.pop()
            if min_ambulancias[0] < self.prox_evento_llega:
                return ("Fin Atencion", min_ambulancias)
        return ("Generar evento", None)


    def llegar_evento(self):
        self.tiempo_actual = self.prox_evento_llega
        self.prox_evento_llega = self.tiempo_actual + timedelta(minutes = int(npr.exponential(1/TASA_LLEGADA)))
        evento = Evento(self.tiempo_actual)
        print(f"Se genera el evento {evento.id} en {(evento.x , evento.y)}")
        # Asigna la base más cercana al evento con ambulancias disponibles
        tiempo_total, id_ambulancia, base_asignada = self.control.asignar_base(evento)
        self.tiempos_ambulancias.append([self.tiempo_actual + timedelta(minutes = int(tiempo_total)), id_ambulancia, base_asignada])

    def fin_atencion(self, tiempo, id_ambulancia, base_asignada):
        self.tiempo_actual = tiempo
        base_asignada.terminar_atencion(id_ambulancia)

    def simular(self):
        while self.tiempo_actual < self.tiempo_maximo:
            estado, parametros  = self.proxima_accion
            if estado == "Fin Atencion":
                tiempo, id_ambulancia, base_asignada = parametros[0], parametros[1], parametros[2]
                self.fin_atencion(tiempo, id_ambulancia, base_asignada)
            elif estado == "Generar evento":
                self.llegar_evento()
    
    def crear_entidades(self):
        self.control = Control()
        self.control.cargar_entidades()


if __name__ == "__main__":
    sim = Simmulacion()
    sim.simular()