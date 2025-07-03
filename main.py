"""
SIMULADOR DE SISTEMA OPERATIVO - PUNTO DE ENTRADA PRINCIPAL
==========================================================

Este es el simulador de SO con gestión avanzada de memoria que incluye:
- Algoritmos de reemplazo de páginas (FIFO, LRU, LFU)
- Sistema de SWAP avanzado
- Interfaz gráfica completa con métricas en tiempo real
- Programas predefinidos con división automática en procesos
- Demostración visual de algoritmos

Para ejecutar: python main.py
"""

import sys
import os

# Añadir el directorio actual al path para importar los módulos
sys.path.append('.')

# Importar la interfaz
from Interfaz.interfaz import SimuladorUI
import tkinter as tk

def main():
    """Ejecuta el simulador de SO con gestión avanzada de memoria"""
    print("🚀 SIMULADOR DE SISTEMA OPERATIVO")
    print("=" * 60)
    print("✅ Funcionalidades disponibles:")
    print("   🧠 Algoritmos de reemplazo (FIFO, LRU, LFU)")
    print("   📊 Métricas avanzadas en tiempo real")
    print("   ⚙️ Configuración de umbrales de SWAP")
    print("   🖥️ Programas predefinidos con división automática")
    print("   🎯 Demostración de algoritmos")
    print("=" * 60)
    print("🎮 Instrucciones:")
    print("   1. Prueba agregar programas desde 'Añadir Proceso' → 'Programas Predefinidos'")
    print("   2. Cambia algoritmos desde el panel 'Configuración Avanzada'")
    print("   3. Observa las métricas en 'Métricas de Memoria Avanzadas'")
    print("   4. Usa 'Demo Algoritmos' para ver diferencias en rendimiento")
    print("   5. Ajusta umbrales de SWAP y aplica cambios")
    print("=" * 60)
    
    # Crear y ejecutar la interfaz
    root = tk.Tk()
    app = SimuladorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
