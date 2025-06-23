#!/usr/bin/env python3
"""
Test simple de estadísticas de la interfaz
"""

import sys
import os
sys.path.append('Interfaz')

from interfaz import SimuladorUI
import tkinter as tk

def test_estadisticas_interfaz():
    """Test para verificar estadísticas en la interfaz"""
    print("🧪 Probando estadísticas de la interfaz...")
    
    # Crear ventana principal
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Crear aplicación
    app = SimuladorUI(root)
    
    # Ejecutar algunos pasos de simulación programáticamente
    app.simulador.iniciar_simulacion()
    
    # Ejecutar varios pasos
    for i in range(15):
        if not app.simulador.paso_simulacion():
            break
    
    print(f"📊 Procesos terminados: {len(app.simulador.procesos_terminados)}")
    
    # Llamar directamente al método de estadísticas
    app.mostrar_estadisticas()
    
    # Mantener ventana abierta por un momento
    root.after(5000, root.quit)  # Cerrar después de 5 segundos
    root.mainloop()

if __name__ == "__main__":
    test_estadisticas_interfaz()
