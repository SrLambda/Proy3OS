"""
Algoritmos de Reemplazo de Páginas - Implementa diferentes estrategias para mover páginas entre RAM y SWAP
"""

from typing import List, Optional, Dict
import time

class AlgoritmoReemplazo:
    """Clase base para algoritmos de reemplazo de páginas"""
    
    def __init__(self, nombre):
        self.nombre = nombre
        self.page_faults = 0
        self.hits = 0
        self.reemplazos_realizados = 0
    
    def seleccionar_pagina_victima(self, paginas_candidatas):
        """Selecciona la página a reemplazar. Debe ser implementado por subclases"""
        raise NotImplementedError("Subclases deben implementar este método")
    
    def registrar_acceso(self, pagina):
        """Registra el acceso a una página para estadísticas"""
        pass
    
    def obtener_estadisticas(self):
        """Retorna estadísticas del algoritmo"""
        total_accesos = self.hits + self.page_faults
        hit_ratio = (self.hits / total_accesos * 100) if total_accesos > 0 else 0
        
        return {
            'algoritmo': self.nombre,
            'page_faults': self.page_faults,
            'hits': self.hits,
            'hit_ratio': hit_ratio,
            'reemplazos': self.reemplazos_realizados
        }

class FIFO(AlgoritmoReemplazo):
    """First In, First Out - La página más antigua es reemplazada"""
    
    def __init__(self):
        super().__init__("FIFO")
        self.cola_paginas = []  # Lista que mantiene el orden de llegada
    
    def seleccionar_pagina_victima(self, paginas_candidatas):
        """Selecciona la página que llegó primero"""
        if not self.cola_paginas:
            return paginas_candidatas[0] if paginas_candidatas else None
        
        # Buscar la página más antigua que esté en las candidatas
        for pagina_antigua in self.cola_paginas:
            if pagina_antigua in paginas_candidatas:
                self.cola_paginas.remove(pagina_antigua)
                self.reemplazos_realizados += 1
                print(f"🔄 FIFO: Reemplazando página más antigua {pagina_antigua.numero}")
                return pagina_antigua
        
        # Si no encuentra, tomar la primera candidata
        return paginas_candidatas[0] if paginas_candidatas else None
    
    def registrar_acceso(self, pagina):
        """Registra una nueva página en la cola FIFO"""
        if pagina not in self.cola_paginas:
            self.cola_paginas.append(pagina)
            print(f"📝 FIFO: Página {pagina.numero} agregada a cola")

class LRU(AlgoritmoReemplazo):
    """Least Recently Used - La página menos recientemente usada es reemplazada"""
    
    def __init__(self):
        super().__init__("LRU")
        self.accesos_paginas = {}  # {pagina: timestamp_ultimo_acceso}
    
    def seleccionar_pagina_victima(self, paginas_candidatas):
        """Selecciona la página menos recientemente usada"""
        if not paginas_candidatas:
            return None
        
        # Encontrar la página con el timestamp más antiguo
        pagina_victima = min(paginas_candidatas, 
                           key=lambda p: self.accesos_paginas.get(p, 0))
        
        self.reemplazos_realizados += 1
        print(f"🔄 LRU: Reemplazando página menos usada {pagina_victima.numero}")
        
        # Remover de tracking
        if pagina_victima in self.accesos_paginas:
            del self.accesos_paginas[pagina_victima]
        
        return pagina_victima
    
    def registrar_acceso(self, pagina):
        """Registra el acceso a una página con timestamp"""
        self.accesos_paginas[pagina] = time.time()
        print(f"📝 LRU: Acceso registrado para página {pagina.numero}")

class LFU(AlgoritmoReemplazo):
    """Least Frequently Used - La página menos frecuentemente usada es reemplazada"""
    
    def __init__(self):
        super().__init__("LFU")
        self.frecuencias = {}  # {pagina: numero_de_accesos}
    
    def seleccionar_pagina_victima(self, paginas_candidatas):
        """Selecciona la página menos frecuentemente usada"""
        if not paginas_candidatas:
            return None
        
        # Encontrar la página con menor frecuencia
        pagina_victima = min(paginas_candidatas, 
                           key=lambda p: self.frecuencias.get(p, 0))
        
        self.reemplazos_realizados += 1
        print(f"🔄 LFU: Reemplazando página menos frecuente {pagina_victima.numero} (freq: {self.frecuencias.get(pagina_victima, 0)})")
        
        # Remover de tracking
        if pagina_victima in self.frecuencias:
            del self.frecuencias[pagina_victima]
        
        return pagina_victima
    
    def registrar_acceso(self, pagina):
        """Incrementa el contador de frecuencia"""
        self.frecuencias[pagina] = self.frecuencias.get(pagina, 0) + 1
        print(f"📝 LFU: Página {pagina.numero} freq: {self.frecuencias[pagina]}")

class GestorMemoriaAvanzado:
    """Gestor avanzado que incorpora algoritmos de reemplazo y optimizaciones"""
    
    def __init__(self, gestor_paginacion, algoritmo_reemplazo="LRU"):
        self.gestor_paginacion = gestor_paginacion
        self.algoritmos_disponibles = {
            "FIFO": FIFO(),
            "LRU": LRU(),
            "LFU": LFU()
        }
        
        self.algoritmo_actual = self.algoritmos_disponibles[algoritmo_reemplazo]
        print(f"🧠 Gestor de memoria inicializado con algoritmo: {algoritmo_reemplazo}")
        
        # Métricas avanzadas
        self.total_page_faults = 0
        self.total_hits = 0
        self.tiempo_inicio = time.time()
        
        # Configuración de optimización
        self.umbral_swap_agresivo = 0.8  # 80% RAM ocupada -> mover a SWAP
        self.umbral_swap_conservador = 0.6  # 60% RAM ocupada -> dejar en RAM
        
    def cambiar_algoritmo(self, nuevo_algoritmo):
        """Cambia el algoritmo de reemplazo en tiempo de ejecución"""
        if nuevo_algoritmo in self.algoritmos_disponibles:
            self.algoritmo_actual = self.algoritmos_disponibles[nuevo_algoritmo]
            print(f"🔄 Algoritmo cambiado a: {nuevo_algoritmo}")
            return True
        else:
            print(f"❌ Algoritmo '{nuevo_algoritmo}' no disponible")
            return False
    
    def asignar_memoria_inteligente(self, proceso):
        """Asignación inteligente que considera el estado de la memoria"""
        print(f"🧠 Asignación inteligente para P{proceso.pid}")
        
        # Obtener estado actual de memoria
        stats = self.gestor_paginacion.obtener_estadisticas_paginacion()
        porcentaje_ram = stats['uso_ram']  # Corregido: usar 'uso_ram' directamente
        
        print(f"   RAM ocupada: {porcentaje_ram:.1f}%")
        
        # Decidir estrategia basada en ocupación
        if porcentaje_ram < self.umbral_swap_conservador:
            print(f"   📈 RAM disponible, asignación normal")
            return self.gestor_paginacion.asignar_memoria_a_proceso(proceso)
        
        elif porcentaje_ram < self.umbral_swap_agresivo:
            print(f"   ⚠️ RAM moderadamente ocupada, liberando espacio preventivo")
            self._liberar_espacio_preventivo()
            return self.gestor_paginacion.asignar_memoria_a_proceso(proceso)
        
        else:
            print(f"   🚨 RAM crítica, aplicando reemplazo agresivo")
            return self._asignar_con_reemplazo_agresivo(proceso)
    
    def _liberar_espacio_preventivo(self):
        """Libera espacio en RAM moviendo páginas menos utilizadas al SWAP"""
        print("🧹 Liberación preventiva de espacio...")
        
        # Obtener páginas candidatas para mover a SWAP
        candidatas = []
        for pagina in self.gestor_paginacion.paginas_ram:
            if pagina.proceso_pid is not None:  # Página ocupada
                candidatas.append(pagina)
        
        if len(candidatas) <= 2:  # Mantener al menos algunas páginas en RAM
            return
        
        # Seleccionar páginas para mover usando el algoritmo actual
        num_paginas_a_mover = len(candidatas) // 4  # Mover 25% de las páginas
        
        for _ in range(min(num_paginas_a_mover, 5)):  # Máximo 5 páginas por vez
            pagina_victima = self.algoritmo_actual.seleccionar_pagina_victima(candidatas)
            if pagina_victima:
                self._mover_pagina_a_swap(pagina_victima)
                candidatas.remove(pagina_victima)
    
    def _asignar_con_reemplazo_agresivo(self, proceso):
        """Asignación con reemplazo agresivo cuando RAM está llena"""
        print("🔥 Aplicando reemplazo agresivo...")
        
        # Calcular páginas necesarias
        import math
        paginas_necesarias = math.ceil(proceso.tamano_memoria / self.gestor_paginacion.tamano_pagina)
        
        # Liberar páginas suficientes
        candidatas = [p for p in self.gestor_paginacion.paginas_ram if p.proceso_pid is not None]
        paginas_liberadas = 0
        
        while paginas_liberadas < paginas_necesarias and candidatas:
            pagina_victima = self.algoritmo_actual.seleccionar_pagina_victima(candidatas)
            if pagina_victima:
                self._mover_pagina_a_swap(pagina_victima)
                candidatas.remove(pagina_victima)
                paginas_liberadas += 1
        
        # Intentar asignación normal
        return self.gestor_paginacion.asignar_memoria_a_proceso(proceso)
    
    def _mover_pagina_a_swap(self, pagina):
        """Mueve una página de RAM a SWAP"""
        if pagina.proceso_pid is None:  # Página libre, no hay nada que mover
            return
        
        proceso_pid = pagina.proceso_pid
        print(f"💾 Moviendo página {pagina.numero} de P{proceso_pid} a SWAP")
        
        # Buscar espacio en SWAP
        for pagina_swap in self.gestor_paginacion.paginas_swap:
            if pagina_swap.proceso_pid is None:  # Página libre en SWAP
                # Transferir información
                pagina_swap.proceso_pid = proceso_pid
                pagina_swap.tiempo_acceso = pagina.tiempo_acceso
                pagina_swap.frecuencia_acceso = pagina.frecuencia_acceso
                
                # Liberar página en RAM
                pagina.proceso_pid = None
                pagina.tiempo_acceso = 0
                pagina.frecuencia_acceso = 0
                
                print(f"✅ Página movida exitosamente a SWAP[{pagina_swap.numero}]")
                return True
        
        print(f"❌ No hay espacio en SWAP para mover página")
        return False
        return False
    
    def registrar_acceso_pagina(self, proceso, numero_pagina_virtual):
        """Registra el acceso a una página para el algoritmo de reemplazo"""
        if proceso.pid in self.gestor_paginacion.tablas_paginas:
            tabla = self.gestor_paginacion.tablas_paginas[proceso.pid]
            if numero_pagina_virtual in tabla.entradas:
                entrada = tabla.entradas[numero_pagina_virtual]
                pagina_fisica = entrada['pagina_fisica']
                
                if entrada['presente']:
                    # Hit - página está en RAM
                    self.total_hits += 1
                    self.algoritmo_actual.registrar_acceso(pagina_fisica)
                    print(f"✅ HIT: P{proceso.pid} accedió a página {numero_pagina_virtual}")
                else:
                    # Page fault - página está en SWAP
                    self.total_page_faults += 1
                    self.algoritmo_actual.page_faults += 1
                    print(f"❌ PAGE FAULT: P{proceso.pid} página {numero_pagina_virtual} en SWAP")
                    self._traer_pagina_de_swap(proceso, numero_pagina_virtual)
    
    def _traer_pagina_de_swap(self, proceso, numero_pagina_virtual):
        """Trae una página desde SWAP a RAM"""
        print(f"📥 Trayendo página {numero_pagina_virtual} de P{proceso.pid} desde SWAP")
        
        # Buscar espacio libre en RAM o hacer reemplazo
        pagina_ram_libre = None
        for pagina in self.gestor_paginacion.paginas_ram:
            if pagina.proceso_pid is None:  # Página libre
                pagina_ram_libre = pagina
                break
        
        if not pagina_ram_libre:
            # Necesitamos hacer reemplazo
            candidatas = [p for p in self.gestor_paginacion.paginas_ram if p.proceso_pid is not None]
            if candidatas:
                pagina_victima = self.algoritmo_actual.seleccionar_pagina_victima(candidatas)
                if pagina_victima:
                    self._mover_pagina_a_swap(pagina_victima)
                    pagina_ram_libre = pagina_victima
        
        if pagina_ram_libre:
            # Asignar página al proceso (simplificado)
            pagina_ram_libre.proceso_pid = proceso.pid
            pagina_ram_libre.tiempo_acceso = self.gestor_paginacion.contador_tiempo
            pagina_ram_libre.frecuencia_acceso = 1
            
            print(f"✅ Página traída exitosamente a RAM[{pagina_ram_libre.numero}]")
            return True
        
        return False
    
    def obtener_estadisticas_avanzadas(self):
        """Retorna estadísticas detalladas del gestor avanzado"""
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        stats_algoritmo = self.algoritmo_actual.obtener_estadisticas()
        stats_paginacion = self.gestor_paginacion.obtener_estadisticas_paginacion()
        
        return {
            'algoritmo_reemplazo': stats_algoritmo,
            'memoria': stats_paginacion,
            'rendimiento': {
                'tiempo_transcurrido': tiempo_transcurrido,
                'total_hits': self.total_hits,
                'total_page_faults': self.total_page_faults,
                'hit_ratio_global': (self.total_hits / (self.total_hits + self.total_page_faults) * 100) if (self.total_hits + self.total_page_faults) > 0 else 0
            },
            'configuracion': {
                'umbral_swap_agresivo': self.umbral_swap_agresivo,
                'umbral_swap_conservador': self.umbral_swap_conservador
            }
        }
