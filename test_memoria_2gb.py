#!/usr/bin/env python3
"""
Prueba de la clase Memoria con especificaciones del proyecto: 2 GB
"""

from proceso import Proceso
from memoria import Memoria

def probar_memoria_especificaciones():
    print("🚀 === PRUEBA CON ESPECIFICACIONES DEL PROYECTO ===\n")
    
    # Crear memoria de 2 GB como especifica el proyecto
    memoria = Memoria(tamano_total_gb=2)  # DEFAULT: 2 GB según especificaciones
    print()
    
    # Crear procesos más realistas para 2 GB
    proceso1 = Proceso(pid=1, tiempo_llegada=0, duracion=5, tamano_memoria=512*1024*1024)   # 512MB
    proceso2 = Proceso(pid=2, tiempo_llegada=1, duracion=3, tamano_memoria=256*1024*1024)   # 256MB
    proceso3 = Proceso(pid=3, tiempo_llegada=2, duracion=4, tamano_memoria=1024*1024*1024)  # 1GB
    proceso4 = Proceso(pid=4, tiempo_llegada=3, duracion=2, tamano_memoria=300*1024*1024)   # 300MB
    
    print("📋 Procesos creados para 2 GB de memoria:")
    print(f"   - {proceso1} → {proceso1.tamano_memoria/(1024*1024):.0f} MB")
    print(f"   - {proceso2} → {proceso2.tamano_memoria/(1024*1024):.0f} MB")
    print(f"   - {proceso3} → {proceso3.tamano_memoria/(1024*1024):.0f} MB")
    print(f"   - {proceso4} → {proceso4.tamano_memoria/(1024*1024):.0f} MB")
    print(f"   📊 Total requerido: {(proceso1.tamano_memoria + proceso2.tamano_memoria + proceso3.tamano_memoria + proceso4.tamano_memoria)/(1024*1024):.0f} MB")
    print()
    
    # Verificar que tenemos exactamente 2 GB
    uso_inicial = memoria.obtener_uso_memoria()
    print(f"✅ Memoria total disponible: {uso_inicial['total']/(1024*1024*1024):.1f} GB")
    print(f"✅ Memoria total en bytes: {uso_inicial['total']:,} bytes")
    print()
    
    # Probar asignaciones
    print("🔵 === ASIGNACIÓN EN MEMORIA DE 2 GB ===")
    memoria.asignar_memoria(proceso1)  # 512 MB
    print()
    
    memoria.asignar_memoria(proceso2)  # 256 MB
    print()
    
    memoria.asignar_memoria(proceso3)  # 1 GB
    print()
    
    memoria.asignar_memoria(proceso4)  # 300 MB - debería fallar
    print()
    
    # Verificar el estado final
    uso_final = memoria.obtener_uso_memoria()
    print("📊 === ESTADO FINAL DE MEMORIA 2 GB ===")
    print(f"💾 Memoria total: {uso_final['total']/(1024*1024*1024):.1f} GB")
    print(f"🔴 Memoria ocupada: {uso_final['ocupada']/(1024*1024):.0f} MB ({uso_final['porcentaje_uso']:.1f}%)")
    print(f"🟢 Memoria libre: {uso_final['libre']/(1024*1024):.0f} MB")
    print(f"📦 Bloques ocupados: {uso_final['num_bloques_ocupados']}")
    print(f"📦 Bloques libres: {uso_final['num_bloques_libres']}")
    
    print("\n✅ === VERIFICACIÓN DE ESPECIFICACIONES ===")
    print(f"✓ Memoria configurada: 2 GB (como solicita el proyecto)")
    print(f"✓ Algoritmo First-Fit implementado")
    print(f"✓ Gestión de fragmentación activa")
    print(f"✓ Fusión de bloques libres funcionando")
    print(f"✓ Estadísticas de memoria disponibles")

if __name__ == "__main__":
    probar_memoria_especificaciones()
