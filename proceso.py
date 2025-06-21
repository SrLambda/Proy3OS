import time
import random

class Proceso:
    def __init__(self, pid,nombre="", tiempo_llegada=0, duracion=0, tamano_memoria=0,):
        self.pid = pid  # ID del proceso
        self.nombre = nombre  # Asegúrate de tener este atributo
        self.tiempo_llegada = tiempo_llegada  # Momento en que el proceso llega al sistema 
        self.duracion = duracion  # Tiempo total de CPU que necesita el proceso (CPU burst) 
        self.tiempo_restante = duracion # Tiempo restante de ejecución
        self.tamano_memoria = tamano_memoria # Tamaño en memoria que requiere el proceso 
        self.estado = "Nuevo"  # Estado actual del proceso (Nuevo, Listo, Ejecutando, Esperando, Terminado) 
        self.tiempo_inicio_ejecucion = -1 # Para calcular tiempo de respuesta
        self.tiempo_finalizacion = -1 # Para calcular tiempo de retorno
        self.tiempo_espera = 0 # Para calcular tiempo de espera
        self.tiempo_en_cpu = 0 # Tiempo que el proceso ha estado en CPU
        self.tiempo_quantum_actual = 0 # Tiempo ejecutado en el quantum actual (para Round Robin)
        self.bloques_memoria_asignados = [] # Lista de bloques de memoria asignados

    def __repr__(self):
        return f"P{self.pid} (Estado: {self.estado}, Dur: {self.duracion}, Rest: {self.tiempo_restante}, Mem: {self.tamano_memoria})"

    def actualizar_tiempo_restante(self, tiempo_unidad):
        """Actualiza el tiempo restante del proceso"""
        self.tiempo_restante = max(0, self.tiempo_restante - tiempo_unidad)
        if self.tiempo_restante == 0:
            self.set_estado("terminado")
        print(f"[{self.nombre}] Estado final: {self.estado}")

    def set_estado(self, nuevo_estado):
        self.estado = nuevo_estado

    def reiniciar_quantum(self):
        """Reinicia el tiempo de quantum actual para Round Robin"""
        self.tiempo_quantum_actual = 0


