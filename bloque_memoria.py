class BloqueMemoria:
    def __init__(self, id_bloque, inicio, tamano, ocupado=False, pid_proceso=None):
        self.id = id_bloque
        self.inicio = inicio
        self.tamano = tamano
        self.ocupado = ocupado
        self.pid_proceso = pid_proceso

    def __repr__(self):
        return f"Bloque {self.id} (Inicio: {self.inicio}, Tam: {self.tamano}, Ocupado: {self.ocupado}, PID: {self.pid_proceso})"
