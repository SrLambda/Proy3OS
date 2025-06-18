import random
import tkinter as tk
from tkinter import font

from PIL import Image, ImageOps, ImageTk

# =========================================================


# --- CLASE DE PRUEBA PARA EL BACKEND DE MEMORIA ---
class GestionMemoria:
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


class SimuladorUI:
    """
    Clase que encapsula la interfaz gráfica del simulador de procesos.
    """

    def __init__(self, master):
        """
        Constructor de la clase. Inicializa la ventana principal y sus componentes.
        :param master: La ventana raíz de Tkinter (tk.Tk()).
        """
        self.master = master

        # --- Configuración de la Ventana Principal ---
        self.master.title("Simulador de Ejecución de Procesos")
        self.master.geometry("1280x720")
        self.master.configure(bg="black")
        self.master.resizable(False, False)

        # --- Prueba ---
        self.gestor_memoria = GestionMemoria()

        # --- Inicializar Layout ---
        self._crear_layout()

        self._crear_widgets()

        # --- TEST: Realizar una prueba inicial para visualizar ---
        self.gestor_memoria.registrar_nuevo_proceso("P1")
        self.gestor_memoria.asignar_memoria_a_proceso("P1", 300)  # Asigna 5 bloques
        self.gestor_memoria.registrar_nuevo_proceso("P2")
        self.gestor_memoria.asignar_memoria_a_proceso("P2", 500)  # Asigna 8 bloques

        # --- CORRECCIÓN: Llamar a la función de dibujo después de un breve retraso ---
        self.master.after(100, self._actualizar_ui_memoria)

    def iniciar(self):
        """
        Método para iniciar el bucle principal de la aplicación.
        """
        self.master.mainloop()

    # --- NUEVOS MÉTODOS PARA DIBUJAR LA MEMORIA ---
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
        # Esta función será el punto central para refrescar las barras
        self._dibujar_barra_memoria(
            self.canvas_ram,
            self.gestor_memoria.ram,
            self.gestor_memoria.procesos_colores,
        )
        self._dibujar_barra_memoria(
            self.canvas_swap,
            self.gestor_memoria.swap,
            self.gestor_memoria.procesos_colores,
        )

        # Actualizar porcentajes (a implementar)
        self.label_ram_porcentaje.config(text="-- %")
        self.label_swap_porcentaje.config(text="-- %")

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
            0, weight=40
        )  # Columna 0 obtiene 40/100 del espacio
        self.frame_inferior.grid_columnconfigure(
            1, weight=60
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
        font_memoria = font.Font(family="Helvetica", size=12, weight="bold")

        # --- Widgets en Frame Superior (Fila 1) ---
        imagen_ayuda_original = Image.open("boton_ayuda.png")
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
        self._actualizar_estado_quantum()

        # --- Widgets en Frame 3.1.2.1 (Botón Finalizar) ---
        self.boton_finalizar = tk.Button(
            self.frame_3_1_2_1,
            text="Finalizar",
            bg="#a62626",
            fg="white",
            activebackground="#c44e4e",
            font=font_botones,
            bd=0,
            cursor="hand2",
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
        )
        # Para este botón más grande, podemos usar una proporción mayor, ej: 90%
        self.boton_agregar.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)


# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    # 1. Crear la instancia de la ventana raíz
    root = tk.Tk()

    # 2. Crear una instancia de nuestra clase de UI, pasándole la ventana raíz
    app = SimuladorUI(root)

    # 3. Iniciar la aplicación
    app.iniciar()
