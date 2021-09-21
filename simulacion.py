from random import uniform, random, seed, randint, gauss, expovariate
from typing import Collection
import numpy as np
import time as tm
import pandas as pd
import math 
from collections import deque
from datetime import datetime, time, timedelta
from scipy.stats import fisk

seed(1)

events = list()
prob_events = list()

with open("Datos/eventos.csv", 'r') as file:
    next(file)
    for line in file:
        linea = line.strip().split(";")
        events.append(linea)

prob_events = []

class Llamada:
    _id = 0
    def __init__(self, tiempo_instance):
        Llamada._id += 1
        self.id = Llamada._id
        self.hora_llegada = tiempo_instance
        self.ambulancia = None
        self.x = None
        self.y = None
        # self.tiempo_despacho = None
        # self.tiempo_derivacion = None
        # self.tiempo_atencion = None
    
    def generar_tiempo_abandono_sistema(self, tiempo_actual):
        self.hora_llegada = tiempo_actual + timedelta(minutes=int(uniform(0,1440)))
        
    def generar_coordenadas_llamadas(self):
        self.x = uniform(-71349005853253000, 79640174915830800)
        self.y = uniform(-77026387347217800, 74964947847257300)
        
    def __str__(self):
        return "Hora llegada {} llamada {}"-format(self.hora_llegada, self.id)
    
class System:
    def __init__(self, tiempo_simulacion, tasa_llegda, capacidad):
        date = datetime(2021, 21, 9)
        newdate = date.replace(hour=0)
        
        #seteamos variable de tiempo
        self.tiempo_actual = newdate
        self.tiempo_maximo = newdate + timedelta(hours = tiempo_simulacion)
        
        #seteamos inputs de distribiciones y estrucutras de la simulación
        self.tasa_llegada = tasa_llegda
        #aqui encontrar una distribución para las llamadas
        self.prox_llamada_llega = self.tiempo_actual + timedelta(minutes = int(fisk(4,7446,740,24,0)))
        self.capacidad_cola = capacidad
        self.cola = deque()
        #timedelta(minutes = int(fisk(4,7446,740,24,0)))
        
        # las variables para el cálculo de estadísticas se dejan en el constructor
        self.cantidad_llamadas = 0 # son los autos que llegan
        self.cantidad_llamadas_perdidas = 0
        self.terminadas = 0
        
        # manejamos una lista con todos los tiempos de una atención completa que se generan
        self.tiempos_atencion_completa = [[self.tiempo_actual.replace(year=3000), None]]
        
        
    # usamos properties para trabajar con mayor comodidad el atributo del proximo auto que termina de ser atendido
    @property
    def proxima_atencion_termina(self):
        # Esta la próxima persona que terminará de ser atendida con su tiempo asociado
        x, y = self.tiempos_atencion_completa[0]
        return x, y
        
    @property
    def proximo_evento(self):
        tiempos = [self.proximo_llamada_llega,
                   self.proxima_atencion_termina[0]]
        tiempo_prox_evento = min(tiempos)

        if tiempo_prox_evento >= self.tiempo_maximo:
            return "fin"
        eventos = ["llegada_llamada", "evento_completo"]
        return eventos[tiempos.index(tiempo_prox_evento)]    
    
    
    def llegar_llamada(self):
        time.sleep(0.4)
        self.tiempo_actual = self.prox_llamada_llega
        self.prox_llamada_llega = self.tiempo_actual + timedelta(minutes = int(fisk(4,7446,740,24,0)))
        llamada = Llamada(self.tiempo_actual)
        print("\r\r\033[92m[INGRESO ESTACION]\033[0m ha ingresado una llamada id: {0} {1}".format(llamada,self.tiempo_actual))
        
        if len(self.cola) == self.capacidad_cola:
            print("[COLA LLENA!!!] Se ha llenado la cola de espera para el sistema")
            self.cantidad_llamadas += 1
            self.cantidad_llamadas_perdidas += 1
        
        #si la ambulanca está libre ver que hacer aca
        # elif self.estacion["E1"] == None:
        #     #self.tiempo_sistema_vacio += (self.tiempo_actual - self.ultimo_tiempo_actual_vacio)
        #     self.estacion["E1"] = llamada
        #     self.estacion["E1"].estacion = "E1"
        #     self.estacion["E1"].generar_tiempo_abandono_taller(self.tiempo_actual)
        #     self.tiempos_abandono_taller.append((auto.tiempo_abandono_taller, llamada))
        #     self.tiempos_abandono_taller.sort(key=lambda z: datetime.strftime(z[0], "%Y-%m-%d-%H-%M"))
        #     print("\r\r\033[92m[INGRESO ESTACION]\033[0m ha ingresado un auto a E1 id: {} {}".format(
        #         self.estacion["E1"]._id, self.tiempo_actual))
        
        # self.cantidad_llamadas += 1
        else:
            self.cola.append(llamada)
            
    def evento_completo(self):
        time.sleep(0.4)
        self.tiempo_actual, llamada_termina = self.proxima_atencion_termina
        
        if len(self.cola) > 0:
            print("Se desocupa una ambulancia \n")#colocar id
            print("Se termina la llada id {}".format(llamada_termina))
            proxima_llamada = self.cola.popleft()
            print(proxima_llamada)
            proxima_llamada.ambulancia = llamada_termina.ambulancia
            self.llamada_pasa_a_ser_atendida(proxima_llamada, llamada_termina.ambulancia)
        else:
            print("La amulancia termina de atender la llamada id: {}, está desocupada pero"
                  "no hay llamadas en cola {}".format(llamada_termina._id, self.tiempo_actual))
            self.ambulancia[llamada_termina.estacion] = None
        self.tiempos_atencion_completa.pop(0)
        self.terminadas += 1
        
    def llamada_pasa_a_ser_atendida(self, llamada, e):
        time.sleep(0.4)
        self.ambulancia[e] = llamada
        self.ambulancia[e].generar_tiempo
        
    
    #motor de la simulacion
    def run(self):
        while self.tiempo_actual < self.tiempo_maximo:
            evento = self.proximo_evento
            if evento == "fin":
                self.tiempo_actual = self.tiempo_maximo
                break
            elif evento == "llegada_llamada":
                self.llegar_llamada()
            elif evento == "evento_completo":
                self.completar_evento()