# Simulador de Sistema Operativo 🖥️

Un simulador educativo de sistema operativo con interfaz gráfica que demuestra conceptos fundamentales como gestión de procesos, planificación de CPU y gestión de memoria.

## 🎯 Características

### Algoritmos de Planificación
- **SJF (Shortest Job First)**: Planifica procesos por tiempo de ráfaga más corto
- **Round Robin**: Planificación circular con quantum configurable

### Gestión de Memoria  
- **Asignación First-Fit**: Busca el primer bloque libre suficiente
- **Fusión automática**: Previene fragmentación externa
- **Visualización en tiempo real**: Barras gráficas de memoria RAM y SWAP

### Interfaz Gráfica
- **Control interactivo**: Botones para iniciar, finalizar y agregar procesos
- **Visualización de memoria**: Barras de colores por proceso
- **Panel de información**: Estado de procesos en tiempo real
- **Configuración de algoritmos**: Selección SJF/RR con quantum

## 🚀 Instalación y Uso

### Dependencias
```bash
pip install pillow
```

### Verificar Dependencias
```bash
python verificar_dependencias.py
```

### Ejecutar Interfaz Gráfica
```bash
python main_interfaz.py
```

### Ejecutar Simulación por Consola
```bash
python main.py
```

## 🎮 Controles de la Interfaz

1. **Seleccionar Algoritmo**: Elige entre SJF o Round Robin
2. **Configurar Quantum**: Solo para Round Robin (valor por defecto: 2)
3. **Iniciar**: Comienza la simulación con los procesos cargados
4. **Agregar Proceso**: Añade un proceso aleatorio durante la ejecución
5. **Finalizar**: Detiene la simulación actual

## 📊 Visualización

### Barra de Memoria RAM
- **Bloques grises**: Memoria libre
- **Bloques de colores**: Memoria ocupada por procesos
- **Porcentaje**: Uso actual de memoria

### Panel de Información
- **Tiempo global**: Reloj del sistema
- **Procesos nuevos**: En cola de entrada
- **Procesos listos**: Esperando CPU
- **Procesos en CPU**: Ejecutándose por núcleo
- **Procesos terminados**: Completados recientemente

## 🏗️ Arquitectura del Sistema

### Clases Principales
- **`Proceso`**: Encapsula información de procesos individuales
- **`CPU`**: Simula núcleos de procesador multi-core
- **`Memoria`**: Gestiona asignación y liberación de memoria
- **`Planificador`**: Implementa algoritmos de planificación
- **`Simulador`**: Coordinador principal del sistema
- **`BloqueMemoria`**: Representa segmentos de memoria

### Flujo de Ejecución
1. **Creación**: Los procesos se crean y van a cola de nuevos
2. **Asignación**: Se asigna memoria usando First-Fit
3. **Planificación**: El planificador selecciona procesos según algoritmo
4. **Ejecución**: Los procesos se ejecutan en núcleos de CPU
5. **Finalización**: Se libera memoria y se registran estadísticas

## 🧪 Ejemplos de Uso

### Simulación SJF
```python
simulador = Simulador(num_nucleos=2)
simulador.configurar_algoritmo("SJF")
proceso = Proceso(1, 0, 5, 200*1024*1024)  # 200MB
simulador.agregar_proceso(proceso)
```

### Simulación Round Robin  
```python
simulador = Simulador(num_nucleos=2)
simulador.configurar_algoritmo("RR")
simulador.set_quantum(3)
```

## 📁 Estructura del Proyecto

```
ProyectoSO3repo/
├── proceso.py              # Clase Proceso
├── cpu.py                  # Simulación de CPU
├── memoria.py              # Gestión de memoria
├── bloque_memoria.py       # Bloques de memoria
├── planificador.py         # Algoritmos de planificación  
├── simulador.py            # Controlador principal
├── main.py                 # Ejemplos por consola
├── main_interfaz.py        # Lanzador de interfaz gráfica
├── verificar_dependencias.py # Verificador de dependencias
├── Interfaz/
│   ├── interfaz.py         # Interfaz gráfica principal
│   └── boton_ayuda.png     # Recursos gráficos
└── test_*.py               # Archivos de pruebas
```

## 🎓 Conceptos Demostrados

- **Estados de procesos**: Nuevo, Listo, Ejecutando, Terminado
- **Planificación de CPU**: SJF y Round Robin
- **Gestión de memoria**: Asignación, liberación y fragmentación  
- **Métricas de rendimiento**: Tiempo de espera, respuesta y retorno
- **Concurrencia**: Simulación de múltiples núcleos de CPU

## 🐛 Solución de Problemas

### Error de PIL/Pillow
```bash
pip install --upgrade pillow
```

### Error de tkinter (Linux)
```bash
sudo apt-get install python3-tk
```

### Módulos no encontrados
Asegúrate de ejecutar desde el directorio raíz del proyecto.

---

**Desarrollado para fines educativos** 📚
Simulador de Sistema Operativo v1.0
