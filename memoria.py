from bloque_memoria import BloqueMemoria

class Memoria:
    def __init__(self, tamano_total_gb=2):
        self.tamano_total = tamano_total_gb * 1024 * 1024 * 1024  # Convertir GB a Bytes
        self.bloques_libres = [BloqueMemoria(0, 0, self.tamano_total, ocupado=False)]
        self.bloques_ocupados = []
        self.next_block_id = 1 # Para asignar IDs únicos a los bloques
        print(f"🖥️  Memoria inicializada: {tamano_total_gb} GB ({self.tamano_total:,} bytes)")

    def asignar_memoria(self, proceso):
        """Asigna memoria a un proceso usando algoritmo First-Fit"""
        tamano_requerido = proceso.tamano_memoria
        print(f"📋 Intentando asignar {tamano_requerido:,} bytes al proceso {proceso.pid}")
        
        # Buscar un bloque libre que sea suficientemente grande
        for i, bloque in enumerate(self.bloques_libres):
            if bloque.tamano >= tamano_requerido:
                print(f"✅ Bloque encontrado: {bloque.tamano:,} bytes en posición {bloque.inicio}")
                
                # Crear nuevo bloque ocupado
                nuevo_bloque_ocupado = BloqueMemoria(
                    self.next_block_id,
                    bloque.inicio,
                    tamano_requerido,
                    ocupado=True,
                    pid_proceso=proceso.pid
                )
                
                self.bloques_ocupados.append(nuevo_bloque_ocupado)
                proceso.bloques_memoria_asignados.append(nuevo_bloque_ocupado)
                self.next_block_id += 1
                
                # Si el bloque libre era exactamente del tamaño requerido, lo eliminamos
                if bloque.tamano == tamano_requerido:
                    print(f"🔄 Bloque usado completamente, eliminando de libres")
                    self.bloques_libres.pop(i)
                else:
                    # Reducir el tamaño del bloque libre
                    print(f"🔄 Fragmentando bloque: quedan {bloque.tamano - tamano_requerido:,} bytes libres")
                    bloque.inicio += tamano_requerido
                    bloque.tamano -= tamano_requerido
                
                print(f"🎉 Memoria asignada exitosamente al proceso {proceso.pid}")
                self._mostrar_estado_memoria()
                return True
        
        print(f"❌ No hay memoria suficiente para el proceso {proceso.pid}")
        return False
    

    def liberar_memoria(self, proceso):
        """Libera la memoria ocupada por un proceso"""
        print(f"🔓 Liberando memoria del proceso {proceso.pid}")
        bloques_a_liberar = []
        
        # Encontrar todos los bloques del proceso
        for bloque in self.bloques_ocupados:
            if bloque.pid_proceso == proceso.pid:
                bloques_a_liberar.append(bloque)
                print(f"📦 Liberando bloque: {bloque.tamano:,} bytes en posición {bloque.inicio}")
        
        # Mover bloques a libres
        for bloque in bloques_a_liberar:
            # Cambiar estado a libre
            bloque.ocupado = False
            bloque.pid_proceso = None
            self.bloques_libres.append(bloque)
            self.bloques_ocupados.remove(bloque)
            
            # Limpiar la lista de bloques asignados del proceso
            proceso.bloques_memoria_asignados.clear()
            
        # Fusionar bloques libres adyacentes
        print(f"🔄 Fusionando bloques libres adyacentes...")
        self.fusionar_bloques_libres()
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
            
            # Si los bloques son adyacentes, fusionar
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
        """Retorna estadísticas de uso de memoria"""
        memoria_ocupada = sum(bloque.tamano for bloque in self.bloques_ocupados)
        memoria_libre = sum(bloque.tamano for bloque in self.bloques_libres)
        porcentaje_uso = (memoria_ocupada / self.tamano_total) * 100
        
        return {
            'total': self.tamano_total,
            'ocupada': memoria_ocupada,
            'libre': memoria_libre,
            'porcentaje_uso': porcentaje_uso,
            'num_bloques_ocupados': len(self.bloques_ocupados),
            'num_bloques_libres': len(self.bloques_libres)
        }
        
    def hay_swapping_necesario(self, tamano_requerido):
        """Verifica si es necesario hacer swapping para asignar memoria"""
        memoria_libre_total = sum(bloque.tamano for bloque in self.bloques_libres)
        return memoria_libre_total < tamano_requerido
    
    def _mostrar_estado_memoria(self):
        """Método auxiliar para mostrar el estado actual de la memoria"""
        uso = self.obtener_uso_memoria()
        print(f"📊 Estado de Memoria:")
        print(f"   💾 Total: {uso['total']:,} bytes")
        print(f"   🔴 Ocupada: {uso['ocupada']:,} bytes ({uso['porcentaje_uso']:.1f}%)")
        print(f"   🟢 Libre: {uso['libre']:,} bytes")
        print(f"   📦 Bloques ocupados: {uso['num_bloques_ocupados']}")
        print(f"   📦 Bloques libres: {uso['num_bloques_libres']}")
        print(f"   --- Detalle de bloques libres ---")
        for i, bloque in enumerate(self.bloques_libres):
            print(f"     Bloque libre {i+1}: {bloque.tamano:,} bytes en posición {bloque.inicio}")
        print("   " + "="*40)
       


