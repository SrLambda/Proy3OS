#!/usr/bin/env python3
"""
Prueba de la clase Memoria
"""

from proceso import Proceso
from memoria import Memoria

def probar_memoria():
    print("🚀 === PRUEBA DE LA CLASE MEMORIA ===\n")
    
    # Crear memoria de 1 GB para pruebas más rápidas
    memoria = Memoria(tamano_total_gb=1)
    print()
    
    # Crear algunos procesos de prueba
    proceso1 = Proceso(pid=1, tiempo_llegada=0, duracion=5, tamano_memoria=200*1024*1024)  # 200MB
    proceso2 = Proceso(pid=2, tiempo_llegada=1, duracion=3, tamano_memoria=300*1024*1024)  # 300MB
    proceso3 = Proceso(pid=3, tiempo_llegada=2, duracion=4, tamano_memoria=150*1024*1024)  # 150MB
    proceso4 = Proceso(pid=4, tiempo_llegada=3, duracion=2, tamano_memoria=600*1024*1024)  # 600MB (muy grande)
    
    print("📋 Procesos creados:")
    print(f"   - {proceso1}")
    print(f"   - {proceso2}")
    print(f"   - {proceso3}")
    print(f"   - {proceso4}")
    print()
    
    # Probar asignación de memoria
    print("🔵 === PRUEBA 1: Asignación de Memoria ===")
    memoria.asignar_memoria(proceso1)
    print()
    
    memoria.asignar_memoria(proceso2)
    print()
    
    memoria.asignar_memoria(proceso3)
    print()
    
    # Intentar asignar un proceso muy grande
    print("🔵 === PRUEBA 2: Proceso que no cabe ===")
    memoria.asignar_memoria(proceso4)
    print()
    
    # Liberar memoria del proceso 2
    print("🔵 === PRUEBA 3: Liberación de Memoria ===")
    memoria.liberar_memoria(proceso2)
    print()
    
    # Ahora intentar asignar el proceso grande otra vez
    print("🔵 === PRUEBA 4: Reasignación después de liberación ===")
    memoria.asignar_memoria(proceso4)
    print()
    
    # Liberar todos los procesos
    print("🔵 === PRUEBA 5: Liberación completa ===")
    memoria.liberar_memoria(proceso1)
    print()
    
    memoria.liberar_memoria(proceso3)
    print()
    
    if proceso4.bloques_memoria_asignados:
        memoria.liberar_memoria(proceso4)
        print()
    
    print("✅ === PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    probar_memoria()
