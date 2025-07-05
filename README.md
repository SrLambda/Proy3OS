# Simulador de Sistema Operativo

## Descripción
Simulador de Sistema Operativo con gestión avanzada de memoria que incluye algoritmos de reemplazo de páginas, sistema SWAP, interfaz gráfica interactiva y métricas en tiempo real.

## Características Principales
- 🧠 **Algoritmos de Reemplazo**: FIFO, LRU, LFU
- 📊 **Métricas en Tiempo Real**: Page faults, hit ratio, fragmentación
- ⚙️ **Configuración Dinámica**: Ajuste de algoritmos y umbrales SWAP
- 🖥️ **Programas Predefinidos**: Navegador, Editor, Compilador, etc.
- 🎯 **Demostración Visual**: Comparación de rendimiento de algoritmos
- 💾 **Sistema SWAP Avanzado**: Gestión automática de memoria virtual

## Ejecución
```bash
python main.py
```
o
```bash
python ejecutar_simulador.py
```

## Requisitos
- Python 3.7+
- tkinter (incluido en Python estándar)

## Estructura del Proyecto
```
├── main.py                    # Punto de entrada principal
├── simulador.py              # Motor del simulador
├── memoria.py                # Gestión de memoria avanzada
├── algoritmos_reemplazo.py   # Algoritmos FIFO, LRU, LFU
├── programa.py               # Programas predefinidos
├── proceso.py                # Definición de procesos
├── cpu.py                    # Simulación de CPU
├── planificador.py          # Planificador de procesos
├── bloque_memoria.py        # Gestión de bloques
└── Interfaz/
    └── interfaz.py          # Interfaz gráfica
```

## Uso de la Interfaz
1. **Agregar Procesos**: Usa "Añadir Proceso" para crear procesos manuales o seleccionar programas predefinidos
2. **Configurar Algoritmos**: Cambia algoritmos de reemplazo desde "Configuración Avanzada"
3. **Monitorear Métricas**: Observa estadísticas en tiempo real en "Métricas de Memoria Avanzadas"
4. **Demostrar Algoritmos**: Usa "Demo Algoritmos" para comparar rendimiento
5. **Controlar Simulación**: Play/Pause/Reset para controlar la ejecución

## Funcionalidades Avanzadas
- División automática de programas en procesos hijos
- Gestión inteligente de SWAP con umbrales configurables
- Visualización de estado de memoria en tiempo real
- Detección automática de fragmentación
- Corrección automática de inconsistencias de estado
