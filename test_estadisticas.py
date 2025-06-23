#!/usr/bin/env python3
"""
Test rápido para verificar que las estadísticas funcionen
"""

from simulador import Simulador
from proceso import Proceso

def test_estadisticas():
    print("🧪 Probando generación de estadísticas...")
    
    # Crear simulador
    simulador = Simulador(num_nucleos=2)
    simulador.configurar_algoritmo("SJF")
    
    # Crear procesos de prueba CON NOMBRES
    procesos = [
        Proceso(nombre="Navegador", tiempo_llegada=0, duracion=3, tamano_memoria=100*1024*1024),
        Proceso(nombre="Editor", tiempo_llegada=1, duracion=2, tamano_memoria=150*1024*1024),
        Proceso(nombre="Juego", tiempo_llegada=2, duracion=4, tamano_memoria=200*1024*1024)
    ]
    
    # Agregar al simulador
    for proceso in procesos:
        simulador.agregar_proceso(proceso)
    
    print(f"📋 Procesos agregados: {len(simulador.procesos_nuevos)}")
    
    # Ejecutar simulación
    simulador.iniciar_simulacion()
    
    pasos = 0
    while simulador.paso_simulacion() and pasos < 20:
        pasos += 1
        print(f"   Paso {pasos}: Nuevos={len(simulador.procesos_nuevos)}, Listos={len(simulador.cola_listos)}, Terminados={len(simulador.procesos_terminados)}")
    
    # Calcular estadísticas
    estadisticas = simulador.calcular_estadisticas()
    
    print(f"\n📊 RESULTADOS:")
    print(f"   Procesos terminados: {len(simulador.procesos_terminados)}")
    print(f"   Estadísticas de procesos: {len(estadisticas['procesos'])}")
    
    if estadisticas['procesos']:
        print(f"\n📋 DETALLE DE PROCESOS:")
        for proc in estadisticas['procesos']:
            print(f"   - {proc['nombre']} (PID {proc['pid']}): "
                  f"Espera={proc['tiempo_espera']:.1f}, "
                  f"Respuesta={proc['tiempo_respuesta']:.1f}, "
                  f"Retorno={proc['tiempo_retorno']:.1f}")
                  
        print(f"\n📈 PROMEDIOS:")
        promedios = estadisticas['promedios']
        print(f"   Tiempo de Espera: {promedios['tiempo_espera']:.2f}")
        print(f"   Tiempo de Respuesta: {promedios['tiempo_respuesta']:.2f}")
        print(f"   Tiempo de Retorno: {promedios['tiempo_retorno']:.2f}")
    else:
        print("❌ No se generaron estadísticas")
        
        # Debug: Revisar procesos terminados
        print(f"\n🔍 DEBUG - Procesos terminados:")
        for i, proc in enumerate(simulador.procesos_terminados):
            print(f"   {i+1}. {proc.nombre} - Primer ejecución: {proc.tiempo_primer_ejecucion}, Finalización: {proc.tiempo_finalizacion}")

if __name__ == "__main__":
    test_estadisticas()
