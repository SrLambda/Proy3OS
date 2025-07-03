"""
CASOS DE PRUEBA PARA EL SIMULADOR DE SO
========================================

Este script proporciona casos de prueba específicos para validar
todas las funcionalidades de la interfaz gráfica avanzada.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import time

# Configurar path
sys.path.append('.')

def mostrar_instrucciones():
    """Muestra las instrucciones de prueba"""
    print("🧪 CASOS DE PRUEBA PARA EL SIMULADOR DE SO")
    print("=" * 60)
    print("📋 CHECKLIST DE FUNCIONALIDADES A PROBAR:")
    print()
    
    print("🎯 1. FUNCIONALIDADES BÁSICAS:")
    print("   ✅ Interfaz se abre correctamente")
    print("   ✅ Paneles se muestran sin errores")
    print("   ✅ Botones responden al click")
    print("   ✅ Play/Pause/Reset funcionan")
    print()
    
    print("🧠 2. GESTIÓN DE PROCESOS:")
    print("   ✅ Agregar proceso manual")
    print("   ✅ Agregar programas predefinidos")
    print("   ✅ División automática en procesos hijos")
    print("   ✅ Terminación de procesos")
    print("   ✅ Visualización en tiempo real")
    print()
    
    print("💾 3. ALGORITMOS DE MEMORIA:")
    print("   ✅ Cambio de algoritmo FIFO")
    print("   ✅ Cambio de algoritmo LRU")
    print("   ✅ Cambio de algoritmo LFU")
    print("   ✅ Aplicar configuración")
    print()
    
    print("📊 4. MÉTRICAS AVANZADAS:")
    print("   ✅ Page faults actualizándose")
    print("   ✅ Hit ratio cambiando")
    print("   ✅ Uso de RAM/SWAP en tiempo real")
    print("   ✅ Fragmentación detectándose")
    print()
    
    print("🎯 5. DEMOSTRACIONES:")
    print("   ✅ Demo de algoritmos ejecutándose")
    print("   ✅ Comparación de rendimiento")
    print("   ✅ Gráficos actualizándose")
    print()
    
    print("⚙️ 6. CONFIGURACIÓN AVANZADA:")
    print("   ✅ Cambio de umbrales SWAP")
    print("   ✅ Configuración aplicándose")
    print("   ✅ Efectos visibles en métricas")
    print()

def casos_de_prueba_especificos():
    """Lista casos de prueba específicos paso a paso"""
    print("\n🔬 CASOS DE PRUEBA ESPECÍFICOS:")
    print("=" * 60)
    
    casos = [
        {
            "nombre": "Caso 1: Prueba de Carga Básica",
            "pasos": [
                "1. Ejecutar: python main.py",
                "2. Verificar que aparecen todos los paneles",
                "3. Click en 'Añadir Proceso'",
                "4. Crear proceso: PID=1, Tamaño=100MB, Duración=5s",
                "5. Click 'Agregar' y verificar que aparece en la lista",
                "6. Click 'Play' y observar ejecución",
                "7. Verificar métricas actualizándose"
            ],
            "resultado_esperado": "Proceso se ejecuta, métricas se actualizan, memoria se asigna correctamente"
        },
        {
            "nombre": "Caso 2: Programas Predefinidos",
            "pasos": [
                "1. Click 'Añadir Proceso' → 'Programas Predefinidos'",
                "2. Seleccionar 'Navegador Web'",
                "3. Click 'Lanzar Programa'",
                "4. Observar que se crean múltiples procesos hijos",
                "5. Verificar diferentes tamaños de memoria",
                "6. Ejecutar simulación"
            ],
            "resultado_esperado": "Se crean 3-4 procesos hijos automáticamente con diferentes características"
        },
        {
            "nombre": "Caso 3: Cambio de Algoritmos",
            "pasos": [
                "1. Agregar 3-4 procesos de diferentes tamaños",
                "2. En 'Configuración Avanzada' seleccionar FIFO",
                "3. Click 'Aplicar Configuración'",
                "4. Ejecutar simulación y observar métricas",
                "5. Pausar, cambiar a LRU, aplicar",
                "6. Continuar y comparar métricas",
                "7. Repetir con LFU"
            ],
            "resultado_esperado": "Diferentes algoritmos muestran diferentes ratios de page faults y hit ratio"
        },
        {
            "nombre": "Caso 4: Saturación de Memoria",
            "pasos": [
                "1. Agregar muchos procesos grandes (500MB+ cada uno)",
                "2. Ejecutar hasta llenar RAM",
                "3. Observar uso de SWAP incrementándose",
                "4. Verificar page faults aumentando",
                "5. Observar procesos moviéndose a SWAP"
            ],
            "resultado_esperado": "SWAP se activa, page faults aumentan, rendimiento se degrada visiblemente"
        },
        {
            "nombre": "Caso 5: Demo de Algoritmos",
            "pasos": [
                "1. Click 'Demo Algoritmos'",
                "2. Observar ventana de demostración",
                "3. Ver comparación automática de algoritmos",
                "4. Analizar gráficos y estadísticas",
                "5. Verificar diferencias de rendimiento"
            ],
            "resultado_esperado": "Se muestra comparación clara entre FIFO, LRU y LFU con estadísticas"
        },
        {
            "nombre": "Caso 6: Configuración de SWAP",
            "pasos": [
                "1. Cambiar 'Umbral SWAP' a 60%",
                "2. Click 'Aplicar Configuración'",
                "3. Agregar procesos hasta 60% de RAM",
                "4. Verificar que SWAP se activa antes",
                "5. Cambiar umbral a 90% y repetir"
            ],
            "resultado_esperado": "SWAP se activa en diferentes momentos según el umbral configurado"
        },
        {
            "nombre": "Caso 7: Estrés de la Interfaz",
            "pasos": [
                "1. Agregar 10+ procesos simultáneamente",
                "2. Cambiar algoritmos repetidamente",
                "3. Play/Pause/Reset varias veces",
                "4. Verificar que la interfaz no se cuelga",
                "5. Verificar métricas consistentes"
            ],
            "resultado_esperado": "Interfaz mantiene responsividad, datos consistentes, sin errores"
        }
    ]
    
    for i, caso in enumerate(casos, 1):
        print(f"\n📋 {caso['nombre']}")
        print("-" * 40)
        for paso in caso['pasos']:
            print(f"   {paso}")
        print(f"🎯 Resultado esperado: {caso['resultado_esperado']}")
        print()

def ejecutar_con_datos_test():
    """Ejecuta el simulador con datos de prueba preconfigurados"""
    print("\n🚀 EJECUTANDO SIMULADOR CON DATOS DE PRUEBA...")
    
    try:
        from Interfaz.interfaz import SimuladorUI
        
        root = tk.Tk()
        app = SimuladorUI(root)
        
        # Mensaje de bienvenida para testing
        messagebox.showinfo(
            "🧪 MODO DE PRUEBAS",
            "SIMULADOR EN MODO DE PRUEBAS\n\n"
            "✅ Todas las funcionalidades están activas\n"
            "📊 Métricas en tiempo real habilitadas\n"
            "🧠 Algoritmos FIFO, LRU, LFU listos\n"
            "🎯 Demos y programas predefinidos disponibles\n\n"
            "¡Comienza a probar las funcionalidades!"
        )
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error ejecutando simulador: {e}")
        return False
    
    return True

def main():
    """Función principal del script de pruebas"""
    mostrar_instrucciones()
    casos_de_prueba_especificos()
    
    print("🔧 HERRAMIENTAS DE TESTING:")
    print("=" * 40)
    print("1. python casos_prueba.py        - Ver esta guía")
    print("2. python main.py               - Ejecutar simulador normal")
    print("3. python ejecutar_simulador.py - Ejecutar versión simple")
    print()
    
    respuesta = input("¿Deseas ejecutar el simulador para testing? (s/n): ").lower()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        ejecutar_con_datos_test()

if __name__ == "__main__":
    main()
