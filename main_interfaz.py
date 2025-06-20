#!/usr/bin/env python3
"""
Script principal para ejecutar la interfaz gráfica integrada con el simulador
"""

import tkinter as tk
import sys
import os

# Agregar el directorio de la interfaz al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Interfaz'))

def main():
    """Función principal que inicializa la interfaz gráfica"""
    try:
        # Importar la interfaz
        from interfaz import SimuladorUI
        
        # Crear la ventana principal
        root = tk.Tk()
        
        # Crear la aplicación
        app = SimuladorUI(root)
        
        print("🖥️  Interfaz gráfica inicializada")
        print("📋 Controles disponibles:")
        print("   • Selecciona algoritmo: SJF o Round Robin")
        print("   • Configura quantum para Round Robin")
        print("   • Presiona 'Iniciar' para comenzar la simulación")
        print("   • Presiona 'Agregar Proceso' para añadir procesos aleatorios")
        print("   • Presiona 'Finalizar' para detener la simulación")
        print("🎯 La memoria RAM se visualiza en tiempo real")
        
        # Iniciar la aplicación
        app.iniciar()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que PIL (Pillow) esté instalado: pip install pillow")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        
if __name__ == "__main__":
    main()
