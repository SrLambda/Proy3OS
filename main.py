#!/usr/bin/env python3
"""
Simulador de Sistema Operativo
Este archivo principal demuestra el uso del simulador de SO
"""

from proceso import Proceso
from simulador import Simulador
import random

def crear_procesos_ejemplo():
    """Crea una lista de procesos de ejemplo para la simulación"""
    procesos = [
        Proceso(pid=1, tiempo_llegada=0, duracion=5, tamano_memoria=100*1024*1024),  # 100MB
        Proceso(pid=2, tiempo_llegada=1, duracion=3, tamano_memoria=200*1024*1024),  # 200MB
        Proceso(pid=3, tiempo_llegada=2, duracion=8, tamano_memoria=150*1024*1024),  # 150MB
        Proceso(pid=4, tiempo_llegada=3, duracion=2, tamano_memoria=300*1024*1024),  # 300MB
        Proceso(pid=5, tiempo_llegada=4, duracion=6, tamano_memoria=250*1024*1024),  # 250MB
    ]
    return procesos

def ejecutar_simulacion_sjf():
    """Ejecuta simulación con algoritmo SJF"""
    print("\n=== SIMULACIÓN CON ALGORITMO SJF ===\n")
    
    simulador = Simulador(num_nucleos=2)
    simulador.configurar_algoritmo("SJF")
    
    # Crear procesos de prueba con tamaños de memoria en MB
    procesos = [
        Proceso(1, 0, 5, 100 * 1024 * 1024),  # 100 MB
        Proceso(2, 1, 3, 200 * 1024 * 1024),  # 200 MB
        Proceso(3, 2, 8, 150 * 1024 * 1024),  # 150 MB
        Proceso(4, 3, 2, 300 * 1024 * 1024),  # 300 MB
        Proceso(5, 4, 6, 250 * 1024 * 1024),  # 250 MB
    ]
    
    for proceso in procesos:
        simulador.agregar_proceso(proceso)
    
    print("Iniciando simulación...")
    
    paso = 0
    while simulador.paso_simulacion() and paso < 10:
        simulador.mostrar_estado()
        paso += 1
    
    estadisticas = simulador.calcular_estadisticas()
    
    print(f"\n=== ESTADÍSTICAS FINALES SJF ===")
    for clave, valor in estadisticas.items():
        print(f"{clave}: {valor}")
    
    return estadisticas

def ejecutar_simulacion_round_robin():
    """Ejecuta simulación con algoritmo Round Robin"""
    print("\n=== SIMULACIÓN CON ALGORITMO ROUND ROBIN ===\n")
    
    simulador = Simulador(num_nucleos=2)
    simulador.configurar_algoritmo("RR")
    
    # Crear procesos con RÁFAGAS MÁS LARGAS y tamaños de memoria en MB
    procesos = [
        Proceso(1, 0, 8, 100 * 1024 * 1024),   # 8 unidades, 100 MB
        Proceso(2, 1, 6, 200 * 1024 * 1024),   # 6 unidades, 200 MB
        Proceso(3, 2, 10, 150 * 1024 * 1024),  # 10 unidades, 150 MB
        Proceso(4, 3, 4, 300 * 1024 * 1024),   # 4 unidades, 300 MB
        Proceso(5, 4, 12, 250 * 1024 * 1024),  # 12 unidades, 250 MB
    ]
    
    for proceso in procesos:
        simulador.agregar_proceso(proceso)
    
    print("Iniciando simulación...")
    
    paso = 0
    while simulador.paso_simulacion() and paso < 50:  # Límite aumentado
        simulador.mostrar_estado()
        paso += 1
    
    estadisticas = simulador.calcular_estadisticas()
    
    print(f"\n=== ESTADÍSTICAS FINALES ROUND ROBIN ===")
    for clave, valor in estadisticas.items():
        print(f"{clave}: {valor}")
    
    return estadisticas

def crear_procesos_aleatorios(num_procesos=10):
    """Crea procesos con características aleatorias"""
    procesos = []
    for i in range(num_procesos):
        proceso = Proceso(
            pid=i+1,
            tiempo_llegada=random.randint(0, 10),
            duracion=random.randint(2, 15),
            tamano_memoria=random.randint(50, 400) * 1024 * 1024  # 50MB a 400MB
        )
        procesos.append(proceso)
    return procesos

def simulacion_interactiva():
    """Permite al usuario configurar y ejecutar una simulación personalizada"""
    print("\n=== SIMULACIÓN INTERACTIVA ===")
    
    # Configuración del simulador
    try:
        num_nucleos = int(input("Número de núcleos de CPU (default: 2): ") or "2")
        algoritmo = input("Algoritmo de planificación (SJF/Round Robin) [default: SJF]: ") or "SJF"
        
        simulador = Simulador(num_nucleos=num_nucleos)
        simulador.set_algoritmo_planificacion(algoritmo)
        
        if algoritmo == "Round Robin":
            quantum = int(input("Quantum para Round Robin (default: 3): ") or "3")
            simulador.set_quantum(quantum)
        
        # Tipo de procesos
        tipo_procesos = input("¿Usar procesos aleatorios? (s/n) [default: n]: ") or "n"
        
        if tipo_procesos.lower() == 's':
            num_procesos = int(input("Número de procesos aleatorios (default: 5): ") or "5")
            procesos = crear_procesos_aleatorios(num_procesos)
        else:
            procesos = crear_procesos_ejemplo()
        
        # Agregar procesos al simulador
        for proceso in procesos:
            simulador.agregar_proceso(proceso)
        
        print(f"\nConfiguración:")
        print(f"- Núcleos: {num_nucleos}")
        print(f"- Algoritmo: {algoritmo}")
        if algoritmo == "Round Robin":
            print(f"- Quantum: {quantum}")
        print(f"- Procesos: {len(procesos)}")
        
        input("\nPresiona Enter para iniciar la simulación...")
        
        # Ejecutar simulación
        simulador.iniciar_simulacion()
        
        paso = 0
        while simulador.paso_simulacion() and paso < 100:
            if paso % 3 == 0:
                simulador.mostrar_estado()
                input("Presiona Enter para continuar...")
            paso += 1
        
        # Estadísticas finales
        print("\n=== ESTADÍSTICAS FINALES ===")
        estadisticas = simulador.calcular_estadisticas()
        for clave, valor in estadisticas.items():
            print(f"{clave}: {valor}")
        
    except ValueError as e:
        print(f"Error en la entrada: {e}")
    except KeyboardInterrupt:
        print("\nSimulación interrumpida por el usuario.")

def main():
    """Función principal del programa"""
    print("Simulador de Sistema Operativo")
    print("==============================")
    
    while True:
        print("\nOpciones:")
        print("1. Ejecutar simulación SJF")
        print("2. Ejecutar simulación Round Robin")
        print("3. Comparar algoritmos")
        print("4. Simulación interactiva")
        print("5. Salir")
        
        opcion = input("\nSelecciona una opción (1-5): ")
        
        if opcion == "1":
            ejecutar_simulacion_sjf()
        elif opcion == "2":
            ejecutar_simulacion_round_robin()
        elif opcion == "3":
            print("Comparando algoritmos...")
            stats_sjf = ejecutar_simulacion_sjf()
            stats_rr = ejecutar_simulacion_round_robin()
            
            print("\n=== COMPARACIÓN DE ALGORITMOS ===")
            print(f"SJF - Tiempo promedio de retorno: {stats_sjf.get('tiempo_promedio_retorno', 0):.2f}")
            print(f"Round Robin - Tiempo promedio de retorno: {stats_rr.get('tiempo_promedio_retorno', 0):.2f}")
            print(f"SJF - Tiempo promedio de respuesta: {stats_sjf.get('tiempo_promedio_respuesta', 0):.2f}")
            print(f"Round Robin - Tiempo promedio de respuesta: {stats_rr.get('tiempo_promedio_respuesta', 0):.2f}")
            
        elif opcion == "4":
            simulacion_interactiva()
        elif opcion == "5":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, selecciona un número del 1 al 5.")

if __name__ == "__main__":
    main()
