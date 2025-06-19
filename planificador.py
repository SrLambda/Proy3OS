import collections

class Planificador:
    def __init__(self):
        # El planificador no guarda las colas, las tiene que recibir el Simulador para operar sobre ellas.
        pass

    def planificar(self, cola_listos, algoritmo="SJF"):
        """
        Planifica procesos según el algoritmo especificado
        """
        if algoritmo == "SJF":
            return self._planificar_sjf(cola_listos)
        elif algoritmo in ["Round Robin", "RR"]:  # Aceptar ambas formas
            return self._planificar_round_robin(cola_listos)
        else:
            raise ValueError("Algoritmo de planificación no reconocido.")

    def _planificar_sjf(self, cola_listos):
        """
        Planificación Shortest Job First (SJF)
        Ordena por tiempo de ráfaga restante (más corto primero)
        """
        if not cola_listos:
            return []
        
        # Ordenar por tiempo restante (SJF)
        procesos_ordenados = sorted(cola_listos, key=lambda p: p.tiempo_restante)
        
        # Devolver el proceso más corto como lista para consistencia
        return [procesos_ordenados[0]]

    def _planificar_round_robin(self, cola_listos, quantum=3):
        """
        Planificación Round Robin con quantum
        Devuelve el primer proceso de la cola (FIFO)
        """
        if cola_listos:
            # En lugar de popleft(), usar índice 0 para listas normales
            return [cola_listos[0]]  # Devolver como lista para consistencia
        return []
