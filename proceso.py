import time
import random

class Proceso:
    def __init__(self, nombre="", tiempo_llegada=0, duracion=0, tamano_memoria=0, pid=None, color=None):
        self.pid = pid  # ID del proceso
        self.nombre = nombre  # Asegúrate de tener este atributo
        self.tiempo_llegada = tiempo_llegada  # Momento en que el proceso llega al sistema
        self.duracion = duracion  # Tiempo total de CPU que necesita el proceso (CPU burst)
        self.tiempo_restante = duracion # Tiempo restante de ejecución
        self.tamano_memoria = tamano_memoria # Tamaño en memoria que requiere el proceso
        self.estado = "nuevo"  # Estado actual del proceso (Nuevo, Listo, Ejecutando, Esperando, Terminado)
        
        # Atributos para estadísticas (INICIALIZADOS)
        self.tiempo_primer_ejecucion = None   # Tiempo de primera ejecución
        self.tiempo_finalizacion = None       # Tiempo de finalización
        self.tiempo_espera = 0                # Tiempo acumulado esperando
        self.tiempo_en_cpu = 0                # Tiempo en ejecución
        self.tiempo_quantum_actual = 0        # Tiempo en quantum actual
        self.bloques_memoria_asignados = []
        self.color = self.generar_color()

    def __repr__(self):
        return f"P{self.pid} (Estado: {self.estado}, Dur: {self.duracion}, Rest: {self.tiempo_restante}, Mem: {self.tamano_memoria}), Color: {self.color}"
    

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

    def generar_color(self):
        colorasignado = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        return colorasignado
