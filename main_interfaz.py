#!/usr/bin/env python3
"""
"""

import tkinter as tk
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), 'Interfaz'))

def main():
    
    try:
      
        from interfaz import SimuladorUI
        
     
        root = tk.Tk()
        
     
        app = SimuladorUI(root)
        
        print("🖥️  Interfaz gráfica inicializada")
        print("📋 Controles disponibles:")
        print("   • Selecciona algoritmo: SJF o Round Robin")
        print("   • Configura quantum para Round Robin")
        print("   • Presiona 'Iniciar' para comenzar la simulación")
        print("   • Presiona 'Agregar Proceso' para añadir procesos aleatorios")
        print("   • Presiona 'Finalizar' para detener la simulación")
        print("🎯 La memoria RAM se visualiza en tiempo real")
        
       
        app.iniciar()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que PIL (Pillow) esté instalado: pip install pillow")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        
if __name__ == "__main__":
    main()
