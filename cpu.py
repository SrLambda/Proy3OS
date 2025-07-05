class CPU:
    def __init__(self, num_nucleos):
        self.num_nucleos = num_nucleos
        self.nucleos = [None] * num_nucleos  
        self.tiempo_ocioso = [0] * num_nucleos

    def asignar_proceso(self, nucleo_id, proceso):
        if 0 <= nucleo_id < self.num_nucleos:
            self.nucleos[nucleo_id] = proceso
            if proceso:
                proceso.set_estado("ejecutando")  
    def desalojar_proceso(self, nucleo_id):
        if 0 <= nucleo_id < self.num_nucleos:
            proceso = self.nucleos[nucleo_id]
            self.nucleos[nucleo_id] = None
            if proceso:
                proceso.set_estado("listo")  # Cambiar estado 
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

    def obtener_procesos_en_ejecucion(self):
        """Retorna lista de procesos que están ejecutándose en los núcleos"""
        procesos_ejecutando = []
        for nucleo in self.nucleos:
            if nucleo is not None:
                procesos_ejecutando.append(nucleo)
        return procesos_ejecutando
