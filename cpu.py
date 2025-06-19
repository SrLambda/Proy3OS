class CPU:
    def __init__(self, num_nucleos):
        self.num_nucleos = num_nucleos
        self.nucleos = [None] * num_nucleos  # Cada elemento puede contener un Proceso
        self.tiempo_ocioso = [0] * num_nucleos # Para estadísticas

    def asignar_proceso(self, nucleo_id, proceso):
        self.nucleos[nucleo_id] = proceso
        if proceso:
            proceso.set_estado("Ejecutando")

    def desalojar_proceso(self, nucleo_id):
        proceso = self.nucleos[nucleo_id]
        self.nucleos[nucleo_id] = None
        return proceso

    def esta_libre(self, nucleo_id):
        return self.nucleos[nucleo_id] is None

    def get_proceso_en_nucleo(self, nucleo_id):
        return self.nucleos[nucleo_id]

    def avanzar_tiempo(self, tiempo_unidad):
        for i in range(self.num_nucleos):
            if self.nucleos[i]:
                self.nucleos[i].actualizar_tiempo_restante(tiempo_unidad)
            else:
                self.tiempo_ocioso[i] += tiempo_unidad
