import random
import time
from grafo import Grafo
import threading 
import copy


# REESCALAR MINUTOS A SEGUNDOS (60 min en la vida real --> 60 segundos en la simualción)}
# DESPUÉS HAY QUE REESCALAR

class Ambulancia:
    # Generador de ID
    ID = 0
    @classmethod
    def incr(self):
        self.ID += 1
        return self.ID

    def __init__(self, x, y):
        self.id = self.incr()
        self.x = x
        self.y = y
        self.disponibe = True
        self.thread_viaje = None
  
    def viajar(self, tiempo_viaje, evento):
        self.disponibe = False
        time.sleep(tiempo_viaje)
        self.atender(evento)
        # Terminar evento (no se como borrar el evento del dic de simulación y no se si es necesario)
        # Colocar la ambulancia como disponible 
    
    def atender(self, evento):
        # time.sleep() distribución tiempo de antencion
        evento.atendido  = True
            
class Base:
    def __init__(self, x, y, nodo_cercano):
        self.x = x
        self.y = y
        self.threads_ambulancias = []
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

    def asignar(self, evento, tiempo_viaje):
        ambulancia_asignada = [ambulancia for ambulancia in 
                             self.ambunalcias if ambulancia.disponibe][0]
        thread_ambulancia = threading.Thread(target=ambulancia_asignada.comenzar_viaje,args=(evento, tiempo_viaje))
        # Iniciamos el viaje de las ambulancisa
        self.ambulancias.append(thread_ambulancia)
        thread_ambulancia.start()
        

class Evento:
    # Generador de ID
    ID = 0
    @classmethod
    def incr(self):
        self.ID += 1
        return self.ID

    def __init__(self, x, y):
        self.id = self.incr()
        self.x = x
        self.y = y
        self.atendido = False


class CentroMedico:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Control:
    def __init__(self, x, y):
        self.bases = {}
        self.waze = Grafo("Datos/nodos.csv", "Datos/arcos.csv")
    
    def generar_entidades(self):
        # Crear bases, ambulancias y centros
        pass

    def asignar_ambulancia(self, evento):
        # Obtenemos el nodo cercano al evento
        nodo_evento = self.grafo.nodo_cercano(evento.x, evento.y)
        # Corremos Dijsktra
        self.grafo.tiempo_minimo(nodo_evento)
        # Seleccionamos la base a menor tiempo
        bases_disponibles  = [base for base in self.bases if base.ambulancias_disponibles]
        base_asignada =  bases_disponibles.sort(key = lambda x: x.nodo_cercano.tiempo)[0]
        tiempo = copy.copy(base_asignada.nodo_cercano.tiempo)
        base_asignada.asignar(evento, tiempo)

        self.grafo.reiniciar_caminos()
      
class Simmulacion:

    lock_evento = threading.Lock()

    def __init__(self):
        self.activa =  True 
        self.control = Control()
        self.eventos = {}
        generador_eventos = threading.Thread(name="Generador Eventos", target=self.crear_eventos)
    
    def crear_eventos(self):
        while self.activa == True:
            tiempo_espera = random.exponential(1/3) # Beta de 1/3 --> 1 llamada cada 3 min
            time.sleep(tiempo_espera)
            x = random.uniform(-71349005853253000, 79640174915830800)
            y = random.uniform(-77026387347217800, 74964947847257300)
            evento = Evento(self, x, y)

            # No se si es necesario guardar los eventos
            self.eventos[evento.id] = evento

            with self.lock_evento:
                self.notificar_evento(evento)

    def notificar_evento(self, evento):
        self.control.asignar_ambulancia(evento)

    def simular(self):
        pass


    