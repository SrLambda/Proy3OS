class CPU:
    def __init__(self, num_nucleos):
        self.num_nucleos = num_nucleos
        self.nucleos = [None] * num_nucleos  # Cada elemento puede contener un Proceso
        self.tiempo_ocioso = [0] * num_nucleos # Para estadísticas

    def asignar_proceso(self, nucleo_id, proceso):
        if 0 <= nucleo_id < self.num_nucleos:
            self.nucleos[nucleo_id] = proceso
            if proceso:
                proceso.set_estado("ejecutando")  # Usar minúsculas para consistencia

    def desalojar_proceso(self, nucleo_id):
        if 0 <= nucleo_id < self.num_nucleos:
            proceso = self.nucleos[nucleo_id]
            self.nucleos[nucleo_id] = None
            if proceso:
                proceso.set_estado("listo")  # Cambiar estado al desalojar
            return proceso
        return None

    def esta_libre(self, nucleo_id):
        return 0 <= nucleo_id < self.num_nucleos and self.nucleos[nucleo_id] is None

    def get_proceso_en_nucleo(self, nucleo_id):
        if 0 <= nucleo_id < self.num_nucleos:
            return self.nucleos[nucleo_id]
        return None

    def avanzar_tiempo(self, tiempo_unidad):
        for i in range(self.num_nucleos):
            if self.nucleos[i] is not None:
                self.nucleos[i].tiempo_restante = max(0, self.nucleos[i].tiempo_restante - tiempo_unidad)
