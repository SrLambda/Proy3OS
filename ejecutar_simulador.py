#!/usr/bin/env python3
"""
Test simple del simulador
"""

import tkinter as tk
from Interfaz.interfaz import SimuladorUI

def test_simulador():
    """Ejecuta el simulador en modo gráfico"""
    print("🚀 SIMULADOR DE SO - EJECUTANDO...")
    print("✅ Interfaz gráfica con gestión avanzada de memoria")
    
    # Crear ventana principal
    root = tk.Tk()
    
    # Crear aplicación
    app = SimuladorUI(root)
    
    # Ejecutar interfaz
    print("🎮 Interfaz lista. ¡Disfruta del simulador!")
    root.mainloop()

if __name__ == "__main__":
    test_simulador()
