#!/usr/bin/env python3
"""
Script de configuración para verificar dependencias del simulador
"""

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    dependencias_faltantes = []
    
    # Verificar tkinter (viene con Python por defecto)
    try:
        import tkinter
        print("✅ tkinter: Disponible")
    except ImportError:
        print("❌ tkinter: No disponible")
        dependencias_faltantes.append("tkinter")
    
    # Verificar PIL/Pillow
    try:
        from PIL import Image, ImageOps, ImageTk
        print("✅ PIL (Pillow): Disponible")
    except ImportError:
        print("❌ PIL (Pillow): No disponible")
        dependencias_faltantes.append("pillow")
    
    # Verificar módulos del simulador
    try:
        from proceso import Proceso
        from simulador import Simulador
        from memoria import Memoria
        from cpu import CPU
        from planificador import Planificador
        print("✅ Módulos del simulador: Disponibles")
    except ImportError as e:
        print(f"❌ Módulos del simulador: Error - {e}")
        dependencias_faltantes.append("módulos del simulador")
    
    return dependencias_faltantes

def instalar_dependencias():
    """Proporciona instrucciones para instalar dependencias faltantes"""
    print("\n📦 Para instalar las dependencias faltantes:")
    print("   pip install pillow")
    print("\n💡 tkinter viene incluido con Python por defecto")
    print("💡 Los módulos del simulador deben estar en el mismo directorio")

def main():
    """Función principal de verificación"""
    print("🔍 Verificando dependencias del simulador...")
    print("=" * 50)
    
    dependencias_faltantes = verificar_dependencias()
    
    print("=" * 50)
    
    if not dependencias_faltantes:
        print("🎉 Todas las dependencias están disponibles!")
        print("🚀 Puedes ejecutar la interfaz con: python main_interfaz.py")
    else:
        print(f"⚠️  Faltan {len(dependencias_faltantes)} dependencias:")
        for dep in dependencias_faltantes:
            print(f"   • {dep}")
        instalar_dependencias()

if __name__ == "__main__":
    main()
