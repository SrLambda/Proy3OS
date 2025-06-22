import collections
from cpu import CPU
from memoria import Memoria
from planificador import Planificador

class Simulador:
    def __init__(self, num_nucleos=2):
        self.cpu = CPU(num_nucleos)
        self.memoria = Memoria()
        self.planificador = Planificador()
        self.quantum = 2  # Quantum más corto para ver desalojos
        self.reloj_global = 0
        self.simulacion_activa = True

        # Listas para gestionar procesos
        self.procesos_nuevos = []
        self.cola_listos = []
        self.procesos_terminados = []

        # Algoritmo de planificación actual
        self.algoritmo_planificacion = "SJF"


    def todos_los_procesos(self):
        """
        Retorna todos los procesos en el sistema, independientemente de su estado
        """
        # 1. Procesos en CPU - recoge los procesos que no son None
        procesos_en_cpu = [p for p in self.cpu.nucleos if p is not None]

        # 2. Combinar todas las listas de procesos
        return (
            self.procesos_nuevos
            + self.cola_listos
            + procesos_en_cpu
            + self.procesos_terminados
        )

    def agregar_proceso(self, proceso):
        """Agrega un proceso al sistema"""
        proceso.set_estado("nuevo")
        self.procesos_nuevos.append(proceso)  # Cambiar cola_nuevos por procesos_nuevos
        print(f"✅ Proceso {proceso.pid} agregado al sistema (Memoria: {proceso.tamano_memoria // (1024**2)}MB)")

    def configurar_algoritmo(self, algoritmo):
        """Configura el algoritmo de planificación"""
        self.algoritmo_planificacion = algoritmo
        print(f"🔧 Algoritmo de planificación establecido: {algoritmo}")

    def set_quantum(self, quantum):
        self.quantum = quantum

    def iniciar_simulacion(self):
        self.simulacion_activa = True
        print("Iniciando simulación...")
        print("🔄 VERSIÓN ACTUALIZADA - Procesamiento de llegadas activado")
        print("🖥️  NUEVA FUNCIONALIDAD - Planificación de CPU implementada")
        print("⚡ ÚLTIMA FUNCIONALIDAD - Ejecución y finalización implementada")

    def detener_simulacion(self):
        self.simulacion_activa = False
        print("Simulación detenida.")

    def paso_simulacion(self):
        # Por ahora solo incrementamos el reloj y terminamos rápido
        if not self.simulacion_activa:
            return False

        print(f"⏰ Paso de simulación {self.reloj_global}")

        # 1. Mover procesos de "nuevos" a "listos" si han llegado
        self._procesar_llegadas()

        # 2. Planificar procesos en núcleos libres
        self.planificar_cpu()

        # 3. NUEVO: Avanzar tiempo en CPU y verificar procesos terminados
        self._avanzar_ejecucion()

        # Incrementar el reloj global
        self.reloj_global += 1

        # Ahora terminar después de 10 pasos para ver procesos terminando
        if self.reloj_global >= 15:
            print("🏁 Simulación terminada (15 pasos completados)")
            return False

        return True


    def planificar_cpu(self):
        """Planifica procesos en núcleos libres usando el algoritmo seleccionado"""
        if not self.cola_listos:
            return

        # Obtener procesos ordenados según el algoritmo
        procesos_ordenados = self.planificador.planificar(self.cola_listos, self.algoritmo_planificacion)

        # Asignar procesos a núcleos libres
        for i, nucleo in enumerate(self.cpu.nucleos):
            if nucleo is None and procesos_ordenados:
                proceso = procesos_ordenados.pop(0)
                self.cpu.asignar_proceso(i, proceso)
                proceso.set_estado("ejecutando")
                proceso.reiniciar_quantum()  # Reiniciar quantum al asignar
                self.cola_listos.remove(proceso)
                print(f"🖥️  Proceso {proceso.pid} asignado al núcleo {i} (Algoritmo: {self.algoritmo_planificacion})")

    def mostrar_estado(self):
        """Muestra el estado actual del sistema"""
        if self.reloj_global % 5 == 0 or self.reloj_global < 3:
            print(f"\n--- Estado en tiempo {self.reloj_global + 1} ---")
            print(f"Cola nuevos: {len(self.procesos_nuevos)} procesos")  # Cambiar cola_nuevos por procesos_nuevos
            print(f"Cola listos: {len(self.cola_listos)} procesos")
            print(f"Ejecutando: {sum(1 for nucleo in self.cpu.nucleos if nucleo)} procesos")
            print(f"Terminados: {len(self.procesos_terminados)} procesos")

            # Mostrar estado de cada núcleo
            for i, proceso in enumerate(self.cpu.nucleos):
                if proceso:
                    print(f"Núcleo {i}: Proceso {proceso.pid} (restante: {proceso.tiempo_restante})")
                else:
                    print(f"Núcleo {i}: Libre")

    def calcular_estadisticas(self):
        """Calcula estadísticas del sistema"""
        # Calcular todos los procesos del sistema
        todos_los_procesos = (self.procesos_nuevos + self.cola_listos +
                             [p for p in self.cpu.nucleos if p] + self.procesos_terminados)

        return {
            "total_procesos": len(todos_los_procesos),
            "procesos_nuevos": len(self.procesos_nuevos),
            "procesos_listos": len(self.cola_listos),
            "procesos_ejecutando": sum(1 for nucleo in self.cpu.nucleos if nucleo),
            "procesos_terminados": len(self.procesos_terminados),
            "tiempo_promedio_retorno": 0,
            "tiempo_promedio_respuesta": 0,
            "tiempo_promedio_espera": 0,
            "tiempo_total_simulacion": self.reloj_global
        }

    def _procesar_llegadas(self):
        """Procesa los procesos que llegan en el tiempo actual"""
        for proceso in list(self.procesos_nuevos):  # Cambiar cola_nuevos por procesos_nuevos
            if proceso.tiempo_llegada <= self.reloj_global:
                # Intentar asignar memoria
                if self.memoria.asignar_memoria(proceso):
                    # Mover a cola de listos
                    proceso.set_estado("listo")
                    self.cola_listos.append(proceso)
                    self.procesos_nuevos.remove(proceso)  # Cambiar cola_nuevos por procesos_nuevos
                    print(f"📋 Proceso {proceso.pid} movido a cola de listos (llegó en tiempo {proceso.tiempo_llegada})")
                else:
                    print(f"❌ No hay memoria suficiente para el proceso {proceso.pid}")

    def _avanzar_ejecucion(self):
        """Avanza la ejecución de procesos en los núcleos y maneja desalojos"""
        procesos_a_desalojar = []

        # Verificar procesos en ejecución ANTES de avanzar tiempo de CPU
        for i, proceso in enumerate(self.cpu.nucleos):
            if proceso:
                # Incrementar quantum ANTES de verificar terminación
                proceso.tiempo_quantum_actual += 1

                if proceso.tiempo_restante <= 0:
                    # Proceso terminó completamente
                    print(f"🔓 Liberando memoria del proceso {proceso.pid}")
                    self.memoria.liberar_memoria(proceso)
                    print(f"🏁 Proceso {proceso.pid} terminado y liberado del núcleo {i}")
                    proceso.set_estado("terminado")
                    self.procesos_terminados.append(proceso)
                    procesos_a_desalojar.append((i, None))

                elif (self.algoritmo_planificacion == "RR" and
                      proceso.tiempo_quantum_actual >= self.quantum):
                    # Desalojo por quantum en Round Robin
                    print(f"⏰ Proceso {proceso.pid} desalojado por quantum (quantum={self.quantum})")
                    proceso.reiniciar_quantum()
                    proceso.set_estado("listo")
                    self.cola_listos.append(proceso)
                    procesos_a_desalojar.append((i, None))

        # Avanzar tiempo de CPU DESPUÉS de verificar quantum
        self.cpu.avanzar_tiempo(1)

        # Ejecutar desalojos
        for nucleo, _ in procesos_a_desalojar:
            self.cpu.desalojar_proceso(nucleo)

    def _verificar_procesos_terminados(self):
        """Verifica y procesa procesos que han terminado"""
        for i in range(self.cpu.num_nucleos):
            proceso = self.cpu.get_proceso_en_nucleo(i)
            if proceso and proceso.tiempo_restante <= 0:
                # Usar el método de CPU para desalojar
                proceso_terminado = self.cpu.desalojar_proceso(i)

                # Actualizar estado usando el método del proceso
                proceso_terminado.set_estado("Terminado")
                proceso_terminado.tiempo_finalizacion = self.reloj_global

                # Actualizar listas del simulador
                self.procesos_terminados.append(proceso_terminado)
                self.procesos_ejecutando.remove(proceso_terminado)

                # Usar el método de memoria para liberar
                self.memoria.liberar_memoria(proceso_terminado)

                print(f"🏁 Proceso {proceso_terminado.pid} terminado y liberado del núcleo {i}")

    def set_algoritmo_planificacion(self, algoritmo):
        """Configura el algoritmo de planificación (método alternativo)"""
        self.configurar_algoritmo(algoritmo)

    
