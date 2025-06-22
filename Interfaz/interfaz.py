import random
import tkinter as tk
from tkinter import font, messagebox
import sys
import os
from tkinter import ttk

# Agregar el directorio padre al path para importar las clases del simulador
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageOps, ImageTk
from simulador import Simulador
from proceso import Proceso

# =========================================================


# --- CLASE DE PRUEBA PARA EL BACKEND DE MEMORIA (COMENTADA PARA USAR EL SIMULADOR REAL) ---
class GestionMemoria_Old:
    def __init__(self, ram_mb=2048, swap_mb=4096, block_size_mb=64):
        num_bloques_ram = ram_mb // block_size_mb
        num_bloques_swap = swap_mb // block_size_mb
        self.ram = self._inicializar_memoria(num_bloques_ram)
        self.swap = self._inicializar_memoria(num_bloques_swap)
        self.procesos_colores = {}
        self._colores_disponibles = [
            "#FF5733",
            "#33FF57",
            "#3357FF",
            "#FF33A1",
            "#A133FF",
            "#33FFA1",
            "#FFC300",
            "#DAF7A6",
        ]

    def _inicializar_memoria(self, num_bloques):
        return [{"estado": "libre", "proceso_id": None} for _ in range(num_bloques)]

    def registrar_nuevo_proceso(self, proceso_id):
        if proceso_id not in self.procesos_colores:
            color = random.choice(self._colores_disponibles)
            self.procesos_colores[proceso_id] = {"color": color}

    def asignar_memoria_a_proceso(self, proceso_id, memoria_requerida_mb):
        bloques_necesarios = (memoria_requerida_mb + 63) // 64
        for i in range(len(self.ram) - bloques_necesarios + 1):
            if all(
                self.ram[j]["estado"] == "libre"
                for j in range(i, i + bloques_necesarios)
            ):
                for j in range(i, i + bloques_necesarios):
                    self.ram[j]["estado"] = "ocupado"
                    self.ram[j]["proceso_id"] = proceso_id
                return True
        return False

    def liberar_memoria_de_proceso(self, proceso_id):
        for bloque in self.ram:
            if bloque["proceso_id"] == proceso_id:
                bloque["estado"] = "libre"
                bloque["proceso_id"] = None
        for bloque in self.swap:
            if bloque["proceso_id"] == proceso_id:
                bloque["estado"] = "libre"
                bloque["proceso_id"] = None


# =========================================================

# --- ADAPTADOR PARA SINCRONIZAR CON EL SIMULADOR REAL ---
class AdaptadorMemoriaUI:
    """
    Clase que adapta los datos del simulador real para la interfaz gráfica
    """
    def __init__(self, simulador):
        self.simulador = simulador
        self.procesos_colores = {}
        self._colores_disponibles = [
            "#FF5733", "#33FF57", "#3357FF", "#FF33A1",
            "#A133FF", "#33FFA1", "#FFC300", "#DAF7A6",
            "#FF8C00", "#8A2BE2", "#20B2AA", "#DC143C"
        ]
        self.block_size_mb = 64  # Tamaño de bloque para visualización
        
    def _asignar_color_proceso(self, pid):
        """Asigna un color único a cada proceso"""
        if pid not in self.procesos_colores:
            color = random.choice(self._colores_disponibles)
            self.procesos_colores[pid] = {"color": color}
            
    def obtener_datos_memoria_ram(self):
        """Convierte los datos de memoria del simulador a formato para la UI"""
        memoria = self.simulador.memoria
        total_mb = memoria.tamano_total // (1024 * 1024)
        num_bloques_ui = total_mb // self.block_size_mb
        
        # Crear array de bloques para la UI
        bloques_ui = [{"estado": "libre", "proceso_id": None} for _ in range(num_bloques_ui)]
        
        # Mapear bloques ocupados del simulador a bloques UI
        for bloque in memoria.bloques_ocupados:
            inicio_mb = bloque.inicio // (1024 * 1024)
            tamano_mb = bloque.tamano // (1024 * 1024)
            
            inicio_bloque_ui = inicio_mb // self.block_size_mb
            fin_bloque_ui = (inicio_mb + tamano_mb) // self.block_size_mb
            
            # Asegurar que no excedamos el límite
            fin_bloque_ui = min(fin_bloque_ui, num_bloques_ui)
            
            # Marcar bloques como ocupados
            for i in range(inicio_bloque_ui, fin_bloque_ui):
                if i < len(bloques_ui):
                    bloques_ui[i]["estado"] = "ocupado"
                    bloques_ui[i]["proceso_id"] = f"P{bloque.pid_proceso}"
                    self._asignar_color_proceso(f"P{bloque.pid_proceso}")
                    
        return bloques_ui
    
    def obtener_datos_swap(self):
        """Implementar manejo real de SWAP"""
        if hasattr(self.simulador, 'swap'):
            # Lógica similar a obtener_datos_memoria_ram
            pass
        else:
            swap_mb = 4096  # Tamaño de SWAP en MB 4GB
            num_bloques_swap = swap_mb // self.block_size_mb
            return [{"estado": "libre", "proceso_id": None} for _ in range(num_bloques_swap)]
    
    def obtener_porcentaje_uso_ram(self):
        """Calcula el porcentaje de uso de RAM"""
        uso = self.simulador.memoria.obtener_uso_memoria()
        return uso['porcentaje_uso']
    
    def obtener_porcentaje_uso_swap(self):
        """Retorna 0% para SWAP por ahora"""
        return 0.0


# =========================================================


class SimuladorUI:
    """
    Clase que encapsula la interfaz gráfica del simulador de procesos.
    """

    def __init__(self, master):
        """
        Constructor de la clase. Inicializa la ventana principal y sus componentes.
        :param master: La ventana raíz de Tkinter (tk.Tk()).
        """
        self.master = master        # --- Configuración de la Ventana Principal ---
        self.master.title("Simulador de Ejecución de Procesos")
        self.master.geometry("1280x720")
        self.master.configure(bg="black")
        self.master.resizable(False, False)

        # --- Inicializar Simulador Real ---
        self.simulador = Simulador(num_nucleos=2)
        self.adaptador_memoria = AdaptadorMemoriaUI(self.simulador)
        
        # Estado de la simulación
        self.simulacion_iniciada = False
        self.procesos_ejemplo = []        # --- Inicializar Layout ---
        self._crear_layout()

        self._crear_widgets()

        # --- TEST: Crear algunos procesos de ejemplo ---
        self._crear_procesos_ejemplo()

        # --- Actualizar UI después de un breve retraso ---
        self.master.after(100, self._actualizar_ui_memoria)

    def iniciar(self):
        """
        Método para iniciar el bucle principal de la aplicación.
        """
        self.master.mainloop()    # --- NUEVOS MÉTODOS PARA DIBUJAR LA MEMORIA ---
    def _dibujar_barra_memoria(self, canvas, memoria_data, procesos_colores):
        canvas.delete("all")
        ancho_canvas = canvas.winfo_width()
        alto_canvas = canvas.winfo_height()
        num_bloques = len(memoria_data)
        if num_bloques == 0:
            return

        ancho_bloque = ancho_canvas / num_bloques

        for i, bloque in enumerate(memoria_data):
            x0 = i * ancho_bloque
            x1 = (i + 1) * ancho_bloque
            y0 = 0
            y1 = alto_canvas

            color = "#424242"  # Color por defecto para bloques libres
            outline_color = "#555555"  # Color del borde del bloque

            if bloque["estado"] == "ocupado":
                proceso_id = bloque["proceso_id"]
                if proceso_id in procesos_colores:
                    color = procesos_colores[proceso_id]["color"]
                else:
                    color = "red"  # Color de error si el proceso no está registrado

            canvas.create_rectangle(
                x0, y0, x1, y1, fill=color, outline=outline_color, width=2
            )

    def _actualizar_ui_memoria(self):
        self.canvas_ram.config(width=self.intermedio_1_2.winfo_width())
        self.canvas_swap.config(width=self.intermedio_2_2.winfo_width())
        # Esta función será el punto central para refrescar las barras usando el simulador real
        datos_ram = self.adaptador_memoria.obtener_datos_memoria_ram()
        datos_swap = self.adaptador_memoria.obtener_datos_swap()
        
        self._dibujar_barra_memoria(
            self.canvas_ram,
            datos_ram,
            self.adaptador_memoria.procesos_colores,
        )
        self._dibujar_barra_memoria(
            self.canvas_swap,
            datos_swap,
            self.adaptador_memoria.procesos_colores,
        )        # Actualizar porcentajes reales
        porcentaje_ram = self.adaptador_memoria.obtener_porcentaje_uso_ram()
        porcentaje_swap = self.adaptador_memoria.obtener_porcentaje_uso_swap()
        
        self.label_ram_porcentaje.config(text=f"{porcentaje_ram:.1f} %")
        self.label_swap_porcentaje.config(text=f"{porcentaje_swap:.1f} %")
        
        
    def _actualizar_tabla_procesos(self):
        # Limpiar tabla existente
        for item in self.tabla_procesos.get_children():
            self.tabla_procesos.delete(item)
        
        # Obtener todos los procesos del simulador
        todos_procesos = self.simulador.todos_los_procesos()
        
        # Insertar procesos en la tabla
        for proceso in todos_procesos:
            # Asegurar que el proceso tenga un nombre
            nombre_proceso = getattr(proceso, 'nombre', f'Proceso {proceso.pid}')
            
            # Convertir memoria a MB
            memoria_mb = proceso.tamano_memoria // (1024 * 1024)
            
            # Insertar en la tabla
            self.tabla_procesos.insert("", "end", values=(
                proceso.pid,
                nombre_proceso,
                proceso.estado.capitalize(),  # Mostrar con primera letra mayúscula
                proceso.duracion,
                memoria_mb
            ))


    def _crear_layout(self):
        """
        Crea y posiciona los 3 frames principales que dividen la ventana.
        Usamos el gestor de geometría 'grid' con pesos para control proporcional.
        """
        # --- 1. Configurar el grid del contenedor principal (la ventana) ---
        # Solo tenemos una columna, la hacemos expandible.
        self.master.grid_columnconfigure(0, weight=1)

        # Configuramos el 'peso' de cada fila para que ocupe un espacio proporcional.
        # La suma total de pesos es 100 (10 + 20 + 70).
        self.master.grid_rowconfigure(0, weight=5)  # Fila 0 obtiene  5/100 del espacio
        self.master.grid_rowconfigure(1, weight=25)  # Fila 1 obtiene 25/100 del espacio
        self.master.grid_rowconfigure(2, weight=70)  # Fila 2 obtiene 70/100 del espacio

        # --- 2. Crear y posicionar los frames en el grid ---
        # --- Fila 1 (Superior) ---
        self.frame_superior = tk.Frame(self.master, bg="#212121")
        self.frame_superior.grid(row=0, column=0, sticky="nsew")
        self.frame_superior.grid_propagate(False)

        # --- Fila 2 (Intermedia) ---
        self.frame_intermedio = tk.Frame(self.master, bg="#323232")
        self.frame_intermedio.grid(row=1, column=0, sticky="nsew")
        self.frame_intermedio.grid_propagate(False)

        # --- Fila 3 (Inferior) ---
        self.frame_inferior = tk.Frame(self.master, bg="#424242")
        self.frame_inferior.grid(row=2, column=0, sticky="nsew")
        self.frame_inferior.grid_propagate(False)

        # --- Subdivisión del Frame Intermedio ---
        self.frame_intermedio.grid_columnconfigure(0, weight=1)
        self.frame_intermedio.grid_rowconfigure(0, weight=1)  # Fila para RAM
        self.frame_intermedio.grid_rowconfigure(1, weight=1)  # Fila para SWAP

        # Contenedores para RAM y SWAP
        self.intermedio_1 = tk.Frame(self.frame_intermedio, bg="#323232")
        self.intermedio_1.grid(row=0, column=0, sticky="nsew", pady=(5, 2))
        self.intermedio_1.grid_propagate(False)

        self.intermedio_2 = tk.Frame(self.frame_intermedio, bg="#323232")
        self.intermedio_2.grid(row=1, column=0, sticky="nsew", pady=(2, 5))
        self.intermedio_1.grid_propagate(False)

        # Dividir intermedio_1 (RAM) en 20/80
        self.intermedio_1.grid_rowconfigure(0, weight=1)
        self.intermedio_1.grid_columnconfigure(0, weight=20)
        self.intermedio_1.grid_columnconfigure(1, weight=80)
        self.intermedio_1_1 = tk.Frame(
            self.intermedio_1, bg="#323232"
        )  # Contenedor para Label RAM
        self.intermedio_1_1.grid(row=0, column=0, sticky="nsew", padx=(10, 5))
        self.intermedio_1_1.grid_propagate(False)
        self.intermedio_1_2 = tk.Frame(
            self.intermedio_1, bg="#323232"
        )  # Contenedor para Canvas RAM
        self.intermedio_1_2.grid(row=0, column=1, sticky="nsew", padx=(5, 10))
        self.intermedio_1_2.grid_propagate(False)

        # Dividir intermedio_2 (SWAP) en 20/80
        self.intermedio_2.grid_rowconfigure(0, weight=1)
        self.intermedio_2.grid_columnconfigure(0, weight=20)
        self.intermedio_2.grid_columnconfigure(1, weight=80)
        self.intermedio_2_1 = tk.Frame(
            self.intermedio_2, bg="#323232"
        )  # Contenedor para Label SWAP
        self.intermedio_2_1.grid(row=0, column=0, sticky="nsew", padx=(10, 5))
        self.intermedio_2_1.grid_propagate(False)
        self.intermedio_2_2 = tk.Frame(
            self.intermedio_2, bg="#323232"
        )  # Contenedor para Canvas SWAP
        self.intermedio_2_2.grid(row=0, column=1, sticky="nsew", padx=(5, 10))
        self.intermedio_2_2.grid_propagate(False)

        # --- 3. Subdividir el frame inferior en dos columnas (40% y 60%) ---
        # Configurar el grid INTERNO de self.frame_inferior
        self.frame_inferior.grid_rowconfigure(0, weight=1)
        self.frame_inferior.grid_columnconfigure(
            0, weight=60
        )  # Columna 0 obtiene 40/100 del espacio
        self.frame_inferior.grid_columnconfigure(
            1, weight=40
        )  # Columna 1 obtiene 60/100 del espacio

        # Crear los frames para las columnas
        self.frame_inf_izquierdo = tk.Frame(
            self.frame_inferior, bg="#535353"
        )  # Un gris para la columna izquierda
        self.frame_inf_izquierdo.grid(row=0, column=0, sticky="nsew")
        self.frame_inf_izquierdo.grid_propagate(False)

        self.frame_inf_derecho = tk.Frame(
            self.frame_inferior, bg="#616161"
        )  # Un gris un poco más claro para la derecha
        self.frame_inf_derecho.grid(row=0, column=1, sticky="nsew")
        self.frame_inf_derecho.grid_propagate(False)

        # --- 4. Subdividir el frame_inf_izquierdo (3.1) en tres filas (3.1.1, 3.1.2, 3.1.3) ---
        self.frame_inf_izquierdo.grid_columnconfigure(0, weight=1)
        # Damos a las 3 filas el mismo peso para que se dividan equitativamente
        self.frame_inf_izquierdo.grid_rowconfigure(0, weight=1)  # Fila 3.1.1
        self.frame_inf_izquierdo.grid_rowconfigure(1, weight=1)  # Fila 3.1.2
        self.frame_inf_izquierdo.grid_rowconfigure(2, weight=1)  # Fila 3.1.3

        # Crear los frames para las nuevas filas
        self.frame_3_1_1 = tk.Frame(self.frame_inf_izquierdo, bg="#4a4a4a")
        self.frame_3_1_1.grid(row=0, column=0, sticky="nsew")
        self.frame_3_1_1.grid_propagate(False)

        self.frame_3_1_2 = tk.Frame(self.frame_inf_izquierdo, bg="#545454")
        self.frame_3_1_2.grid(row=1, column=0, sticky="nsew")
        self.frame_3_1_2.grid_propagate(False)

        self.frame_3_1_3 = tk.Frame(self.frame_inf_izquierdo, bg="#5e5e5e")
        self.frame_3_1_3.grid(row=2, column=0, sticky="nsew")
        self.frame_3_1_3.grid_propagate(False)

        # --- 5. Subdividir el frame_3_1_2 en dos columnas (3.1.2.1 y 3.1.2.2) ---
        self.frame_3_1_2.grid_rowconfigure(0, weight=1)
        self.frame_3_1_2.grid_columnconfigure(0, weight=1)  # Columna 3.1.2.1
        self.frame_3_1_2.grid_columnconfigure(1, weight=1)  # Columna 3.1.2.2

        self.frame_3_1_2_1 = tk.Frame(self.frame_3_1_2, bg="#6f6f6f")
        self.frame_3_1_2_1.grid(row=0, column=0, sticky="nsew")
        self.frame_3_1_2_1.grid_propagate(False)

        self.frame_3_1_2_2 = tk.Frame(self.frame_3_1_2, bg="#7a7a7a")
        self.frame_3_1_2_2.grid(row=0, column=1, sticky="nsew")
        self.frame_3_1_2_2.grid_propagate(False)

    def _actualizar_estado_quantum(self):
        """
        Revisa el valor del radio button y habilita o deshabilita
        la entrada de quantum según corresponda.
        """
        if self.algoritmo_seleccionado.get() == "RR":
            self.entrada_quantum.config(state=tk.NORMAL)
        else:
            self.entrada_quantum.config(state=tk.DISABLED)

    def _validar_solo_numeros(self, nuevo_valor):
        """
        Valida que el valor ingresado en un Entry sea numérico.
        Permite que el campo esté vacío.
        """
        if nuevo_valor == "":
            return True
        return nuevo_valor.isdigit()

    def _crear_widgets(self):
        """
        Crea todos los widgets (botones, etiquetas, etc.) dentro de los frames.
        """
        # --- Fuentes ---
        font_botones = font.Font(family="Helvetica", size=12)
        font_botones_grandes = font.Font(family="Helvetica", size=15)
        font_form_opt = font.Font(family="Helvetica", size=15)
        font_form_cuantum = font.Font(family="Helvetica", size=12)
        font_memoria = font.Font(family="Helvetica", size=12, weight="bold")        # --- Widgets en Frame Superior (Fila 1) ---
        # Obtener la ruta correcta de la imagen
        ruta_imagen = os.path.join(os.path.dirname(__file__), "boton_ayuda.png")
        imagen_ayuda_original = Image.open(ruta_imagen)
        imagen_rgba = imagen_ayuda_original.convert("RGBA")

        # 1. Separar los canales de color (RGB) de la transparencia (A)
        rgb_image = Image.new("RGB", imagen_rgba.size)
        rgb_image.paste(imagen_rgba)

        # 2. Invertir SOLAMENTE los canales de color (RGB)
        inverted_rgb = ImageOps.invert(rgb_image)

        # 3. Extraer el canal de transparencia original
        alpha_channel = imagen_rgba.split()[3]

        # 4. Añadir la transparencia original a la imagen de colores invertidos
        imagen_negativo = inverted_rgb
        imagen_negativo.putalpha(alpha_channel)

        # Redimensionamos la imagen final ya procesada
        imagen_ayuda_redimensionada = imagen_negativo.resize((32, 32), Image.LANCZOS)
        self.imagen_ayuda_tk = ImageTk.PhotoImage(imagen_ayuda_redimensionada)

        self.boton_ayuda = tk.Button(
            self.frame_superior,
            image=self.imagen_ayuda_tk,
            bg="#212121",
            activebackground="#212121",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
        )
        self.boton_ayuda.image = self.imagen_ayuda_tk
        self.boton_ayuda.pack(side="left", padx=10, pady=10)

        # --- Widgets en Frame Intermedio (Fila 2) ---
        # Widgets para RAM
        label_ram = tk.Label(
            self.intermedio_1_1, text="RAM", fg="white", bg="#323232", font=font_memoria
        )
        label_ram.pack(expand=True)

        self.canvas_ram = tk.Canvas(
            self.intermedio_1_2, bg="black", highlightthickness=0
        )
        self.label_ram_porcentaje = tk.Label(
            self.intermedio_1_2, text="0 %", fg="white", bg="#323232", font=font_memoria
        )

        # Posicionamos el canvas y el porcentaje dentro del frame de 80%
        self.intermedio_1_2.grid_columnconfigure(0, weight=10)  # Canvas
        self.intermedio_1_2.grid_columnconfigure(1, weight=1)  # %
        self.intermedio_1_2.grid_rowconfigure(0, weight=1)
        self.canvas_ram.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.label_ram_porcentaje.grid(row=0, column=1, sticky="e")

        # Widgets para SWAP
        label_swap = tk.Label(
            self.intermedio_2_1,
            text="SWAP",
            fg="white",
            bg="#323232",
            font=font_memoria,
        )
        label_swap.pack(expand=True)

        self.canvas_swap = tk.Canvas(
            self.intermedio_2_2, bg="black", highlightthickness=0
        )
        self.label_swap_porcentaje = tk.Label(
            self.intermedio_2_2, text="0 %", fg="white", bg="#323232", font=font_memoria
        )

        # Posicionamos el canvas y el porcentaje dentro del frame de 80%
        self.intermedio_2_2.grid_columnconfigure(0, weight=10)  # Canvas
        self.intermedio_2_2.grid_columnconfigure(1, weight=1)  # %
        self.intermedio_2_2.grid_rowconfigure(0, weight=1)
        self.canvas_swap.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.label_swap_porcentaje.grid(row=0, column=1, sticky="e")

        # --- Widgets en Frame 3.1.1 (Formulario Algoritmo) ---

        # Creamos un frame contenedor para centrar el formulario
        form_container = tk.Frame(self.frame_3_1_1, bg="#4a4a4a")

        vcmd = (self.master.register(self._validar_solo_numeros), "%P")

        # Variable para controlar qué radio button está seleccionado
        self.algoritmo_seleccionado = tk.StringVar(value="SJF")  # Valor inicial SJF

        # Estilo para los radio buttons y labels
        estilo_form_opt = {
            "bg": "#4a4a4a",
            "fg": "white",
            "selectcolor": "#323232",
            "activebackground": "#4a4a4a",
            "activeforeground": "white",
            "font": font_form_opt,
            "bd": 0,
            "highlightthickness": 0,
        }

        estilo_form_cuantum = {
            "bg": "#4a4a4a",
            "fg": "white",
            "selectcolor": "#323232",
            "activebackground": "#4a4a4a",
            "activeforeground": "white",
            "font": font_form_cuantum,
            "bd": 0,
            "highlightthickness": 0,
        }

        # Radio button para SJF
        self.radio_sjf = tk.Radiobutton(
            form_container,
            text="SJF",
            variable=self.algoritmo_seleccionado,
            value="SJF",
            command=self._actualizar_estado_quantum,
            **estilo_form_opt
        )
        self.radio_sjf.pack(side="left", padx=20, pady=10)

        # Radio button para Round Robin
        self.radio_rr = tk.Radiobutton(
            form_container,
            text="Round Robin",
            variable=self.algoritmo_seleccionado,
            value="RR",
            command=self._actualizar_estado_quantum,
            **estilo_form_opt
        )
        self.radio_rr.pack(side="left", padx=(0, 10), pady=10)

        # Etiqueta para Quantum
        self.label_quantum = tk.Label(
            form_container,
            text="quantum:",
            bg=estilo_form_cuantum["bg"],
            fg=estilo_form_cuantum["fg"],
            font=font_form_cuantum,
        )
        self.label_quantum.pack(side="left", pady=10)

        # Entrada de texto para el valor del Quantum
        self.entrada_quantum = tk.Entry(
            form_container,
            width=4,
            font=font_form_cuantum,
            bd=0,
            disabledbackground="#5e5e5e",
            fg="white",
            bg="#323232",
            validate="key",  # Validar en cada pulsación de tecla
            validatecommand=vcmd,
        )
        self.entrada_quantum.pack(side="left", pady=10, ipady=2)

        # 3. Centramos el frame contenedor dentro del frame principal (3.1.1)
        form_container.pack(expand=True)

        # Llamamos a la función una vez para establecer el estado inicial correcto
        self._actualizar_estado_quantum()        # --- Widgets en Frame 3.1.2.1 (Botón Finalizar) ---
        self.boton_finalizar = tk.Button(
            self.frame_3_1_2_1,
            text="Finalizar",
            bg="#a62626",
            fg="white",
            activebackground="#c44e4e",
            font=font_botones,
            bd=0,
            cursor="hand2",
            command=self._finalizar_simulacion
        )
        # Usamos place para un tamaño proporcional del 80% y márgenes del 10%
        self.boton_finalizar.place(relx=0.15, rely=0.15, relwidth=0.7, relheight=0.7)

        # --- Widgets en Frame 3.1.2.2 (Botón Iniciar) ---
        self.boton_iniciar = tk.Button(
            self.frame_3_1_2_2,
            text="Iniciar",
            bg="#348a3d",
            fg="white",
            activebackground="#50a35a",
            font=font_botones,
            bd=0,
            cursor="hand2",
            command=self._iniciar_simulacion
        )
        self.frame_3_1_2_2.grid(row=0, column=1, sticky="nsew")
        self.boton_iniciar.place(relx=0.15, rely=0.15, relwidth=0.7, relheight=0.7)

        # --- Widgets en Frame 3.1.3 (Botón Añadir Proceso) ---
        self.boton_agregar = tk.Button(
            self.frame_3_1_3,
            text="Añadir Proceso",
            bg="#424242",
            fg="white",
            activebackground="#616161",
            font=font_botones_grandes,
            bd=0,
            cursor="hand2",
            command=self._abrir_ventana_agregar_proceso
        )
        # Para este botón más grande, podemos usar una proporción mayor, ej: 90%        self.boton_agregar.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        self.boton_agregar.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        
        # Configurar estilo para la tabla
        style = ttk.Style()
        
        #Configurar colores
        bg_color = "#616161"  # Color de fondo del frame
        header_color = "#535353"  # Color de encabezados
        cell_color = "#616161"  # Color de celdas (mismo que fondo)
        text_color = "white"  # Color de texto
        
        # Cambiar estilo de los encabezados
        style = ttk.Style()
        style.configure("Treeview.Heading", 
                    background=header_color, 
                    foreground="black",
                    font=('Helvetica', 10, 'bold'))
        
        # Cambiar estilo de las filas
        style.configure("Treeview", 
                    background=bg_color,
                    foreground=text_color,
                    fieldbackground=bg_color,
                    font=('Helvetica', 10))
        
        # Cambiar color de selección
        style.map('Treeview', 
                background=[('selected', '#424242')])
        
        
        
        # Crear la tabla con el estilo personalizado
        self.tabla_procesos = ttk.Treeview(
            self.frame_inf_derecho,
            columns=("PID", "Nombre", "Estado", "Duración", "Memoria"),
            show="headings"
        )
        
        # Configurar encabezados
        self.tabla_procesos.heading("PID", text="PID")
        self.tabla_procesos.heading("Nombre", text="Nombre")
        self.tabla_procesos.heading("Estado", text="Estado")
        self.tabla_procesos.heading("Duración", text="Duración")
        self.tabla_procesos.heading("Memoria", text="Memoria (MB)")
        
        # Configurar columnas
        self.tabla_procesos.column("PID", width=50, anchor="center")
        self.tabla_procesos.column("Nombre", width=120, anchor="center")
        self.tabla_procesos.column("Estado", width=80, anchor="center")
        self.tabla_procesos.column("Duración", width=70, anchor="center")
        self.tabla_procesos.column("Memoria", width=90, anchor="center")
        
        # Configurar el frame contenedor para que tenga el mismo color
        self.frame_inf_derecho = tk.Frame(
            self.frame_inferior, 
            bg="#616161"  # Asegurar que el frame tenga el mismo color
        )
        
        # Añadir scrollbar con estilo personalizado
        scrollbar = ttk.Scrollbar(
            self.frame_inf_derecho, 
            orient="vertical", 
            command=self.tabla_procesos.yview
        )
        self.tabla_procesos.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar con el mismo color de fondo
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.tabla_procesos.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Asegurar que el scrollbar tenga el mismo fondo
        style.configure("Vertical.TScrollbar", background=header_color)


    def _finalizar_simulacion(self):
        """Finaliza la simulación actual"""
        if self.simulacion_iniciada:
            self.simulacion_iniciada = False
            self.simulador.detener_simulacion()
            self.boton_iniciar.config(state=tk.NORMAL)
            self.boton_finalizar.config(state=tk.DISABLED)
            print("🛑 Simulación finalizada por el usuario")
            
    # En tu método para agregar procesos aleatorios
    def _agregar_proceso_aleatorio(self):
        pid = len(self.simulador.procesos_nuevos) + len(self.simulador.procesos_terminados) + 1
        nombres = ["Navegador", "Editor", "Reproductor", "Juego", "Antivirus", "Calculadora"]
        nombre = random.choice(nombres)
        
        nuevo_proceso = Proceso(
            pid=pid,
            nombre=nombre,
            duracion=random.randint(3, 10),
            tamano_memoria=random.randint(100, 400) * 1024 * 1024
        )
        self.simulador.agregar_proceso(nuevo_proceso)
        self._actualizar_tabla_procesos()

        
        print(f"➕ Proceso P{pid} agregado - Memoria: {nuevo_proceso.tamano_memoria//(1024*1024)}MB, Duración: {nuevo_proceso.duracion}")
        
    def _abrir_ventana_agregar_proceso(self):
        ventana = tk.Toplevel(self.master)
        ventana.title("Añadir Proceso")
        ventana.configure(bg="#2c2c2c")
        ventana.geometry("350x350")
        ventana.resizable(False, False)

        # Variables para los campos
        var_nombre = tk.StringVar()
        var_llegada = tk.StringVar()
        var_duracion = tk.StringVar()
        var_memoria = tk.StringVar()

        # Función para generar valores aleatorios
        def generar_aleatorio():
            nombres = ["Navegador", "Editor", "Reproductor", "Juego", "Antivirus", "Calculadora"]
            nombre = random.choice(nombres)
            llegada = random.randint(0, 10)
            duracion = random.randint(3, 10)
            memoria = random.randint(100, 400)
            
            var_nombre.set(nombre)
            var_llegada.set(str(llegada))
            var_duracion.set(str(duracion))
            var_memoria.set(str(memoria))

        # Función de validación
        def validar_numero(P):
            return P.isdigit() or P == ""

        vcmd = (ventana.register(validar_numero), '%P')

        # Marco para el formulario
        form_frame = tk.Frame(ventana, bg="#2c2c2c")
        form_frame.pack(pady=10)

        # Campos del formulario
        campos = [
            ("Nombre", var_nombre, "text", ""),
            ("Tiempo de llegada", var_llegada, "number", 0),
            ("Duración (burst)", var_duracion, "number", 1),
            ("Memoria (MB)", var_memoria, "number", 10)
        ]
        
        entries = []
        for i, (label, var, tipo, default) in enumerate(campos):
            tk.Label(form_frame, text=label, fg="white", bg="#2c2c2c").grid(
                row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(form_frame, textvariable=var)
            if tipo == "number":
                entry.config(validate="key", validatecommand=vcmd)
                var.set(str(default))
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entries.append(entry)

        # Botón para generar datos aleatorios
        btn_generar = tk.Button(
            form_frame, 
            text="Generar Aleatorio",
            command=generar_aleatorio,
            bg="#5D6D7E",
            fg="white"
        )
        btn_generar.grid(row=len(campos), column=0, columnspan=2, pady=10, sticky="ew")

        # Función para añadir el proceso
        def agregar():
            try:
                nombre = var_nombre.get() or f"Proceso_{random.randint(100,999)}"
                llegada = max(0, int(var_llegada.get()))
                duracion = max(1, int(var_duracion.get()))
                memoria = max(1, int(var_memoria.get())) * 1024 * 1024  # MB a bytes

                # Crear proceso (el simulador asignará PID)
                proceso = Proceso(
                    nombre=nombre,
                    tiempo_llegada=llegada,
                    duracion=duracion,
                    tamano_memoria=memoria
                )
                
                # Añadir al simulador
                self.simulador.agregar_proceso(proceso)
                
                # Actualizar UI
                self._actualizar_ui_memoria()
                self._actualizar_tabla_procesos()
                ventana.destroy()
                
                print(f"➕ Proceso añadido: {nombre} (Llegada: {llegada}, "
                    f"Duración: {duracion}, Memoria: {memoria//(1024*1024)}MB)")
            except ValueError:
                messagebox.showerror("Error", "Valores inválidos. Verifique los números.")

        # Botones finales
        btn_frame = tk.Frame(ventana, bg="#2c2c2c")
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame, 
            text="Cancelar", 
            command=ventana.destroy,
            width=10,
            bg="#E74C3C",
            fg="white"
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame, 
            text="Añadir", 
            command=agregar,
            width=10,
            bg="#2ECC71",
            fg="white"
        ).pack(side="right", padx=10)

        # Generar valores aleatorios iniciales
        generar_aleatorio()

        # Hacer la ventana modal
        ventana.grab_set()
        ventana.transient(self.master)
        ventana.wait_window(ventana)

        
    def _configurar_algoritmo(self):
        """Configura el algoritmo seleccionado en el simulador"""
        algoritmo = self.algoritmo_seleccionado.get()
        self.simulador.configurar_algoritmo(algoritmo)
        
        if algoritmo == "RR":
            try:
                quantum = int(self.entrada_quantum.get()) if self.entrada_quantum.get() else 2
                self.simulador.set_quantum(quantum)
                print(f"⚙️  Algoritmo configurado: Round Robin (Quantum: {quantum})")
            except ValueError:
                self.simulador.set_quantum(2)  # Valor por defecto
                print("⚙️  Algoritmo configurado: Round Robin (Quantum: 2 por defecto)")
        else:
            print(f"⚙️  Algoritmo configurado: {algoritmo}")

    def _crear_procesos_ejemplo(self):
        """Crea algunos procesos de ejemplo para la demostración"""
        procesos = [
        Proceso(nombre="Navegador", tiempo_llegada=0, duracion=5, tamano_memoria=200*1024*1024),
        Proceso(nombre="Editor", tiempo_llegada=1, duracion=3, tamano_memoria=150*1024*1024),
        Proceso(nombre="Reproductor", tiempo_llegada=2, duracion=8, tamano_memoria=300*1024*1024),
    ]
        
        self.procesos_ejemplo = procesos
        
        # Agregar procesos al simulador pero no ejecutar aún
        for proceso in procesos:
            self.simulador.agregar_proceso(proceso)
            
        # Actualizar la UI para reflejar los procesos agregados
        self._actualizar_tabla_procesos()
            
    def _iniciar_simulacion(self):
        """Inicia la simulación del sistema"""
        if not self.simulacion_iniciada:
            # Configurar algoritmo seleccionado
            self._configurar_algoritmo()
            
            # Cambiar estado de botones
            self.boton_iniciar.config(state=tk.DISABLED)
            self.boton_finalizar.config(state=tk.NORMAL)
            
            # Iniciar simulación
            self.simulacion_iniciada = True
            self.simulador.iniciar_simulacion()
            
            self._actualizar_tabla_procesos()  # Actualizar tabla de procesos
              # Programar el primer paso de simulación
            self.master.after(1000, self._paso_simulacion)
            print("🚀 Simulación iniciada desde la interfaz")
            
    def _paso_simulacion(self):
        """Ejecuta un paso de la simulación"""
        if self.simulacion_iniciada:
            continuar = self.simulador.paso_simulacion()
            
            
            self._actualizar_ui_memoria()
            self._actualizar_tabla_procesos()
            
            # Si la simulación debe continuar, programar el siguiente paso
            if continuar:
                # Usar velocidad configurable en lugar de fija
                velocidad = 1000  # ms, podría ser configurable
                self.master.after(velocidad, self._paso_simulacion)
            else:
                self.simulacion_iniciada = False
                self.mostrar_estadisticas()  # Mostrar estadísticas al finalizar
                print("🏁 Simulación completada")
                
    def mostrar_estadisticas(self):
        """Muestra una ventana con estadísticas al finalizar la simulación"""
        if not self.simulador.procesos_terminados:
            return
        
        ventana = tk.Toplevel(self.master)
        ventana.title("Estadísticas de Simulación")
        ventana.geometry("600x400")
        
        # Calcular métricas
        tiempos_espera = []
        tiempos_respuesta = []
        tiempos_retorno = []
        
        for proceso in self.simulador.procesos_terminados:
            t_espera = proceso.tiempo_finalizacion - proceso.tiempo_llegada - proceso.duracion
            t_retorno = proceso.tiempo_finalizacion - proceso.tiempo_llegada
            t_respuesta = proceso.tiempo_inicio_ejecucion - proceso.tiempo_llegada
            
            
            tiempos_espera.append(t_espera)
            tiempos_respuesta.append(t_respuesta)
            tiempos_retorno.append(t_retorno)
        
        # Crear tabla con ttk.Treeview
        tabla = ttk.Treeview(ventana, columns=("Métrica", "SJF", "RR"), show="headings")
        tabla.heading("Métrica", text="Métrica")
        tabla.heading("SJF", text="SJF")
        tabla.heading("RR", text="Round Robin")
        
        # Agregar datos (aquí deberías tener datos reales de ambas simulaciones)
        datos = [
            ("Tiempo Espera Promedio", sum(tiempos_espera)/len(tiempos_espera), 0),
            ("Tiempo Respuesta Promedio", sum(tiempos_respuesta)/len(tiempos_respuesta), 0),
            ("Tiempo Retorno Promedio", sum(tiempos_retorno)/len(tiempos_retorno), 0)
        ]
        
        for dato in datos:
            tabla.insert("", "end", values=dato)
        
        tabla.pack(fill="both", expand=True, padx=10, pady=10)
    


# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    # 1. Crear la instancia de la ventana raíz
    root = tk.Tk()

    # 2. Crear una instancia de nuestra clase de UI, pasándole la ventana raíz
    app = SimuladorUI(root)

    # 3. Iniciar la aplicación
    app.iniciar()
