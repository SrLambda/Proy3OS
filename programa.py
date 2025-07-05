"""
Clase Programa - Representa un programa que puede dividirse en múltiples procesos
"""

from proceso import Proceso
import math

class Programa:
    def __init__(self, nombre, tamano_total_mb, duracion_estimada, tiempo_llegada=0):
        """
        Inicializa un programa que puede dividirse en múltiples procesos
        
        Args:
            nombre (str): Nombre del programa (ej: "Word", "Excel", "Chrome")
            tamano_total_mb (int): Tamaño total del programa en MB
            duracion_estimada (int): Duración estimada de ejecución
            tiempo_llegada (int): Tiempo de llegada del programa
        """
        self.nombre = nombre
        self.tamano_total_mb = tamano_total_mb
        self.tamano_total_bytes = tamano_total_mb * 1024 * 1024
        self.duracion_estimada = duracion_estimada
        self.tiempo_llegada = tiempo_llegada
        
        # Configuración de división
        self.tamano_maximo_proceso_mb = 512  # Máximo 512MB por proceso hijo
        self.tamano_maximo_proceso_bytes = self.tamano_maximo_proceso_mb * 1024 * 1024
        
        # Lista de procesos hijos generados
        self.procesos_hijos = []
        self.total_procesos_hijos = 0
        self.procesos_completados = 0
        
        # Estado del programa
        self.estado = "Pendiente"  # Pendiente, Ejecutando, Completado
        self.programa_id = None
        
    def dividir_en_procesos(self, simulador):
        """
        Divide el programa en múltiples procesos hijos si es necesario
        
        Args:
            simulador: Instancia del simulador para obtener PIDs únicos
            
        Returns:
            list: Lista de procesos hijos creados
        """
        self.procesos_hijos = []
        
        # Calcular cuántos procesos necesitamos
        num_procesos = math.ceil(self.tamano_total_bytes / self.tamano_maximo_proceso_bytes)
        self.total_procesos_hijos = num_procesos
        
        print(f"📦 Dividiendo programa '{self.nombre}' ({self.tamano_total_mb}MB) en {num_procesos} procesos...")
        
        for i in range(num_procesos):
            # Calcular el tamaño de este proceso hijo
            tamano_restante = self.tamano_total_bytes - (i * self.tamano_maximo_proceso_bytes)
            tamano_proceso = min(self.tamano_maximo_proceso_bytes, tamano_restante)
            
            # Calcular duración proporcional
            proporcion = tamano_proceso / self.tamano_total_bytes
            duracion_proceso = max(1, int(self.duracion_estimada * proporcion))
            
            # Crear proceso hijo
            pid = simulador.obtener_proximo_pid()
            nombre_proceso = f"{self.nombre}_P{i+1}"
            
            proceso_hijo = Proceso(
                pid=pid,
                nombre=nombre_proceso,
                tiempo_llegada=self.tiempo_llegada,
                duracion=duracion_proceso,
                tamano_memoria=tamano_proceso
            )
            
            # Marcar como proceso hijo y asignar referencia al programa padre
            proceso_hijo.es_proceso_hijo = True
            proceso_hijo.programa_padre = self
            proceso_hijo.numero_hijo = i + 1
            
            self.procesos_hijos.append(proceso_hijo)
            
            print(f"  ├─ {nombre_proceso}: {tamano_proceso//(1024*1024)}MB, Duración: {duracion_proceso}")
        
        self.estado = "Dividido"
        return self.procesos_hijos
    
    def marcar_proceso_completado(self):
        """
        Marca un proceso hijo como completado y verifica si el programa está completo
        """
        self.procesos_completados += 1
        
        if self.procesos_completados >= self.total_procesos_hijos:
            self.estado = "Completado"
            print(f"✅ Programa '{self.nombre}' completado exitosamente!")
            return True
        else:
            progreso = (self.procesos_completados / self.total_procesos_hijos) * 100
            print(f"📊 Programa '{self.nombre}' - Progreso: {progreso:.1f}% ({self.procesos_completados}/{self.total_procesos_hijos})")
            return False
    
    def obtener_estado_detallado(self):
        """
        Retorna información detallada del estado del programa
        """
        if not self.procesos_hijos:
            return f"{self.nombre}: Sin dividir"
        
        estados_hijos = {}
        for proceso in self.procesos_hijos:
            estado = proceso.estado
            estados_hijos[estado] = estados_hijos.get(estado, 0) + 1
        
        detalles = ", ".join([f"{estado}: {count}" for estado, count in estados_hijos.items()])
        progreso = (self.procesos_completados / self.total_procesos_hijos) * 100 if self.total_procesos_hijos > 0 else 0
        
        return f"{self.nombre} ({progreso:.1f}%): {detalles}"
    
    def __str__(self):
        return f"Programa(nombre='{self.nombre}', tamaño={self.tamano_total_mb}MB, hijos={len(self.procesos_hijos)}, estado='{self.estado}')"
    
    def __repr__(self):
        return self.__str__()


class GestorProgramas:
    """
    Gestor para manejar múltiples programas y su conversión a procesos
    """
    
    def __init__(self):
        self.programas = []
        self.programas_predefinidos = {
            "Word": {"tamano_mb": 400, "duracion": 8},
            "Excel": {"tamano_mb": 350, "duracion": 6},
            "Chrome": {"tamano_mb": 800, "duracion": 12},
            "Photoshop": {"tamano_mb": 1200, "duracion": 15},
            "Visual Studio": {"tamano_mb": 900, "duracion": 10},
            "Steam": {"tamano_mb": 600, "duracion": 7},
            "Zoom": {"tamano_mb": 200, "duracion": 5},
            "Spotify": {"tamano_mb": 250, "duracion": 4}
        }
    
    def crear_programa(self, nombre, tamano_mb, duracion, tiempo_llegada=0):
        """
        Crea un nuevo programa
        """
        programa = Programa(nombre, tamano_mb, duracion, tiempo_llegada)
        self.programas.append(programa)
        return programa
    
    def crear_programa_predefinido(self, nombre_programa, tiempo_llegada=0):
        """
        Crea un programa usando configuraciones predefinidas
        """
        if nombre_programa not in self.programas_predefinidos:
            raise ValueError(f"Programa '{nombre_programa}' no está predefinido")
        
        config = self.programas_predefinidos[nombre_programa]
        return self.crear_programa(
            nombre=nombre_programa,
            tamano_mb=config["tamano_mb"],
            duracion=config["duracion"],
            tiempo_llegada=tiempo_llegada
        )
    
    def obtener_programas_disponibles(self):
        """
        Retorna lista de programas predefinidos disponibles
        """
        return list(self.programas_predefinidos.keys())
    
    def lanzar_programa(self, programa, simulador):
        """
        Lanza un programa al simulador, dividiéndolo en procesos si es necesario
        """
        procesos_hijos = programa.dividir_en_procesos(simulador)
        
        # Agregar todos los procesos hijos al simulador
        for proceso in procesos_hijos:
            simulador.agregar_proceso(proceso)
        
        return procesos_hijos
