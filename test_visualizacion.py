#!/usr/bin/env python3
"""
Test rápido de visualización de memoria
"""

import sys
sys.path.append('.')

from Interfaz.interfaz import SimuladorUI, AdaptadorMemoriaUI
from simulador import Simulador
import tkinter as tk

def test_visualizacion():
    """Test simple de la visualización"""
    print("🔧 Probando adaptador de memoria...")
    
    try:
        # Crear simulador
        simulador = Simulador()
        
        # Crear adaptador
        adaptador = AdaptadorMemoriaUI(simulador)
        
        # Probar métodos
        datos_ram = adaptador.obtener_datos_memoria_ram()
        datos_swap = adaptador.obtener_datos_swap()
        porcentaje_ram = adaptador.obtener_porcentaje_uso_ram()
        porcentaje_swap = adaptador.obtener_porcentaje_uso_swap()
        
        print(f"✅ RAM: {len(datos_ram)} bloques, {porcentaje_ram:.1f}% usado")
        print(f"✅ SWAP: {len(datos_swap)} bloques, {porcentaje_swap:.1f}% usado")
        print("✅ Adaptador funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en adaptador: {e}")
        return False

if __name__ == "__main__":
    if test_visualizacion():
        print("\n🚀 Ejecutando interfaz completa...")
        root = tk.Tk()
        app = SimuladorUI(root)
        root.mainloop()
    else:
        print("❌ Test fallido - revisar adaptador")
