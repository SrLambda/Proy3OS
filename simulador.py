import collections
from cpu import CPU
from memoria import Memoria
from planificador import Planificador
from programa import GestorProgramas

class Simulador:
    def __init__(self, num_nucleos=2):
        self.cpu = CPU(num_nucleos)        # Memoria original: 2GB RAM + 4GB SWAP
        self.memoria = Memoria()
        self.planificador = Planificador()
        self.quantum = 2  # Quantum más corto para ver desalojos
        self.reloj_global = 0
        self.simulacion_activa = True
        self.proximo_pid=1 # Para asignar PIDs únicos a los procesos

        # Listas para gestionar procesos
        self.procesos_nuevos = []
        self.cola_listos = []
        self.procesos_terminados = []
        
        # Gestor de programas
        self.gestor_programas = GestorProgramas()

        # Algoritmo de planificación actual
        self.algoritmo_planificacion = "SJF"

    
    def obtener_proximo_pid(self):
        """Obtiene el próximo PID secuencial"""
        pid_actual = self.proximo_pid
        self.proximo_pid += 1
        return pid_actual

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
        """Agrega un proceso al sistema asignando PID automático"""
        # Asignar PID solo si no tiene uno
        if proceso.pid is None:
            proceso.pid = self.obtener_proximo_pid()
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
        if not self.hay_procesos_pendientes():
            print(f"🏁 Simulación terminada (todos los procesos completados en tiempo {self.reloj_global})")
            return False
    
        return True

    def hay_procesos_pendientes(self):
        """Verifica si hay procesos que aún no han terminado"""
        # 1. Procesos nuevos que aún no han llegado o no tienen memoria asignada
        if self.procesos_nuevos:
            return True
        
        # 2. Procesos en cola de listos
        if self.cola_listos:
            return True
        
        # 3. Procesos en CPU que no han terminado
        for proceso in self.cpu.nucleos:
            if proceso and proceso.estado != "terminado":
                return True
        
        # 4. Si no hay ninguno de los anteriores, todos los procesos han terminado        return False
    
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
                
                # Si el proceso está en SWAP, intentar moverlo a RAM
                if proceso.en_swap:
                    if not self.mover_proceso_a_ram_si_necesario(proceso):
                        print(f"⚠️  Proceso {proceso.pid} no se puede ejecutar (permanece en SWAP)")
                        continue
                
                self.cpu.asignar_proceso(i, proceso)
                proceso.set_estado("ejecutando")
                proceso.reiniciar_quantum()  # Reiniciar quantum al asignar
                
                # REGISTRO DE TIEMPO DE PRIMERA EJECUCIÓN
                if proceso.tiempo_primer_ejecucion is None:
                    proceso.tiempo_primer_ejecucion = self.reloj_global
                    print(f"📊 Proceso {proceso.pid} inicia por primera vez en tiempo {self.reloj_global}")
                
                self.cola_listos.remove(proceso)
                ubicacion = "SWAP" if proceso.en_swap else "RAM"
                print(f"🖥️  Proceso {proceso.pid} asignado al núcleo {i} desde {ubicacion} (Algoritmo: {self.algoritmo_planificacion})")

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
        """Calcula estadísticas detalladas por proceso"""
        estadisticas = {
            "procesos": [],
            "promedios": {}
        }

        if not self.procesos_terminados:
            return estadisticas

        tiempos_espera = []
        tiempos_respuesta = []
        tiempos_retorno = []

        for proceso in self.procesos_terminados:
            # Verificar que tenga los atributos necesarios
            if not hasattr(proceso, 'tiempo_primer_ejecucion') or not hasattr(proceso, 'tiempo_finalizacion'):
                continue
            if proceso.tiempo_primer_ejecucion is None or proceso.tiempo_finalizacion is None:
                continue

            tiempo_retorno = proceso.tiempo_finalizacion - proceso.tiempo_llegada
            tiempo_respuesta = proceso.tiempo_primer_ejecucion - proceso.tiempo_llegada
            tiempo_espera = proceso.tiempo_espera if hasattr(proceso, 'tiempo_espera') else tiempo_retorno - proceso.duracion

            estadisticas["procesos"].append({
                "pid": proceso.pid,
                "nombre": proceso.nombre,
                "tiempo_espera": tiempo_espera,
                "tiempo_respuesta": tiempo_respuesta,
                "tiempo_retorno": tiempo_retorno
            })

            tiempos_espera.append(tiempo_espera)
            tiempos_respuesta.append(tiempo_respuesta)
            tiempos_retorno.append(tiempo_retorno)

        # Calcular promedios
        if estadisticas["procesos"]:
            estadisticas["promedios"] = {
                "tiempo_espera": sum(tiempos_espera) / len(tiempos_espera),
                "tiempo_respuesta": sum(tiempos_respuesta) / len(tiempos_respuesta),
                "tiempo_retorno": sum(tiempos_retorno) / len(tiempos_retorno)
            }

        return estadisticas



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
        nucleos_a_desalojar = []
        
        # PRIMERO: Avanzar el tiempo de CPU (disminuye tiempo_restante)
        self.cpu.avanzar_tiempo(1)
        
        # SEGUNDO: Verificar cada núcleo después de avanzar el tiempo
        for i, proceso in enumerate(self.cpu.nucleos):
            if proceso is None:
                continue
                
            # Incrementar el tiempo de quantum actual
            proceso.tiempo_quantum_actual += 1
            
            # Verificar si el proceso ha terminado (tiempo restante llegó a 0)
            if proceso.tiempo_restante <= 0:
                print(f"✅ Proceso {proceso.pid} terminado en núcleo {i}")
                
                # Marcar el proceso como terminado
                proceso.set_estado("terminado")
                proceso.tiempo_finalizacion = self.reloj_global
                
                # Liberar memoria del proceso
                self.memoria.liberar_memoria(proceso)
                
                # Mover el proceso a la lista de terminados
                self.procesos_terminados.append(proceso)
                
                # Desalojar el núcleo
                nucleos_a_desalojar.append(i)
                
            # Verificar si en Round Robin se cumple el quantum (solo si no ha terminado)
            elif (self.algoritmo_planificacion == "RR" and 
                proceso.tiempo_quantum_actual >= self.quantum):
                print(f"⏱️ Proceso {proceso.pid} desalojado por quantum en núcleo {i}")
                
                # Cambiar estado a listo
                proceso.set_estado("listo")
                
                # Reiniciar el quantum del proceso
                proceso.reiniciar_quantum()
                
                # Mover el proceso a la cola de listos
                self.cola_listos.append(proceso)
                
                # Desalojar el núcleo
                nucleos_a_desalojar.append(i)
        
        # TERCERO: Desalojar los núcleos marcados
        for i in nucleos_a_desalojar:
            self.cpu.desalojar_proceso(i)

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

    def mover_proceso_a_ram_si_necesario(self, proceso):
        """Mueve un proceso de SWAP a RAM si está en ejecución y es necesario"""
        if proceso.en_swap:
            print(f"🔄 Proceso {proceso.pid} está en SWAP, intentando mover a RAM para ejecución...")
            
            # CORRECCIÓN: Agregar contador de intentos para evitar bucle infinito
            if not hasattr(proceso, 'intentos_swap_ram'):
                proceso.intentos_swap_ram = 0
            
            proceso.intentos_swap_ram += 1
            
            # Si ya intentó muchas veces, marcar como no en SWAP para evitar bucle
            if proceso.intentos_swap_ram > 5:
                print(f"⚠️  Proceso {proceso.pid} tiene demasiados intentos fallidos, corrigiendo estado")
                proceso.en_swap = False
                proceso.intentos_swap_ram = 0
                return True
            
            if self.memoria._mover_proceso_a_ram(proceso.pid):
                proceso.en_swap = False
                proceso.num_swaps_out += 1
                proceso.intentos_swap_ram = 0  # Resetear contador
                print(f"✅ Proceso {proceso.pid} movido exitosamente de SWAP a RAM")
                return True
            else:
                print(f"❌ No se pudo mover el proceso {proceso.pid} de SWAP a RAM (intento {proceso.intentos_swap_ram})")
                return False
        return True

    def obtener_estadisticas_swap(self):
        """Obtiene estadísticas detalladas de SWAP"""
        uso_memoria = self.memoria.obtener_uso_memoria()
        procesos_en_swap = self.memoria.obtener_procesos_en_swap()
        
        return {
            'procesos_en_swap': len(procesos_en_swap),
            'lista_procesos_swap': procesos_en_swap,
            'memoria_swap_usada': uso_memoria['swap']['ocupada'],
            'memoria_swap_libre': uso_memoria['swap']['libre'],
            'porcentaje_swap_uso': uso_memoria['swap']['porcentaje_uso'],
            'total_swaps_in': uso_memoria['estadisticas_swap']['total_swaps_in'],
            'total_swaps_out': uso_memoria['estadisticas_swap']['total_swaps_out'],
        }

    def obtener_visualizacion_memoria(self):
        """Obtiene datos para visualización de memoria RAM y SWAP"""
        bloques = self.memoria.obtener_todos_los_bloques()
        uso = self.memoria.obtener_uso_memoria()
        
        return {
            'ram': {
                'bloques_ocupados': bloques['ram_ocupados'],
                'bloques_libres': bloques['ram_libres'],
                'total': uso['ram']['total'],
                'ocupada': uso['ram']['ocupada'],
                'libre': uso['ram']['libre'],
                'porcentaje_uso': uso['ram']['porcentaje_uso']
            },
            'swap': {
                'bloques_ocupados': bloques['swap_ocupados'],
                'bloques_libres': bloques['swap_libres'],
                'total': uso['swap']['total'],
                'ocupada': uso['swap']['ocupada'],
                'libre': uso['swap']['libre'],
                'porcentaje_uso': uso['swap']['porcentaje_uso']
            }
        }

    # === MÉTODOS PARA GESTIÓN DE PROGRAMAS ===
    
    def lanzar_programa(self, nombre_programa, tamano_mb=None, duracion=None):
        """
        Lanza un programa al simulador, dividiéndolo automáticamente si es necesario
        
        Args:
            nombre_programa (str): Nombre del programa
            tamano_mb (int, optional): Tamaño personalizado en MB
            duracion (int, optional): Duración personalizada
            
        Returns:
            tuple: (programa, lista_procesos_hijos)
        """
        try:
            if tamano_mb is not None and duracion is not None:
                # Crear programa personalizado
                programa = self.gestor_programas.crear_programa(
                    nombre=nombre_programa,
                    tamano_mb=tamano_mb,
                    duracion=duracion,
                    tiempo_llegada=self.reloj_global
                )
            else:
                # Usar programa predefinido
                programa = self.gestor_programas.crear_programa_predefinido(
                    nombre_programa=nombre_programa,
                    tiempo_llegada=self.reloj_global
                )
            
            # Lanzar el programa (lo divide automáticamente)
            procesos_hijos = self.gestor_programas.lanzar_programa(programa, self)
            
            print(f"🚀 Programa '{nombre_programa}' lanzado exitosamente!")
            print(f"   └─ Generados {len(procesos_hijos)} procesos hijos")
            
            return programa, procesos_hijos
            
        except Exception as e:
            print(f"❌ Error al lanzar programa '{nombre_programa}': {e}")
            return None, []
    
    def obtener_programas_disponibles(self):
        """Retorna lista de programas predefinidos disponibles"""
        return self.gestor_programas.obtener_programas_disponibles()
    
    def obtener_estado_programas(self):
        """Retorna información detallada de todos los programas lanzados"""
        programas_info = []
        for programa in self.gestor_programas.programas:
            programas_info.append({
                'nombre': programa.nombre,
                'tamano_mb': programa.tamano_total_mb,
                'estado': programa.estado,
                'total_hijos': programa.total_procesos_hijos,
                'completados': programa.procesos_completados,
                'progreso': (programa.procesos_completados / programa.total_procesos_hijos * 100) if programa.total_procesos_hijos > 0 else 0,
                'detalle': programa.obtener_estado_detallado()
            })
        return programas_info
    
    def obtener_procesos_por_programa(self):
        """
        Retorna un diccionario agrupando procesos por programa padre
        """
        procesos_por_programa = {}
        
        # Recopilar todos los procesos del sistema
        todos_los_procesos = (self.procesos_nuevos + self.cola_listos + 
                            self.cpu.obtener_procesos_en_ejecucion() + 
                            self.procesos_terminados)
        
        for proceso in todos_los_procesos:
            if proceso.es_proceso_hijo and proceso.programa_padre:
                nombre_programa = proceso.programa_padre.nombre
                if nombre_programa not in procesos_por_programa:
                    procesos_por_programa[nombre_programa] = []
                procesos_por_programa[nombre_programa].append(proceso)
            else:
                # Procesos independientes (no hijos de programas)
                if "Procesos Individuales" not in procesos_por_programa:
                    procesos_por_programa["Procesos Individuales"] = []
                procesos_por_programa["Procesos Individuales"].append(proceso)
        
        return procesos_por_programa


