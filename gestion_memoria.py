import random

class GestionMemoria:
    def __init__(self, ram_mb=2048, swap_mb=4096, block_size_mb=64):
        """
        Inicializa el gestor de memoria.
        """
        # Calcular número de bloques
        num_bloques_ram = ram_mb // block_size_mb
        num_bloques_swap = swap_mb // block_size_mb

        # Inicializar las estructuras de datos de memoria
        self.ram = self._inicializar_memoria(num_bloques_ram)
        self.swap = self._inicializar_memoria(num_bloques_swap)

        # Diccionario para mapear procesos a colores
        self.procesos_colores = {}
        self._colores_disponibles = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#A133FF', '#33FFA1']

    def _inicializar_memoria(self, num_bloques):
        """
        Crea una lista de bloques de memoria, todos libres inicialmente.
        """
        return [{'estado': 'libre', 'proceso_id': None} for _ in range(num_bloques)]

    def registrar_nuevo_proceso(self, proceso_id):
        """
        Registra un nuevo proceso y le asigna un color.
        """
        if proceso_id not in self.procesos_colores:
            color = random.choice(self._colores_disponibles) # Asigna un color aleatorio de la lista
            self.procesos_colores[proceso_id] = {'color': color}
            print(f"Proceso {proceso_id} registrado con el color {color}")

    def asignar_memoria_a_proceso(self, proceso_id, memoria_requerida_mb):
        """
        Asigna un número de bloques de memoria a un proceso (algoritmo 'Primer Ajuste').
        """
        bloques_necesarios = (memoria_requerida_mb + 63) // 64 # Redondeo hacia arriba

        # Buscamos el primer hueco lo suficientemente grande
        for i in range(len(self.ram) - bloques_necesarios + 1):
            # Revisa si hay N bloques consecutivos libres
            if all(self.ram[j]['estado'] == 'libre' for j in range(i, i + bloques_necesarios)):
                # Si se encuentra, se asignan los bloques
                for j in range(i, i + bloques_necesarios):
                    self.ram[j]['estado'] = 'ocupado'
                    self.ram[j]['proceso_id'] = proceso_id
                print(f"Asignados {bloques_necesarios} bloques al proceso {proceso_id} en RAM.")
                return True # Asignación exitosa

        print(f"No hay suficiente memoria contigua en RAM para el proceso {proceso_id}.")
        return False # No se pudo asignar
