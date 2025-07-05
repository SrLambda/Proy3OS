import time
import random

class Proceso:
    def __init__(self, nombre="", tiempo_llegada=0, duracion=0, tamano_memoria=0, pid=None, color=None):
        self.pid = pid  
        self.nombre = nombre  
        self.tiempo_llegada = tiempo_llegada  
        self.duracion = duracion  
        self.tiempo_restante = duracion 
        self.tamano_memoria = tamano_memoria 
        self.estado = "nuevo"  
          
        self.tiempo_primer_ejecucion = None  
        self.tiempo_finalizacion = None      
        self.tiempo_espera = 0                
        self.tiempo_en_cpu = 0               
        self.tiempo_quantum_actual = 0       
        self.bloques_memoria_asignados = []
        self.color = self.generar_color()
        
        # Atributos para SWAP
        self.en_swap = False                
        self.bloques_swap_asignados = []     
        self.num_swaps_in = 0                 
        self.num_swaps_out = 0               
        self.tiempo_total_en_swap = 0         
        
        # Atributos para procesos hijos y programas
        self.es_proceso_hijo = False          # Indica si este proceso es hijo de un programa
        self.programa_padre = None            # Referencia al programa padre
        self.numero_hijo = 0                  # Número de hijo (1, 2, 3, etc.)         

    def __repr__(self):
        swap_info = "SWAP" if self.en_swap else "RAM"
        hijo_info = f" [Hijo {self.numero_hijo} de {self.programa_padre.nombre}]" if self.es_proceso_hijo else ""
        return f"P{self.pid} (Estado: {self.estado}, Dur: {self.duracion}, Rest: {self.tiempo_restante}, Mem: {self.tamano_memoria}, Ubicación: {swap_info}){hijo_info}, Color: {self.color}"
    

    def actualizar_tiempo_restante(self, tiempo_unidad):
        """Actualiza el tiempo restante del proceso"""
        self.tiempo_restante = max(0, self.tiempo_restante - tiempo_unidad)
        if self.tiempo_restante == 0:
            self.set_estado("terminado")
        print(f"[{self.nombre}] Estado final: {self.estado}")

    def set_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        
        # Si es un proceso hijo y acaba de terminar, notificar al programa padre
        if (self.es_proceso_hijo and nuevo_estado == "terminado" and 
            self.programa_padre is not None):
            self.programa_padre.marcar_proceso_completado()

    def reiniciar_quantum(self):
        """Reinicia el tiempo de quantum actual para Round Robin"""
        self.tiempo_quantum_actual = 0

    def generar_color(self):
        colorasignado = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        return colorasignado
