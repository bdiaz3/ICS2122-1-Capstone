import numpy.random as npr
from grafo import Grafo
import time
import copy
from collections import deque
from datetime import datetime, timedelta
from parametros import TIEMPO_SIMULACION, TASA_LLEGADA, TIEMPO_DESPACHO, TIEMPO_DERIVACION, \
 MU_ATENCION, SIGMA_ATENCION, MAX_X, MAX_Y, MIN_X, MIN_Y
from cargar_datos import cargar_bases, cargar_centros

# Aca se puede cambiar la seed para probar distintos escenarios
npr.seed(15)

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

        # Setamos variabels para registrar datos
        self.llamadas_atendidas = 0

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
        print(f"A la Ambulancia {ambulancia_seleccionada.id} se le asigna el evento {evento.id}\n")
        return ambulancia_seleccionada.id
    
    def terminar_atencion(self, id_ambulancia):
        print(f"Terminó la Ambulancia {self.ambulancias[id_ambulancia].id} el evento {self.ambulancias[id_ambulancia].evento_asignado.id}\n")
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
        self.x = npr.uniform(MIN_X, MAX_X)
        self.y = npr.uniform(MIN_Y, MAX_Y)
        self.tiempo_espera = 0
        self.tiempo_despacho = npr.exponential(TIEMPO_DESPACHO) # Desde que ocurre la llamada hasta que se encuentra la ambulancia
        # self.tiempo_derivacion = npr.exponential(TIEMPO_DERIVACION) # Tiempo de traslado al centro de salud 
        self.tiempo_atencion = npr.lognormal(MU_ATENCION, SIGMA_ATENCION) # AtencLlega la ambulancia y se atiende 
       
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
        self.base_evento = []
        self.rutas = []
        
    def asignar_base(self, evento):

        # Obtenemos el nodo cercano al evento
        
        nodo_evento = self.grafo.nodo_cercano(evento.x, evento.y)
        # Corremos Dijsktra para el evento
        self.grafo.tiempo_minimo(nodo_evento.id)
                
        # Seleccionamos la base a menor tiempo
        bases_disponibles  = [base for base in self.bases if base.ambulancias_disponibles]

        # Si es que hay ambulancias disponibles
        if bases_disponibles:
            bases_disponibles.sort(key=lambda x: x.nodo_cercano.tiempo)
            base_asignada = bases_disponibles[0]
            tiempo_base = copy.copy(base_asignada.nodo_cercano.tiempo)
            self.base_evento.append((evento.x, evento.y, base_asignada.x, base_asignada.y))
            ruta = self.grafo.entregar_ruta(base_asignada.nodo_cercano.id, nodo_evento.id)
            self.rutas.append(ruta)
            if evento.id == 4:
                print(nodo_evento.x, nodo_evento.y)
                print(base_asignada.nodo_cercano.x, base_asignada.nodo_cercano.y)
                print(ruta)
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
            return (tiempo_base + evento.tiempo_despacho + 
                     + evento.tiempo_atencion + tiempo_centro + tiempo_retorno, id_ambulancia, base_asignada, tiempo_base)

        # Si no hay ambulancias disponibles
        return (None, None, None, None)

    def cargar_entidades(self):
        bases =  cargar_bases()
        for base in bases:
            nodo_cercano = self.grafo.nodo_cercano(base[0],base[1])
            self.bases.append(Base(base[0], base[1], nodo_cercano)) #se asigna nodo más cercano a la base
        for centro in cargar_centros():
            nodo_cercano = self.grafo.nodo_cercano(centro[0],centro[1]) #se asigna nodo más cercano al centro
            self.centros.append(CentroMedico(centro[0],centro[1],nodo_cercano))
        print("SE CARGAN LAS BASES Y LOS CENTROS EN LA CIUDAD\n")

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

        # Seteamos cola para llamadas
        self.cola = deque()
        
        # Seteamos inputs de distribiciones y estrucutras de la simulación
        self.prox_evento_llega = self.tiempo_actual + timedelta(minutes = int(npr.exponential(1/TASA_LLEGADA)))
        self.tiempos_ambulancias = [] # Lista de la forma [[tiempo, id_mbulancia, base_asignada]]
        self.lista_tiempos_respuesta = []

        #Seteamos datos que utilizaremos para llevar registro 
        self.atenciones = 0 #se considera el evento entero
        
    @property
    def proxima_accion(self):
        print(f"Proxima Acción")
        if len(self.tiempos_ambulancias) > 0 :
            self.tiempos_ambulancias.sort(key = lambda x: x[0])
            if self.tiempos_ambulancias[0][0] < self.prox_evento_llega:
                min_ambulancias = self.tiempos_ambulancias.pop(0)
                return ("Fin Atencion", min_ambulancias)
        return ("Generar evento", None)


    def generar_evento(self):
        self.tiempo_actual = self.prox_evento_llega
        self.prox_evento_llega = self.tiempo_actual + timedelta(minutes = int(npr.exponential(1/TASA_LLEGADA)))
        evento = Evento(self.tiempo_actual)
        print(f"\nSe genera el evento {evento.id} en la ubicación {(evento.x , evento.y)}\n")
        # NO HABIA COLA
        if  len(self.cola) == 0:
            # Asigna la base más cercana al evento con ambulancias disponiblesS
            tiempo_total, id_ambulancia, base_asignada, tiempo_base = self.control.asignar_base(evento)
            # Habían ambulancias disponibles
            if tiempo_total != None:
                self.lista_tiempos_respuesta.append(tiempo_base)
                self.tiempos_ambulancias.append([self.tiempo_actual + timedelta(minutes = int(tiempo_total)), id_ambulancia, base_asignada])
            else:
                print(f"Se agrega a la cola el evento {evento.id}\n")
                self.cola.append(evento)
        else:
            print(f"Se agrega a la cola el evento {evento.id}\n")
            self.cola.append(evento)

            
    def fin_atencion(self, tiempo, id_ambulancia, base_asignada):
        self.tiempo_actual = tiempo
        base_asignada.ambulancias[id_ambulancia].llamadas_atendidas += 1 
        base_asignada.terminar_atencion(id_ambulancia)
    
    def actualizar_cola(self):
        print(f"Se actualiza la cola")
        evento = self.cola.popleft()
        # Asigna la base más cercana al evento con ambulancias disponibles
        evento.tiempo_espera = self.tiempo_actual - evento.tiempo_inicio 
        tiempo_total, id_ambulancia, base_asignada, tiempo_base = self.control.asignar_base(evento)
        if tiempo_total != None:
            tiempo_respuesta = tiempo_base + (evento.tiempo_espera)/timedelta(minutes=1)
            self.lista_tiempos_respuesta.append(tiempo_respuesta)
            self.tiempos_ambulancias.append([self.tiempo_actual + timedelta(minutes = int(tiempo_total)), id_ambulancia, base_asignada])

    def simular(self):
        print("COMIENZA LA SIMULACIÓN\n")
        tiempo_inicial = time.time()
        while self.tiempo_actual < self.tiempo_maximo:
            estado, parametros  = self.proxima_accion
            if estado == "Fin Atencion":
                tiempo, id_ambulancia, base_asignada = parametros[0], parametros[1], parametros[2]
                self.fin_atencion(tiempo, id_ambulancia, base_asignada)
                if self.cola:
                    self.actualizar_cola()
            elif estado == "Generar evento":
                self.generar_evento()
        
        for base in self.control.bases:
            contador = 0
            for ambulancia in base.ambulancias.values():
                contador += ambulancia.llamadas_atendidas
                self.atenciones += ambulancia.llamadas_atendidas

            print(f"La base {base.id} atendió {contador} llamadas en total")
        print(f"\nLARGO COLA FINAL {len(self.cola)}")      
        print(f"SE REALIZARON UN TOTAL DE  {self.atenciones} atenciones")
        print(f"TIEMPO DE RESPUESTA PROMEDIO:{sum(tiempo for tiempo in self.lista_tiempos_respuesta)/len(self.lista_tiempos_respuesta)}")
        print(f"TIEMPO TOTAL DE LA SIMULACIÓN:{time.time()-tiempo_inicial}")
        print("FIN SIMULACIÓN")
        # self.guardar_tiempo_promedio("Datos Simulacion/tiempo_promedio_nuevo.csv")
        # self.guardar_tiempos_respuesta("Datos Simulacion/t_respuesta_modelo_viejo.csv")
        # self.guardar_base_evento("Datos Simulacion/base_evento.csv")
        
    def crear_entidades(self):
        self.control = Control()
        self.control.cargar_entidades()
    
    def guardar_tiempos_respuesta(self, path):
        with open(path,"w") as archivo:
            for tiempo in self.lista_tiempos_respuesta:
                archivo.write(f"{tiempo}\n")

    def guardar_tiempo_promedio(self, path):
        tiempo_promedio  = sum(self.lista_tiempos_respuesta)/len(self.lista_tiempos_respuesta)
        with open(path,"a+") as archivo:
            archivo.write(f"{tiempo_promedio}\n")

    def guardar_base_evento(self, path):
        with open(path, "w") as archivo:
            for b in self.control.base_evento:
                archivo.write(f"{b[0]};{b[1]};{b[2]};{b[3]}\n")
        with open("Datos Simulacion/rutas_base_evento.csv", "w") as archivo:
            for ruta in self.control.rutas:
                for i in range(len(ruta)):
                    if i != (len(ruta)-1):
                        archivo.write(f"{ruta[i][0], ruta[i][1], ruta[i][2]};")
                    else:
                        archivo.write(f"{ruta[i][0], ruta[i][1], ruta[i][2]}\n")


if __name__ == "__main__":
    sim = Simmulacion()
    sim.simular()