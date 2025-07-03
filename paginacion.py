"""
Gestor de Paginación para el Simulador de SO
Maneja la paginación de memoria con soporte para SWAP
"""

class Pagina:
    """Representa una página de memoria"""
    def __init__(self, numero, ubicacion="RAM"):
        self.numero = numero
        self.ubicacion = ubicacion  # "RAM" o "SWAP"
        self.proceso_pid = None
        self.tiempo_acceso = 0
        self.frecuencia_acceso = 0
        self.dirty = False
        
    def __repr__(self):
        return f"Página {self.numero} ({self.ubicacion}) - PID: {self.proceso_pid}"

class ProcesoPaginado:
    """Información de paginación de un proceso"""
    def __init__(self, pid, tamano, tamano_pagina):
        self.pid = pid
        self.tamano = tamano
        self.paginas_necesarias = (tamano + tamano_pagina - 1) // tamano_pagina
        self.paginas_asignadas = []
        self.paginas_en_ram = []
        self.paginas_en_swap = []
        
    def agregar_pagina(self, pagina):
        """Agrega una página al proceso"""
        self.paginas_asignadas.append(pagina)
        if pagina.ubicacion == "RAM":
            self.paginas_en_ram.append(pagina)
        else:
            self.paginas_en_swap.append(pagina)
            
    def mover_pagina_a_swap(self, pagina):
        """Mueve una página de RAM a SWAP"""
        if pagina in self.paginas_en_ram:
            self.paginas_en_ram.remove(pagina)
            self.paginas_en_swap.append(pagina)
            pagina.ubicacion = "SWAP"
            
    def mover_pagina_a_ram(self, pagina):
        """Mueve una página de SWAP a RAM"""
        if pagina in self.paginas_en_swap:
            self.paginas_en_swap.remove(pagina)
            self.paginas_en_ram.append(pagina)
            pagina.ubicacion = "RAM"

class GestorPaginacion:
    """Gestor principal de paginación"""
    
    def __init__(self, tamano_pagina=16*1024*1024):  # 16MB por defecto
        self.tamano_pagina = tamano_pagina
        self.paginas_ram = []
        self.paginas_swap = []
        self.procesos_paginados = {}
        self.contador_tiempo = 0
        
        # Estadísticas
        self.page_faults = 0
        self.page_hits = 0
        self.swap_out = 0
        self.swap_in = 0
        
        print(f"🔧 Inicializando sistema de paginación:")
        print(f"   📄 Tamaño de página: {tamano_pagina} bytes ({tamano_pagina//1024}KB)")
        
    def inicializar_memoria(self, tamano_ram, tamano_swap):
        """Inicializa las páginas de RAM y SWAP"""
        num_paginas_ram = tamano_ram // self.tamano_pagina
        num_paginas_swap = tamano_swap // self.tamano_pagina
        
        # Crear páginas de RAM
        self.paginas_ram = [Pagina(i, "RAM") for i in range(num_paginas_ram)]
        
        # Crear páginas de SWAP
        self.paginas_swap = [Pagina(i + num_paginas_ram, "SWAP") for i in range(num_paginas_swap)]
        
        print(f"   🖥️  RAM: {num_paginas_ram} páginas ({tamano_ram//1024//1024//1024}GB)")
        print(f"   💿 SWAP: {num_paginas_swap} páginas ({tamano_swap//1024//1024//1024}GB)")
        
    def asignar_memoria_a_proceso(self, proceso):
        """Asigna memoria paginada a un proceso"""
        try:
            # Crear proceso paginado
            proceso_pag = ProcesoPaginado(proceso.pid, proceso.tamano_memoria, self.tamano_pagina)
            
            # Buscar páginas libres en RAM
            paginas_libres_ram = [p for p in self.paginas_ram if p.proceso_pid is None]
            
            paginas_asignadas = 0
            
            # Asignar páginas en RAM primero
            for pagina in paginas_libres_ram:
                if paginas_asignadas >= proceso_pag.paginas_necesarias:
                    break
                    
                pagina.proceso_pid = proceso.pid
                proceso_pag.agregar_pagina(pagina)
                paginas_asignadas += 1
                
            # Si no hay suficientes páginas en RAM, usar SWAP
            if paginas_asignadas < proceso_pag.paginas_necesarias:
                paginas_libres_swap = [p for p in self.paginas_swap if p.proceso_pid is None]
                
                for pagina in paginas_libres_swap:
                    if paginas_asignadas >= proceso_pag.paginas_necesarias:
                        break
                        
                    pagina.proceso_pid = proceso.pid
                    proceso_pag.agregar_pagina(pagina)
                    paginas_asignadas += 1
                    
            if paginas_asignadas >= proceso_pag.paginas_necesarias:
                self.procesos_paginados[proceso.pid] = proceso_pag
                return True
            else:
                # Liberar páginas asignadas parcialmente
                for pagina in proceso_pag.paginas_asignadas:
                    pagina.proceso_pid = None
                return False
                
        except Exception as e:
            print(f"❌ Error asignando memoria paginada al proceso {proceso.pid}: {e}")
            return False
            
    def liberar_memoria_proceso(self, proceso):
        """Libera todas las páginas de un proceso"""
        if proceso.pid in self.procesos_paginados:
            proceso_pag = self.procesos_paginados[proceso.pid]
            
            for pagina in proceso_pag.paginas_asignadas:
                pagina.proceso_pid = None
                pagina.tiempo_acceso = 0
                pagina.frecuencia_acceso = 0
                pagina.dirty = False
                
            del self.procesos_paginados[proceso.pid]
            
    def obtener_estadisticas_paginacion(self):
        """Retorna estadísticas de paginación"""
        total_accesos = self.page_hits + self.page_faults
        hit_ratio = (self.page_hits / total_accesos * 100) if total_accesos > 0 else 0
        
        # Calcular uso de memoria
        paginas_ram_ocupadas = len([p for p in self.paginas_ram if p.proceso_pid is not None])
        paginas_swap_ocupadas = len([p for p in self.paginas_swap if p.proceso_pid is not None])
        
        uso_ram = (paginas_ram_ocupadas / len(self.paginas_ram) * 100) if self.paginas_ram else 0
        uso_swap = (paginas_swap_ocupadas / len(self.paginas_swap) * 100) if self.paginas_swap else 0
        
        return {
            'page_faults': self.page_faults,
            'page_hits': self.page_hits,
            'hit_ratio': hit_ratio,
            'swap_in': self.swap_in,
            'swap_out': self.swap_out,
            'uso_ram': uso_ram,
            'uso_swap': uso_swap,
            'paginas_ram_ocupadas': paginas_ram_ocupadas,
            'paginas_ram_total': len(self.paginas_ram),
            'paginas_swap_ocupadas': paginas_swap_ocupadas,
            'paginas_swap_total': len(self.paginas_swap)
        }
        
    def simular_acceso_pagina(self, proceso_pid):
        """Simula el acceso a una página de un proceso"""
        self.contador_tiempo += 1
        
        if proceso_pid in self.procesos_paginados:
            proceso_pag = self.procesos_paginados[proceso_pid]
            
            if proceso_pag.paginas_en_ram:
                # Hit - página está en RAM
                self.page_hits += 1
                pagina = proceso_pag.paginas_en_ram[0]
                pagina.tiempo_acceso = self.contador_tiempo
                pagina.frecuencia_acceso += 1
            else:
                # Miss - página necesita cargarse desde SWAP
                self.page_faults += 1
                
    def mostrar_mapa_memoria(self):
        """Muestra el estado actual de la memoria"""
        print("\n📊 MAPA DE MEMORIA:")
        print(f"RAM: {len([p for p in self.paginas_ram if p.proceso_pid is not None])}/{len(self.paginas_ram)} páginas ocupadas")
        print(f"SWAP: {len([p for p in self.paginas_swap if p.proceso_pid is not None])}/{len(self.paginas_swap)} páginas ocupadas")
        
    def obtener_info_proceso_paginacion(self, proceso):
        """Obtiene información de paginación de un proceso específico"""
        if proceso.pid in self.procesos_paginados:
            proceso_pag = self.procesos_paginados[proceso.pid]
            return {
                'paginas_necesarias': proceso_pag.paginas_necesarias,
                'paginas_en_ram': len(proceso_pag.paginas_en_ram),
                'paginas_en_swap': len(proceso_pag.paginas_en_swap),
                'paginas_totales': len(proceso_pag.paginas_asignadas)
            }
        return None
