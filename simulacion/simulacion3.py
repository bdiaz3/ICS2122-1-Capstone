import random
import time
from grafo import Grafo
import copy
from datetime import datetime, time, timedelta
from parametros import TIEMPO_SIMULACION, TASA_LLEGADA


class Ambulancia:
    # Generador de ID
    ID = 0
    @classmethod
    def incr(self):
        self.ID += 1
        return self.ID

    def __init__(self):
        self.id = self.incr()
        self.disponibe = True

class Base:
    def __init__(self, x, y, nodo_cercano):
        self.x = x
        self.y = y
        self.nodo_cercano = nodo_cercano
        self.ambulacias = []
        self.ambulancias_disponibles = True
        self._ambulancias_utilizadas = 0

    @property
    def ambulancias_utilizadas(self):
        return self._ambulancias_utilizadas

    @ambulancias_utilizadas.setter
    def ambulancias_utilizadas(self, other):

        if other >= len(self.ambulacias):
            self._ambulancias_utilizadas = len(self.ambulancias)
            self.ambulancias_disponibles = False

        elif other < len(self.ambulacias):
            self._ambulancias_utilizadas = other
            self.ambulancias_disponibles = True

    def asignar_ambulancia(self, evento):
        # return ambulancia  asignada
        pass

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
        self.x = random.uniform(-30.8300527, 162.663711)
        self.y = random.uniform(-43.3526225, 121.858924)

        self.tiempo_despacho = None # Desde que ocurre la llamada hasta que se encuentra la ambulancia
        self.tiempo_derivacion = None # Tiempo de traslado al centro de salud 
        self.tiempo_atencion = None # Llega la ambulancia y se atiende 

class CentroMedico:
    def __init__(self, x, y, nodo_cercano):
        self.x = x
        self.y = y
        self.nodo_cercano = nodo_cercano
        pass

class Control:
    def __init__(self):
        self.bases = {}
        self.centros = {}
        self.waze = Grafo("Datos/nodos.csv", "Datos/arcos.csv")
    
    def generar_entidades(self):
        # Crear bases, ambulancias y centros
        pass

    def asignar_base(self, evento):

        # Obtenemos el nodo cercano al evento
        nodo_evento = self.grafo.nodo_cercano(evento.x, evento.y)

        # Corremos Dijsktra
        self.grafo.tiempo_minimo(nodo_evento.id)

        # Seleccionamos la base a menor tiempo
        bases_disponibles  = [base for base in self.bases if base.ambulancias_disponibles]
        base_asignada =  bases_disponibles.sort(key = lambda x: x.nodo_cercano.tiempo)[0]
        tiempo_base = copy.copy(base_asignada.nodo_cercano.tiempo)

        # Seleccionamos el centro medico de menor tiempo

        ambulancia = base_asignada.asignar_ambulancia(evento)
        self.grafo.reiniciar_caminos()
        # Falta asignar tiempo Evento-->Centro-->Base
        return (tiempo_base + evento.tiempo_despacho + 
                evento.tiempo_derivacion + evento.tiempo_atencion, ambulancia)
        

class Simmulacion:

    def __init__(self):
        self.activa =  True 
        self.control = Control()

        date = datetime(2021, 21, 9)
        newdate = date.replace(hour=0)
        
        # Seteamos variable de tiempo
        self.tiempo_actual = newdate
        self.tiempo_maximo = newdate + timedelta(hours = TIEMPO_SIMULACION)

        # Seteamos inputs de distribiciones y estrucutras de la simulación
        self.prox_evento_llega = self.tiempo_actual + timedelta(minutes = random.exponential(1/TASA_LLEGADA))
        self.tiempos_ambulancias = [] # Lista de la forma [[tiempo, Ambulancia]]

    @property
    def proxima_accion(self):
        min_ambulancias = self.tiempos_ambulancias.sort(key = lambda x: x[0])[0]
        if min_ambulancias[0] < self.prox_evento_llega:
            return ("Fin Atencion", min_ambulancias)
        return ("Llegada evento")


    def llegar_llamada(self):
        self.tiempo_actual = self.prox_evento_llega
        self.prox_evento_llega = self.tiempo_actual + timedelta(minutes = random.exponential(1/TASA_LLEGADA))
        evento = Evento(self.tiempo_actual)

        # Asigna la base más cercana al evento con ambulancias disponibles
        tiempo_viaje, ambulancia = self.control.asignar_base(evento)
        self.tiempos_ambulancias.append([self.tiempo_actual + timedelta(minutes = tiempo_viaje), ambulancia])

    def fin_atencion(self):
        # Terminar atencion, cambiar los valores de ambulancia y la disponibilidad en la base
        pass

    def simular(self):
        pass
    
    def crear_entidades(self):
        # Crear control
        # Crear Bases
        # Crear Ambulancias
        pass

