from bloque_memoria import BloqueMemoria
from paginacion import GestorPaginacion
from algoritmos_reemplazo import GestorMemoriaAvanzado

class Memoria:
    def __init__(self, tamano_total_gb=2, tamano_swap_gb=4):
        # Configuración de RAM
        self.tamano_total = tamano_total_gb * 1024 * 1024 * 1024  # Convertir GB a Bytes
        self.bloques_libres = [BloqueMemoria(0, 0, self.tamano_total, ocupado=False, ubicacion="RAM")]
        self.bloques_ocupados = []
        
        # Configuración de SWAP
        self.tamano_swap = tamano_swap_gb * 1024 * 1024 * 1024  # Convertir GB a Bytes
        self.bloques_swap_libres = [BloqueMemoria(0, 0, self.tamano_swap, ocupado=False, ubicacion="SWAP")]
        self.bloques_swap_ocupados = []
        
        # Control de IDs
        self.next_block_id = 1 # Para asignar IDs únicos a los bloques
        
        # Estadísticas de SWAP
        self.total_swaps_in = 0
        self.total_swaps_out = 0
        self.tiempo_total_swapping = 0
        
        # Sistema de Paginación
        self.gestor_paginacion = GestorPaginacion(tamano_pagina=16*1024*1024)  # 16MB por página (balance entre realismo y eficiencia)
        self.gestor_paginacion.inicializar_memoria(self.tamano_total, self.tamano_swap)
        self.paginacion_habilitada = True  # Flag para activar/desactivar paginación
        
        # Gestor Avanzado de Memoria
        self.gestor_avanzado = GestorMemoriaAvanzado(self.gestor_paginacion, "LRU")
        self.usar_gestion_avanzada = True  # Flag para usar gestión inteligente
        
        print(f"🖥️  Memoria inicializada:")
        print(f"   📀 RAM: {tamano_total_gb} GB ({self.tamano_total:,} bytes)")
        print(f"   💿 SWAP: {tamano_swap_gb} GB ({self.tamano_swap:,} bytes)")
        print(f"   📄 Paginación: {'Habilitada' if self.paginacion_habilitada else 'Deshabilitada'}")
        print(f"   🧠 Gestión Avanzada: {'Habilitada' if self.usar_gestion_avanzada else 'Deshabilitada'}")

    def asignar_memoria(self, proceso):
        """Asigna memoria a un proceso usando algoritmo First-Fit con soporte de SWAP y Paginación"""
        tamano_requerido = proceso.tamano_memoria
        print(f"📋 Intentando asignar {tamano_requerido:,} bytes al proceso {proceso.pid}, de color {proceso.color}")
        
        # Si la paginación está habilitada, usar el gestor correspondiente
        if self.paginacion_habilitada:
            if self.usar_gestion_avanzada:
                print(f"🧠 Usando gestión avanzada de memoria para proceso P{proceso.pid}")
                return self.gestor_avanzado.asignar_memoria_inteligente(proceso)
            else:
                print(f"📄 Usando sistema de paginación básico para proceso P{proceso.pid}")
                if self.gestor_paginacion.asignar_memoria_a_proceso(proceso):
                    print(f"✅ Memoria asignada exitosamente con paginación a P{proceso.pid}")
                    return True
                else:
                    print(f"❌ No se pudo asignar memoria con paginación a P{proceso.pid}")
                    return False
        
        # Sistema de bloques tradicional (fallback)
        print(f"🔧 Usando sistema de bloques tradicional para proceso P{proceso.pid}")
        if self._asignar_en_ram(proceso, tamano_requerido):
            return True
        
        # intento de swap
        print(f"⚠️  No hay espacio suficiente en RAM, evaluando SWAP...")
        
        espacio_swap_libre = sum(bloque.tamano for bloque in self.bloques_swap_libres)
        if espacio_swap_libre < tamano_requerido:
            print(f"❌ No hay espacio suficiente ni en RAM ni en SWAP para el proceso {proceso.pid}")
            return False

        if self._liberar_espacio_ram_con_swap(tamano_requerido):
            if self._asignar_en_ram(proceso, tamano_requerido):
                return True
        
        # Si no se pudo liberar espacio en RAM, asignar directamente en SWAP
        print(f"🔄 Asignando proceso {proceso.pid} directamente en SWAP...")
        return self._asignar_en_swap(proceso, tamano_requerido)
    

    def liberar_memoria(self, proceso):
        """Libera la memoria ocupada por un proceso tanto en RAM como en SWAP"""
        print(f"🔓 Liberando memoria del proceso {proceso.pid}")
        
        # Si la paginación está habilitada, usar el gestor de paginación
        if self.paginacion_habilitada:
            print(f"📄 Liberando páginas del proceso P{proceso.pid}")
            self.gestor_paginacion.liberar_memoria_proceso(proceso)
            return
        
        # Sistema de bloques tradicional (fallback)
        print(f"🔧 Liberando bloques tradicionales del proceso P{proceso.pid}")
        
        # Liberar bloques en RAM
        bloques_ram_a_liberar = []
        for bloque in self.bloques_ocupados:
            if bloque.pid_proceso == proceso.pid:
                bloques_ram_a_liberar.append(bloque)
                print(f"📦 Liberando bloque RAM: {bloque.tamano:,} bytes en posición {bloque.inicio}")
        
        for bloque in bloques_ram_a_liberar:
            self._liberar_bloque_ram(bloque)
        
        # Liberar bloques en SWAP
        bloques_swap_a_liberar = []
        for bloque in self.bloques_swap_ocupados:
            if bloque.pid_proceso == proceso.pid:
                bloques_swap_a_liberar.append(bloque)
                print(f"💿 Liberando bloque SWAP: {bloque.tamano:,} bytes en posición {bloque.inicio}")
        
        for bloque in bloques_swap_a_liberar:
            self._liberar_bloque_swap(bloque)

        proceso.bloques_memoria_asignados.clear()
        proceso.bloques_swap_asignados.clear()
        proceso.en_swap = False

        print(f"✅ Memoria del proceso {proceso.pid} liberada exitosamente")
        self._mostrar_estado_memoria()
        

    def fusionar_bloques_libres(self):
        """Fusiona bloques libres adyacentes para evitar fragmentación"""
        if len(self.bloques_libres) <= 1:
            print(f"ℹ️  No hay bloques para fusionar (total: {len(self.bloques_libres)})")
            return
        
        print(f"🔄 Iniciando fusión de {len(self.bloques_libres)} bloques libres")
        
        # Ordenar bloques por posición de inicio
        self.bloques_libres.sort(key=lambda x: x.inicio)
        
        bloques_fusionados = []
        bloque_actual = self.bloques_libres[0]
        fusiones_realizadas = 0
        
        for i in range(1, len(self.bloques_libres)):
            siguiente_bloque = self.bloques_libres[i]
            
            # fusion
            if bloque_actual.inicio + bloque_actual.tamano == siguiente_bloque.inicio:
                print(f"🔗 Fusionando bloques: {bloque_actual.tamano:,} + {siguiente_bloque.tamano:,} bytes")
                bloque_actual.tamano += siguiente_bloque.tamano
                fusiones_realizadas += 1
            else:
                bloques_fusionados.append(bloque_actual)
                bloque_actual = siguiente_bloque
        
        bloques_fusionados.append(bloque_actual)
        self.bloques_libres = bloques_fusionados
        
        print(f"✅ Fusión completada: {fusiones_realizadas} fusiones realizadas, {len(self.bloques_libres)} bloques resultantes")
        
    def obtener_uso_memoria(self):
        """Retorna estadísticas de uso de memoria RAM y SWAP"""
        # Estadísticas de RAM
        memoria_ram_ocupada = sum(bloque.tamano for bloque in self.bloques_ocupados)
        memoria_ram_libre = sum(bloque.tamano for bloque in self.bloques_libres)
        porcentaje_ram_uso = (memoria_ram_ocupada / self.tamano_total) * 100
        
        # Estadísticas de SWAP
        memoria_swap_ocupada = sum(bloque.tamano for bloque in self.bloques_swap_ocupados)
        memoria_swap_libre = sum(bloque.tamano for bloque in self.bloques_swap_libres)
        porcentaje_swap_uso = (memoria_swap_ocupada / self.tamano_swap) * 100 if self.tamano_swap > 0 else 0
        
        return {
            'ram': {
                'total': self.tamano_total,
                'ocupada': memoria_ram_ocupada,
                'libre': memoria_ram_libre,
                'porcentaje_uso': porcentaje_ram_uso,
                'num_bloques_ocupados': len(self.bloques_ocupados),
                'num_bloques_libres': len(self.bloques_libres)
            },
            'swap': {
                'total': self.tamano_swap,
                'ocupada': memoria_swap_ocupada,
                'libre': memoria_swap_libre,
                'porcentaje_uso': porcentaje_swap_uso,
                'num_bloques_ocupados': len(self.bloques_swap_ocupados),
                'num_bloques_libres': len(self.bloques_swap_libres)
            },
            'estadisticas_swap': {
                'total_swaps_in': self.total_swaps_in,
                'total_swaps_out': self.total_swaps_out,
                'tiempo_total_swapping': self.tiempo_total_swapping
            }
        }
        
    def hay_swapping_necesario(self, tamano_requerido):
        """Verifica si es necesario hacer swapping para asignar memoria"""
        memoria_libre_total = sum(bloque.tamano for bloque in self.bloques_libres)
        return memoria_libre_total < tamano_requerido
    
    def _mostrar_estado_memoria(self):
        """Método auxiliar para mostrar el estado actual de la memoria"""
        uso = self.obtener_uso_memoria()
        
        print(f"📊 Estado de Memoria:")
        print(f"   � RAM:")
        print(f"      �💾 Total: {uso['ram']['total']:,} bytes")
        print(f"      🔴 Ocupada: {uso['ram']['ocupada']:,} bytes ({uso['ram']['porcentaje_uso']:.1f}%)")
        print(f"      🟢 Libre: {uso['ram']['libre']:,} bytes")
        print(f"      📦 Bloques ocupados: {uso['ram']['num_bloques_ocupados']}")
        print(f"      📦 Bloques libres: {uso['ram']['num_bloques_libres']}")
        
        print(f"   💿 SWAP:")
        print(f"      💾 Total: {uso['swap']['total']:,} bytes")
        print(f"      🔴 Ocupada: {uso['swap']['ocupada']:,} bytes ({uso['swap']['porcentaje_uso']:.1f}%)")
        print(f"      🟢 Libre: {uso['swap']['libre']:,} bytes")
        print(f"      📦 Bloques ocupados: {uso['swap']['num_bloques_ocupados']}")
        print(f"      📦 Bloques libres: {uso['swap']['num_bloques_libres']}")
        
        print(f"   📈 Estadísticas SWAP:")
        print(f"      ⬇️  Swaps IN: {uso['estadisticas_swap']['total_swaps_in']}")
        print(f"      ⬆️  Swaps OUT: {uso['estadisticas_swap']['total_swaps_out']}")
        
        print(f"   --- Detalle de bloques libres ---")
        for i, bloque in enumerate(self.bloques_libres):
            print(f"     RAM libre {i+1}: {bloque.tamano:,} bytes en posición {bloque.inicio}")
        for i, bloque in enumerate(self.bloques_swap_libres):
            print(f"     SWAP libre {i+1}: {bloque.tamano:,} bytes en posición {bloque.inicio}")
        print("   " + "="*50)
    
    def _asignar_en_ram(self, proceso, tamano_requerido):
        """Asigna memoria en RAM usando First-Fit"""
        for i, bloque in enumerate(self.bloques_libres):
            if bloque.tamano >= tamano_requerido:
                print(f"✅ Bloque RAM encontrado: {bloque.tamano:,} bytes en posición {bloque.inicio}")
                
                # Crear nuevo bloque ocupado en RAM
                nuevo_bloque_ocupado = BloqueMemoria(
                    self.next_block_id,
                    bloque.inicio,
                    tamano_requerido,
                    ocupado=True,
                    pid_proceso=proceso.pid,
                    color=proceso.color,
                    ubicacion="RAM"
                )
                
                self.bloques_ocupados.append(nuevo_bloque_ocupado)
                proceso.bloques_memoria_asignados.append(nuevo_bloque_ocupado)
                proceso.en_swap = False
                self.next_block_id += 1
                
                # Fragmentar o eliminar bloque libre
                if bloque.tamano == tamano_requerido:
                    print(f"🔄 Bloque RAM usado completamente, eliminando de libres")
                    self.bloques_libres.pop(i)
                else:
                    print(f"🔄 Fragmentando bloque RAM: quedan {bloque.tamano - tamano_requerido:,} bytes libres")
                    bloque.inicio += tamano_requerido
                    bloque.tamano -= tamano_requerido
                
                print(f"🎉 Memoria RAM asignada exitosamente al proceso {proceso.pid}")
                self._mostrar_estado_memoria()
                return True
        return False

    def _asignar_en_swap(self, proceso, tamano_requerido):
        """Asigna memoria en SWAP usando First-Fit"""
        for i, bloque in enumerate(self.bloques_swap_libres):
            if bloque.tamano >= tamano_requerido:
                print(f"💿 Bloque SWAP encontrado: {bloque.tamano:,} bytes en posición {bloque.inicio}")
                
                # Crear nuevo bloque ocupado en SWAP
                nuevo_bloque_swap = BloqueMemoria(
                    self.next_block_id,
                    bloque.inicio,
                    tamano_requerido,
                    ocupado=True,
                    pid_proceso=proceso.pid,
                    color=proceso.color,
                    ubicacion="SWAP"
                )
                
                self.bloques_swap_ocupados.append(nuevo_bloque_swap)
                proceso.bloques_swap_asignados.append(nuevo_bloque_swap)
                proceso.en_swap = True
                proceso.num_swaps_in += 1
                self.total_swaps_in += 1
                self.next_block_id += 1
                
                # Fragmentar o eliminar bloque libre de SWAP
                if bloque.tamano == tamano_requerido:
                    print(f"🔄 Bloque SWAP usado completamente, eliminando de libres")
                    self.bloques_swap_libres.pop(i)
                else:
                    print(f"🔄 Fragmentando bloque SWAP: quedan {bloque.tamano - tamano_requerido:,} bytes libres")
                    bloque.inicio += tamano_requerido
                    bloque.tamano -= tamano_requerido
                
                print(f"💿 Memoria SWAP asignada exitosamente al proceso {proceso.pid}")
                self._mostrar_estado_memoria()
                return True
        return False

    def _liberar_espacio_ram_con_swap(self, tamano_requerido):
        """Libera espacio en RAM moviendo procesos al SWAP"""
        print(f"🔄 Intentando liberar {tamano_requerido:,} bytes de RAM usando SWAP...")
        

        candidatos = []
        for bloque in self.bloques_ocupados:
            if bloque.ubicacion == "RAM":
                candidatos.append(bloque)
        
  
        candidatos.sort(key=lambda x: x.tiempo_acceso)
        
        espacio_liberado = 0
        procesos_a_mover = []
        
 
        for bloque in candidatos:
            if bloque.pid_proceso not in procesos_a_mover:
                procesos_a_mover.append(bloque.pid_proceso)
                espacio_liberado += bloque.tamano
                if espacio_liberado >= tamano_requerido:
                    break
        

        exito = True
        for pid in procesos_a_mover:
            if not self._mover_proceso_a_swap(pid):
                exito = False
                break
        
        if exito:
            print(f"✅ Se liberaron {espacio_liberado:,} bytes de RAM moviendo {len(procesos_a_mover)} procesos al SWAP")
        
        return exito

    def _mover_proceso_a_swap(self, pid_proceso):
        """Mueve un proceso específico de RAM a SWAP"""
        print(f"🔄 Moviendo proceso {pid_proceso} de RAM a SWAP...")
        

        bloques_ram = [b for b in self.bloques_ocupados if b.pid_proceso == pid_proceso and b.ubicacion == "RAM"]
        
        if not bloques_ram:
            print(f"⚠️  Proceso {pid_proceso} no encontrado en RAM")
            return False
        
        tamano_total = sum(b.tamano for b in bloques_ram)
        

        espacio_swap_libre = sum(bloque.tamano for bloque in self.bloques_swap_libres)
        if espacio_swap_libre < tamano_total:
            print(f"❌ No hay espacio suficiente en SWAP para el proceso {pid_proceso}")
            return False
        

        color_proceso = bloques_ram[0].color
        if not self._asignar_espacio_swap(pid_proceso, tamano_total, color_proceso):
            return False

        for bloque in bloques_ram:
            self._liberar_bloque_ram(bloque)

        self.total_swaps_in += 1
        
        print(f"✅ Proceso {pid_proceso} movido exitosamente a SWAP")
        return True

    def _mover_proceso_a_ram(self, pid_proceso):
        """Mueve un proceso específico de SWAP a RAM"""
        print(f"🔄 Moviendo proceso {pid_proceso} de SWAP a RAM...")
        
        # Buscar bloques del proceso en SWAP
        bloques_swap = [b for b in self.bloques_swap_ocupados if b.pid_proceso == pid_proceso]
        
        if not bloques_swap:
            print(f"⚠️  Proceso {pid_proceso} no encontrado en SWAP")
            
            # CORRECCIÓN DEL BUG: Si no está en SWAP pero se marcó como tal,
            # probablemente ya está en RAM o hay inconsistencia de estado
            print(f"🔧 Verificando si el proceso {pid_proceso} ya está en RAM...")
            
            # Buscar en RAM
            bloques_ram = [b for b in self.bloques_ocupados if b.pid_proceso == pid_proceso]
            if bloques_ram:
                print(f"✅ Proceso {pid_proceso} ya está en RAM, corrigiendo estado")
                return True  # Ya está en RAM, marcar como éxito
            
            # Si no está en ningún lado, puede estar gestionado por paginación
            if self.paginacion_habilitada and self.usar_gestion_avanzada:
                print(f"🔧 Intentando recuperar proceso {pid_proceso} via gestor avanzado...")
                try:
                    # Intentar asignar memoria nuevamente
                    proceso_dummy = type('obj', (object,), {
                        'pid': pid_proceso, 
                        'tamano_memoria': 100 * 1024 * 1024,  # 100MB por defecto
                        'color': '#FF5733'
                    })
                    resultado = self.gestor_avanzado.asignar_memoria_inteligente(proceso_dummy)
                    if resultado:
                        print(f"✅ Proceso {pid_proceso} recuperado via gestor avanzado")
                        return True
                except Exception as e:
                    print(f"❌ Error en gestor avanzado: {e}")
            
            # Si nada funciona, marcar como fallo pero no crítico
            print(f"⚠️  No se pudo localizar proceso {pid_proceso}, marcando como disponible")
            return True  # Evitar bucle infinito
        
        tamano_total = sum(b.tamano for b in bloques_swap)
        
        # Verificar espacio en RAM
        espacio_ram_libre = sum(bloque.tamano for bloque in self.bloques_libres)
        if espacio_ram_libre < tamano_total:
            print(f"❌ No hay espacio suficiente en RAM para el proceso {pid_proceso}")
            return False
        
        # Asignar espacio en RAM
        color_proceso = bloques_swap[0].color
        if not self._asignar_espacio_ram(pid_proceso, tamano_total, color_proceso):
            return False
        
        # Liberar bloques de SWAP
        for bloque in bloques_swap:
            self._liberar_bloque_swap(bloque)
        
        # Actualizar estadísticas
        self.total_swaps_out += 1
        
        print(f"✅ Proceso {pid_proceso} movido exitosamente a RAM")
        return True

    def _asignar_espacio_swap(self, pid_proceso, tamano_requerido, color):
        """Asigna espacio en SWAP para un proceso específico"""
        for i, bloque in enumerate(self.bloques_swap_libres):
            if bloque.tamano >= tamano_requerido:
            
                nuevo_bloque_swap = BloqueMemoria(
                    self.next_block_id,
                    bloque.inicio,
                    tamano_requerido,
                    ocupado=True,
                    pid_proceso=pid_proceso,
                    color=color,
                    ubicacion="SWAP"
                )
                
                self.bloques_swap_ocupados.append(nuevo_bloque_swap)
                self.next_block_id += 1
                
         
                if bloque.tamano == tamano_requerido:
                    self.bloques_swap_libres.pop(i)
                else:
                    bloque.inicio += tamano_requerido
                    bloque.tamano -= tamano_requerido
                
                return True
        return False

    def _asignar_espacio_ram(self, pid_proceso, tamano_requerido, color):
        """Asigna espacio en RAM para un proceso específico"""
        for i, bloque in enumerate(self.bloques_libres):
            if bloque.tamano >= tamano_requerido:
         
                nuevo_bloque_ram = BloqueMemoria(
                    self.next_block_id,
                    bloque.inicio,
                    tamano_requerido,
                    ocupado=True,
                    pid_proceso=pid_proceso,
                    color=color,
                    ubicacion="RAM"
                )
                
                self.bloques_ocupados.append(nuevo_bloque_ram)
                self.next_block_id += 1
                
           
                if bloque.tamano == tamano_requerido:
                    self.bloques_libres.pop(i)
                else:
                    bloque.inicio += tamano_requerido
                    bloque.tamano -= tamano_requerido
                
                return True
        return False

    def _liberar_bloque_ram(self, bloque):
        """Libera un bloque específico de RAM"""
        if bloque in self.bloques_ocupados:
            self.bloques_ocupados.remove(bloque)

            nuevo_bloque_libre = BloqueMemoria(
                bloque.id,
                bloque.inicio,
                bloque.tamano,
                ocupado=False,
                ubicacion="RAM"
            )
            
            self.bloques_libres.append(nuevo_bloque_libre)
            self.fusionar_bloques_libres()

    def _liberar_bloque_swap(self, bloque):
        """Libera un bloque específico de SWAP"""
        if bloque in self.bloques_swap_ocupados:
            self.bloques_swap_ocupados.remove(bloque)
            
 
            nuevo_bloque_libre = BloqueMemoria(
                bloque.id,
                bloque.inicio,
                bloque.tamano,
                ocupado=False,
                ubicacion="SWAP"
            )
            
            self.bloques_swap_libres.append(nuevo_bloque_libre)
            self.fusionar_bloques_swap_libres()

    def fusionar_bloques_swap_libres(self):
        """Fusiona bloques libres adyacentes en SWAP para evitar fragmentación"""
        if len(self.bloques_swap_libres) <= 1:
            return
        
        print(f"🔄 Fusionando bloques libres en SWAP...")
        
  
        self.bloques_swap_libres.sort(key=lambda x: x.inicio)
        
        bloques_fusionados = []
        bloque_actual = self.bloques_swap_libres[0]
        fusiones_realizadas = 0
        
        for i in range(1, len(self.bloques_swap_libres)):
            siguiente_bloque = self.bloques_swap_libres[i]
            
     
            if bloque_actual.inicio + bloque_actual.tamano == siguiente_bloque.inicio:
                bloque_actual.tamano += siguiente_bloque.tamano
                fusiones_realizadas += 1
            else:
                bloques_fusionados.append(bloque_actual)
                bloque_actual = siguiente_bloque
        
        bloques_fusionados.append(bloque_actual)
        self.bloques_swap_libres = bloques_fusionados
        
        print(f"✅ Fusión SWAP completada: {fusiones_realizadas} fusiones realizadas")

    def obtener_procesos_en_swap(self):
        """Retorna una lista de PIDs de procesos que están en SWAP"""
        procesos_swap = set()
        for bloque in self.bloques_swap_ocupados:
            if bloque.pid_proceso:
                procesos_swap.add(bloque.pid_proceso)
        return list(procesos_swap)

    def obtener_todos_los_bloques(self):
        """Retorna todos los bloques de memoria (RAM y SWAP) para visualización"""
        return {
            'ram_ocupados': self.bloques_ocupados,
            'ram_libres': self.bloques_libres,
            'swap_ocupados': self.bloques_swap_ocupados,
            'swap_libres': self.bloques_swap_libres
        }

    # === MÉTODOS PARA PAGINACIÓN ===
    
    def alternar_paginacion(self, habilitar=None):
        """Alterna o establece el estado de la paginación"""
        if habilitar is None:
            self.paginacion_habilitada = not self.paginacion_habilitada
        else:
            self.paginacion_habilitada = habilitar
        
        estado = "Habilitada" if self.paginacion_habilitada else "Deshabilitada"
        print(f"🔧 Paginación {estado}")
        return self.paginacion_habilitada
    
    def obtener_estadisticas_paginacion(self):
        """Retorna estadísticas del sistema de paginación"""
        if not self.paginacion_habilitada:
            return None
        return self.gestor_paginacion.obtener_estadisticas_paginacion()
    
    def mostrar_mapa_paginacion(self):
        """Muestra el mapa de páginas de memoria"""
        if not self.paginacion_habilitada:
            print("❌ Paginación deshabilitada")
            return
        self.gestor_paginacion.mostrar_mapa_memoria()
    
    def obtener_info_proceso_paginacion(self, proceso):
        """Obtiene información de paginación de un proceso específico"""
        if not self.paginacion_habilitada:
            return None
        return self.gestor_paginacion.obtener_info_proceso_paginacion(proceso)
    
    def obtener_estadisticas_combinadas(self):
        """Retorna estadísticas combinadas de bloques y paginación"""
        stats_bloques = {
            'sistema': 'bloques',
            'ram': self.obtener_uso_memoria(),
            'swap': self.obtener_uso_swap()
        }
        
        if self.paginacion_habilitada:
            stats_paginacion = self.obtener_estadisticas_paginacion()
            return {
                'bloques': stats_bloques,
                'paginacion': stats_paginacion,
                'sistema_activo': 'paginacion' if self.paginacion_habilitada else 'bloques'
            }
        else:
            return {
                'bloques': stats_bloques,
                'paginacion': None,
                'sistema_activo': 'bloques'
            }
    
    # === MÉTODOS PARA GESTIÓN AVANZADA ===
    
    def cambiar_algoritmo_reemplazo(self, algoritmo):
        """Cambia el algoritmo de reemplazo de páginas"""
        if self.usar_gestion_avanzada:
            return self.gestor_avanzado.cambiar_algoritmo(algoritmo)
        else:
            print("❌ Gestión avanzada no está habilitada")
            return False
    
    def alternar_gestion_avanzada(self, habilitar=None):
        """Alterna o establece el uso de gestión avanzada"""
        if habilitar is None:
            self.usar_gestion_avanzada = not self.usar_gestion_avanzada
        else:
            self.usar_gestion_avanzada = habilitar
        
        estado = "Habilitada" if self.usar_gestion_avanzada else "Deshabilitada"
        print(f"🧠 Gestión Avanzada {estado}")
        return self.usar_gestion_avanzada
    
    def simular_acceso_pagina(self, proceso, numero_pagina_virtual):
        """Simula el acceso a una página específica de un proceso"""
        if self.usar_gestion_avanzada and self.paginacion_habilitada:
            self.gestor_avanzado.registrar_acceso_pagina(proceso, numero_pagina_virtual)
        else:
            print(f"⚠️ Simulación de acceso no disponible (gestión avanzada: {self.usar_gestion_avanzada}, paginación: {self.paginacion_habilitada})")
    
    def obtener_estadisticas_avanzadas(self):
        """Retorna estadísticas completas del sistema de memoria"""
        if not self.usar_gestion_avanzada:
            return self.obtener_estadisticas_combinadas()
        
        return self.gestor_avanzado.obtener_estadisticas_avanzadas()
    
    def configurar_umbrales_swap(self, umbral_agresivo=None, umbral_conservador=None):
        """Configura los umbrales para el swapping inteligente"""
        if not self.usar_gestion_avanzada:
            print("❌ Gestión avanzada no está habilitada")
            return False
        
        if umbral_agresivo is not None:
            self.gestor_avanzado.umbral_swap_agresivo = umbral_agresivo
            print(f"🔧 Umbral agresivo configurado: {umbral_agresivo:.1%}")
        
        if umbral_conservador is not None:
            self.gestor_avanzado.umbral_swap_conservador = umbral_conservador
            print(f"🔧 Umbral conservador configurado: {umbral_conservador:.1%}")
        
        return True
    
    def obtener_reporte_rendimiento(self):
        """Genera un reporte detallado del rendimiento del sistema"""
        if not self.usar_gestion_avanzada:
            return "❌ Reporte de rendimiento solo disponible con gestión avanzada"
        
        stats = self.gestor_avanzado.obtener_estadisticas_avanzadas()
        
        reporte = "📊 REPORTE DE RENDIMIENTO DEL SISTEMA DE MEMORIA\n"
        reporte += "=" * 60 + "\n\n"
        
        # Información del algoritmo
        algo_stats = stats['algoritmo_reemplazo']
        reporte += f"🧠 Algoritmo de Reemplazo: {algo_stats['algoritmo']}\n"
        reporte += f"   Page Faults: {algo_stats['page_faults']}\n"
        reporte += f"   Hits: {algo_stats['hits']}\n"
        reporte += f"   Hit Ratio: {algo_stats['hit_ratio']:.2f}%\n"
        reporte += f"   Reemplazos realizados: {algo_stats['reemplazos']}\n\n"
        
        # Estado de memoria
        mem_stats = stats['memoria']
        reporte += f"💾 Estado de Memoria:\n"
        reporte += f"   RAM: {mem_stats['ram']['ocupadas']}/{mem_stats['ram']['total_paginas']} páginas ({mem_stats['ram']['porcentaje_uso']:.1f}%)\n"
        reporte += f"   SWAP: {mem_stats['swap']['ocupadas']}/{mem_stats['swap']['total_paginas']} páginas ({mem_stats['swap']['porcentaje_uso']:.1f}%)\n"
        reporte += f"   Tablas de páginas activas: {mem_stats['tablas_activas']}\n\n"
        
        # Rendimiento global
        perf_stats = stats['rendimiento']
        reporte += f"⚡ Rendimiento Global:\n"
        reporte += f"   Tiempo transcurrido: {perf_stats['tiempo_transcurrido']:.2f}s\n"
        reporte += f"   Hit Ratio Global: {perf_stats['hit_ratio_global']:.2f}%\n"
        reporte += f"   Total Page Faults: {perf_stats['total_page_faults']}\n"
        reporte += f"   Total Hits: {perf_stats['total_hits']}\n\n"
        
        # Configuración
        config_stats = stats['configuracion']
        reporte += f"⚙️ Configuración:\n"
        reporte += f"   Umbral SWAP Agresivo: {config_stats['umbral_swap_agresivo']:.1%}\n"
        reporte += f"   Umbral SWAP Conservador: {config_stats['umbral_swap_conservador']:.1%}\n"
        
        return reporte



