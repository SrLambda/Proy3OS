import random
import tkinter as tk
from tkinter import font
import sys
import os
from tkinter import ttk
from tkinter import messagebox

import proceso


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageOps, ImageTk
from simulador import Simulador
from proceso import Proceso




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

    def registrar_nuevo_proceso(self, proceso_id, color=None):
        if proceso_id not in self.procesos_colores:
            color = proceso[color]
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
        self.block_size_mb = 64 

    def _asignar_color_proceso(self, pid):
        """Asigna un color único a cada proceso sin repetir"""
        if pid not in self.procesos_colores:
            if not self._colores_disponibles:
                # Si se acaban los colores, se puede generar uno aleatorio
                color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            else:
                color = self._colores_disponibles.pop(0)  # Usar sin repetir
            self.procesos_colores[pid] = {"color": color}

    def obtener_datos_memoria_ram(self):
        """Convierte los datos de memoria del simulador a formato para la UI"""
        memoria = self.simulador.memoria
        
        # Calcular bloques UI basado en el tamaño total
        total_mb = memoria.tamano_total // (1024 * 1024)
        num_bloques_ui = total_mb // self.block_size_mb

        # Crear array de bloques para la UI
        bloques_ui = [{"estado": "libre", "proceso_id": None} for _ in range(num_bloques_ui)]

        # Usar la información de paginación para llenar los bloques
        if hasattr(memoria, 'gestor_paginacion') and memoria.gestor_paginacion:
            paginas_ocupadas = 0
            procesos_activos = {}
            
            # Contar páginas ocupadas por proceso
            for pagina in memoria.gestor_paginacion.paginas_ram:
                if pagina.proceso_pid is not None:
                    paginas_ocupadas += 1
                    pid_str = f"P{pagina.proceso_pid}"
                    if pid_str not in procesos_activos:
                        procesos_activos[pid_str] = 0
                    procesos_activos[pid_str] += 1
            
            # Llenar bloques UI basado en páginas ocupadas
            bloque_idx = 0
            for pid_str, num_paginas in procesos_activos.items():
                self._asignar_color_proceso(pid_str)
                
                # Calcular cuántos bloques UI representa este proceso
                bloques_proceso = (num_paginas * 16) // self.block_size_mb  # 16MB por página
                bloques_proceso = max(1, bloques_proceso)  # Mínimo 1 bloque
                
                for _ in range(min(bloques_proceso, len(bloques_ui) - bloque_idx)):
                    if bloque_idx < len(bloques_ui):
                        bloques_ui[bloque_idx]["estado"] = "ocupado"
                        bloques_ui[bloque_idx]["proceso_id"] = pid_str
                        bloque_idx += 1

        return bloques_ui

    def obtener_datos_swap(self):
        """Convierte los datos de memoria SWAP del simulador a formato para la UI"""
        memoria = self.simulador.memoria
        total_swap_mb = memoria.tamano_swap // (1024 * 1024)
        num_bloques_swap_ui = total_swap_mb // self.block_size_mb

        # Crear array de bloques para la UI
        bloques_swap_ui = [{"estado": "libre", "proceso_id": None} for _ in range(num_bloques_swap_ui)]

        # Usar la información de paginación para SWAP
        if hasattr(memoria, 'gestor_paginacion') and memoria.gestor_paginacion:
            procesos_swap = {}
            
            # Contar páginas en SWAP por proceso
            for pagina in memoria.gestor_paginacion.paginas_swap:
                if pagina.proceso_pid is not None:
                    pid_str = f"P{pagina.proceso_pid}"
                    if pid_str not in procesos_swap:
                        procesos_swap[pid_str] = 0
                    procesos_swap[pid_str] += 1
            
            # Llenar bloques UI basado en páginas en SWAP
            bloque_idx = 0
            for pid_str, num_paginas in procesos_swap.items():
                self._asignar_color_proceso(pid_str)
                
                # Calcular cuántos bloques UI representa este proceso
                bloques_proceso = (num_paginas * 16) // self.block_size_mb  # 16MB por página
                bloques_proceso = max(1, bloques_proceso)  # Mínimo 1 bloque
                
                for _ in range(min(bloques_proceso, len(bloques_swap_ui) - bloque_idx)):
                    if bloque_idx < len(bloques_swap_ui):
                        bloques_swap_ui[bloque_idx]["estado"] = "ocupado"
                        bloques_swap_ui[bloque_idx]["proceso_id"] = pid_str
                        bloque_idx += 1

        return bloques_swap_ui

    def obtener_porcentaje_uso_ram(self):
        """Calcula el porcentaje de uso de RAM"""
        memoria = self.simulador.memoria
        if hasattr(memoria, 'gestor_paginacion') and memoria.gestor_paginacion:
            stats = memoria.gestor_paginacion.obtener_estadisticas_paginacion()
            return stats['uso_ram']
        return 0.0

    def obtener_porcentaje_uso_swap(self):
        """Calcula el porcentaje de uso de SWAP"""
        memoria = self.simulador.memoria
        if hasattr(memoria, 'gestor_paginacion') and memoria.gestor_paginacion:
            stats = memoria.gestor_paginacion.obtener_estadisticas_paginacion()
            return stats['uso_swap']
        return 0.0




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
        self.master.title("Simulador de Ejecución de Procesos")
        self.master.geometry("1280x720")
        self.master.configure(bg="black")
        self.master.resizable(False, False)

     
        self.simulador = Simulador(num_nucleos=2)
        self.adaptador_memoria = AdaptadorMemoriaUI(self.simulador)


        self.simulacion_iniciada = False
        self.procesos_ejemplo = []       
        self._crear_layout()

        self._crear_widgets()

  
        self._crear_procesos_ejemplo()

 
        self.master.after(100, self._actualizar_ui_memoria)

    def iniciar(self):
        """
        Método para iniciar el bucle principal de la aplicación.
        """
        self.master.mainloop()   
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

            color = "#424242"  
            outline_color = "#555555" 

            if bloque["estado"] == "ocupado":
                proceso_id = bloque["proceso_id"]
                if proceso_id in procesos_colores:
                    color = procesos_colores[proceso_id]["color"]
                else:
                    color = "red"  

            canvas.create_rectangle(
                x0, y0, x1, y1, fill=color, outline=outline_color, width=2
            )

    def _actualizar_ui_memoria(self):
        
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
        )      
        porcentaje_ram = self.adaptador_memoria.obtener_porcentaje_uso_ram()
        porcentaje_swap = self.adaptador_memoria.obtener_porcentaje_uso_swap()

        self.label_ram_porcentaje.config(text=f"{porcentaje_ram:.1f} %")
        self.label_swap_porcentaje.config(text=f"{porcentaje_swap:.1f} %")
        
        # Actualizar métricas avanzadas si están disponibles
        self._actualizar_metricas_avanzadas()
        
        # Programar próxima actualización
        self.master.after(500, self._actualizar_ui_memoria)

    def _actualizar_metricas_avanzadas(self):
        """Actualiza las métricas avanzadas de memoria y paginación"""
        try:
            if hasattr(self.simulador.memoria, 'obtener_estadisticas_avanzadas'):
                stats = self.simulador.memoria.obtener_estadisticas_avanzadas()
                
                # Actualizar métricas de rendimiento
                rendimiento = stats.get('rendimiento', {})
                self.label_page_faults.config(text=f"Page Faults: {rendimiento.get('total_page_faults', 0)}")
                self.label_hits.config(text=f"Hits: {rendimiento.get('total_hits', 0)}")
                self.label_hit_ratio.config(text=f"Hit Ratio: {rendimiento.get('hit_ratio_global', 0.0):.1f}%")
                
                # Actualizar métricas del algoritmo
                algoritmo_stats = stats.get('algoritmo_reemplazo', {})
                self.label_algoritmo_actual.config(text=f"Algoritmo: {algoritmo_stats.get('algoritmo', 'N/A')}")
                self.label_reemplazos.config(text=f"Reemplazos: {algoritmo_stats.get('reemplazos', 0)}")
                
                # Actualizar estado de páginas
                memoria_stats = stats.get('memoria', {})
                ram_stats = memoria_stats.get('ram', {})
                if ram_stats:
                    ocupadas = ram_stats.get('ocupadas', 0)
                    total = ram_stats.get('total_paginas', 64)
                    self.label_paginas_activas.config(text=f"Páginas en RAM: {ocupadas}/{total}")
                
            else:
                # Fallback a métricas básicas
                self.label_page_faults.config(text="Page Faults: N/A")
                self.label_hits.config(text="Hits: N/A") 
                self.label_hit_ratio.config(text="Hit Ratio: N/A")
                self.label_algoritmo_actual.config(text="Algoritmo: Básico")
                self.label_reemplazos.config(text="Reemplazos: N/A")
                self.label_paginas_activas.config(text="Páginas en RAM: N/A")
                
        except Exception as e:
            print(f"⚠️ Error actualizando métricas avanzadas: {e}")


    def _actualizar_tabla_procesos(self):
      
        for item in self.tabla_procesos.get_children():
            self.tabla_procesos.delete(item)

        
        todos_procesos = self.simulador.todos_los_procesos()

     
        for proceso in todos_procesos:
   
            nombre_proceso = getattr(proceso, 'nombre', f'Proceso {proceso.pid}')

        
            memoria_mb = proceso.tamano_memoria // (1024 * 1024)

      
            self.tabla_procesos.insert("", "end", values=(
                proceso.pid,
                nombre_proceso,
                proceso.estado.capitalize(),  
                proceso.duracion,
                memoria_mb
            ), tags=(proceso.pid,))
            # Obtener el mismo color que se usa en la memoria RAM
            pid_tag = f"P{proceso.pid}" 

            # Asignar color coherente si existe
            color_proceso = self.adaptador_memoria.procesos_colores.get(pid_tag, {}).get("color", "#FFFFFF")

            self.tabla_procesos.tag_configure(proceso.pid, background=color_proceso)

    def _crear_layout(self):
        """
        Crea y posiciona los 3 frames principales que dividen la ventana.
        Usamos el gestor de geometría 'grid' con pesos para control proporcional.
        """
      
        self.master.grid_columnconfigure(0, weight=1)

     
        self.master.grid_rowconfigure(0, weight=5)  
        self.master.grid_rowconfigure(1, weight=25) 
        self.master.grid_rowconfigure(2, weight=70)  

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
        )  # Un gris claro para la derecha
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
            command=self._mostrar_ayuda
        )
        self.boton_ayuda.image = self.imagen_ayuda_tk
        self.boton_ayuda.pack(side="left", padx=10, pady=10)


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
        # Ajustar el botón para que sea más pequeño y deje espacio al panel de configuración
        self.boton_agregar.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.25)

        # --- Panel de Configuración Avanzada de Memoria ---
        self.frame_config_avanzada = tk.Frame(self.frame_3_1_3, bg="#2d2d2d")
        self.frame_config_avanzada.place(relx=0.05, rely=0.32, relwidth=0.9, relheight=0.63)
        
        # Título del panel
        tk.Label(
            self.frame_config_avanzada,
            text="🧠 Configuración Avanzada",
            bg="#2d2d2d",
            fg="white",
            font=font_form_cuantum
        ).pack(pady=(5, 10))
        
        # Frame para algoritmos de reemplazo
        frame_algoritmos = tk.Frame(self.frame_config_avanzada, bg="#2d2d2d")
        frame_algoritmos.pack(fill="x", padx=10, pady=5)
        
        tk.Label(
            frame_algoritmos,
            text="Algoritmo de Reemplazo:",
            bg="#2d2d2d",
            fg="white",
            font=('Helvetica', 9)
        ).pack(anchor="w")
        
        # Variable para el algoritmo seleccionado
        self.algoritmo_reemplazo = tk.StringVar(value="LRU")
        
        # Radio buttons para algoritmos
        frame_radios = tk.Frame(frame_algoritmos, bg="#2d2d2d")
        frame_radios.pack(fill="x", pady=2)
        
        algoritmos = [("FIFO", "FIFO"), ("LRU", "LRU"), ("LFU", "LFU")]
        for texto, valor in algoritmos:
            tk.Radiobutton(
                frame_radios,
                text=texto,
                variable=self.algoritmo_reemplazo,
                value=valor,
                bg="#2d2d2d",
                fg="white",
                selectcolor="#424242",
                font=('Helvetica', 8),
                command=self._cambiar_algoritmo_reemplazo
            ).pack(side="left", padx=5)
        
        # Frame para umbrales
        frame_umbrales = tk.Frame(self.frame_config_avanzada, bg="#2d2d2d")
        frame_umbrales.pack(fill="x", padx=10, pady=5)
        
        tk.Label(
            frame_umbrales,
            text="Umbrales de SWAP:",
            bg="#2d2d2d",
            fg="white",
            font=('Helvetica', 9)
        ).pack(anchor="w")
        
        # Umbrales
        frame_umbral_vals = tk.Frame(frame_umbrales, bg="#2d2d2d")
        frame_umbral_vals.pack(fill="x", pady=2)
        
        tk.Label(frame_umbral_vals, text="Conservador:", bg="#2d2d2d", fg="white", font=('Helvetica', 8)).grid(row=0, column=0, sticky="w")
        self.entry_conservador = tk.Entry(frame_umbral_vals, width=8, font=('Helvetica', 8))
        self.entry_conservador.grid(row=0, column=1, padx=(5,10))
        self.entry_conservador.insert(0, "60")
        
        tk.Label(frame_umbral_vals, text="Agresivo:", bg="#2d2d2d", fg="white", font=('Helvetica', 8)).grid(row=0, column=2, sticky="w")
        self.entry_agresivo = tk.Entry(frame_umbral_vals, width=8, font=('Helvetica', 8))
        self.entry_agresivo.grid(row=0, column=3, padx=5)
        self.entry_agresivo.insert(0, "80")
        
        # Botón aplicar configuración
        tk.Button(
            frame_umbrales,
            text="Aplicar",
            bg="#4CAF50",
            fg="white",
            font=('Helvetica', 8),
            command=self._aplicar_configuracion_avanzada
        ).pack(pady=5)
        
        # Botón para demostración de algoritmos
        tk.Button(
            self.frame_config_avanzada,
            text="🎯 Demo Algoritmos",
            bg="#9C27B0",
            fg="white",
            font=('Helvetica', 9, 'bold'),
            command=self._demostrar_algoritmos
        ).pack(pady=5)

        # Configurar estilo para la tabla
        style = ttk.Style()
        style.configure("Treeview",
                        background="#616161",  # Fondo gris para celdas  #### Proceso.generar_color(id)
                        foreground="Black",    # Texto negro
                        fieldbackground="#616161",  # Fondo de campos
                        font=('Helvetica', 10))

        style.configure("Treeview.Heading",
                        background="#535353",  # Fondo más oscuro para encabezados
                        foreground="black",
                        font=('Helvetica', 10, 'bold'))

        style.map('Treeview',
                background=[('selected', '#424242')])  # Color selección

        # Crear la tabla
        self.tabla_procesos = ttk.Treeview(
            self.frame_inf_derecho,
            columns=("PID", "Nombre", "Estado", "Duración", "Memoria"),
            show="headings",
            style="Treeview"  # Aplicar el estilo
        )

        # Configurar encabezados
        self.tabla_procesos.heading("PID", text="PID")
        self.tabla_procesos.heading("Nombre", text="Nombre")
        self.tabla_procesos.heading("Estado", text="Estado")
        self.tabla_procesos.heading("Duración", text="Duración")
        self.tabla_procesos.heading("Memoria", text="Memoria (MB)")

        # Configurar columnas
        self.tabla_procesos.column("PID", width=50, anchor="center")
        self.tabla_procesos.column("Nombre", width=120, anchor="w")
        self.tabla_procesos.column("Estado", width=80, anchor="center")
        self.tabla_procesos.column("Duración", width=70, anchor="center")
        self.tabla_procesos.column("Memoria", width=90, anchor="center")

        # --- Panel de Métricas Avanzadas ---
        self.frame_metricas = tk.Frame(self.frame_inf_derecho, bg="#3d3d3d")
        self.frame_metricas.pack(fill="x", padx=10, pady=5)
        
        # Título de métricas
        tk.Label(
            self.frame_metricas,
            text="📊 Métricas de Memoria Avanzadas",
            bg="#3d3d3d",
            fg="white",
            font=('Helvetica', 10, 'bold')
        ).pack(pady=5)
        
        # Frame para métricas en dos columnas
        frame_metricas_cols = tk.Frame(self.frame_metricas, bg="#3d3d3d")
        frame_metricas_cols.pack(fill="x", padx=5, pady=5)
        
        # Columna izquierda
        frame_col1 = tk.Frame(frame_metricas_cols, bg="#3d3d3d")
        frame_col1.pack(side="left", fill="both", expand=True)
        
        self.label_page_faults = tk.Label(
            frame_col1,
            text="Page Faults: 0",
            bg="#3d3d3d",
            fg="#FFB74D",
            font=('Helvetica', 9)
        )
        self.label_page_faults.pack(anchor="w", pady=1)
        
        self.label_hits = tk.Label(
            frame_col1,
            text="Hits: 0",
            bg="#3d3d3d",
            fg="#81C784",
            font=('Helvetica', 9)
        )
        self.label_hits.pack(anchor="w", pady=1)
        
        self.label_hit_ratio = tk.Label(
            frame_col1,
            text="Hit Ratio: 0.0%",
            bg="#3d3d3d",
            fg="#64B5F6",
            font=('Helvetica', 9)
        )
        self.label_hit_ratio.pack(anchor="w", pady=1)
        
        # Columna derecha
        frame_col2 = tk.Frame(frame_metricas_cols, bg="#3d3d3d")
        frame_col2.pack(side="right", fill="both", expand=True)
        
        self.label_algoritmo_actual = tk.Label(
            frame_col2,
            text="Algoritmo: LRU",
            bg="#3d3d3d",
            fg="#BA68C8",
            font=('Helvetica', 9)
        )
        self.label_algoritmo_actual.pack(anchor="w", pady=1)
        
        self.label_reemplazos = tk.Label(
            frame_col2,
            text="Reemplazos: 0",
            bg="#3d3d3d",
            fg="#F06292",
            font=('Helvetica', 9)
        )
        self.label_reemplazos.pack(anchor="w", pady=1)
        
        self.label_paginas_activas = tk.Label(
            frame_col2,
            text="Páginas en RAM: 0/64",
            bg="#3d3d3d",
            fg="#4DB6AC",
            font=('Helvetica', 9)
        )
        self.label_paginas_activas.pack(anchor="w", pady=1)

        # Añadir scrollbar para la tabla
        scrollbar = ttk.Scrollbar(
            self.frame_inf_derecho,
            orient="vertical",
            command=self.tabla_procesos.yview
        )
        self.tabla_procesos.configure(yscrollcommand=scrollbar.set)

        # Crear frame para botones de la tabla
        self.frame_botones_tabla = tk.Frame(self.frame_inf_derecho, bg="#616161")
        
        # Botón eliminar proceso
        self.boton_eliminar = tk.Button(
            self.frame_botones_tabla,
            text="Eliminar Proceso",
            bg="#c62828",  # Rojo para eliminar
            fg="white",
            activebackground="#d32f2f",
            font=('Helvetica', 10, 'bold'),
            bd=0,
            cursor="hand2",
            command=self._eliminar_proceso_seleccionado
        )
        
        # Empaquetar botones
        self.boton_eliminar.pack(side="left", padx=5, pady=5)
        
        # Empaquetar todo
        self.frame_botones_tabla.pack(fill="x", padx=10, pady=(0,5))
        scrollbar.pack(side="right", fill="y")
        self.tabla_procesos.pack(fill="both", expand=True, padx=10, pady=(5,10))

    def _finalizar_simulacion(self):
        """Finaliza la simulación actual"""
        if self.simulacion_iniciada:
            self.simulacion_iniciada = False
            self.simulador.detener_simulacion()
            self.boton_iniciar.config(state=tk.NORMAL)
            self.boton_finalizar.config(state=tk.DISABLED)
            print("🛑 Simulación finalizada por el usuario")

    def _cambiar_algoritmo_reemplazo(self):
        """Cambia el algoritmo de reemplazo de páginas"""
        algoritmo = self.algoritmo_reemplazo.get()
        if hasattr(self.simulador.memoria, 'cambiar_algoritmo_reemplazo'):
            success = self.simulador.memoria.cambiar_algoritmo_reemplazo(algoritmo)
            if success:
                print(f"🔄 Algoritmo de reemplazo cambiado a: {algoritmo}")
                self.label_algoritmo_actual.config(text=f"Algoritmo: {algoritmo}")
            else:
                print(f"❌ Error al cambiar algoritmo a: {algoritmo}")
    
    def _aplicar_configuracion_avanzada(self):
        """Aplica la configuración avanzada de umbrales"""
        try:
            conservador = float(self.entry_conservador.get()) / 100.0
            agresivo = float(self.entry_agresivo.get()) / 100.0
            
            if not (0.0 <= conservador <= 1.0) or not (0.0 <= agresivo <= 1.0):
                messagebox.showerror("Error", "Los umbrales deben estar entre 0 y 100")
                return
            
            if conservador >= agresivo:
                messagebox.showerror("Error", "El umbral conservador debe ser menor que el agresivo")
                return
            
            if hasattr(self.simulador.memoria, 'configurar_umbrales_swap'):
                success = self.simulador.memoria.configurar_umbrales_swap(agresivo, conservador)
                if success:
                    print(f"⚙️ Umbrales configurados: Conservador={conservador:.1%}, Agresivo={agresivo:.1%}")
                    messagebox.showinfo("Éxito", "Configuración aplicada correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo aplicar la configuración")
            else:
                messagebox.showwarning("Advertencia", "Gestión avanzada no disponible")
                
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

        # Actualizar etiquetas de métricas después de cambiar configuración
        self._actualizar_metricas_memoria()

    def _actualizar_metricas_memoria(self):
        """Actualiza las etiquetas de métricas de memoria"""
        uso = self.simulador.memoria.obtener_uso_memoria()
        
        # Obtener estadísticas de page faults y hits
        page_faults = uso.get('page_faults', 0)
        hits = uso.get('hits', 0)
        hit_ratio = uso.get('hit_ratio', 0.0) * 100  # Convertir a porcentaje
        
        # Actualizar etiquetas
        self.label_page_faults.config(text=f"Page Faults: {page_faults}")
        self.label_hits.config(text=f"Hits: {hits}")
        self.label_hit_ratio.config(text=f"Hit Ratio: {hit_ratio:.1f}%")
        
        # Actualizar etiquetas de páginas activas y algoritmo
        self.label_paginas_activas.config(text=f"Páginas en RAM: {len(self.simulador.memoria.bloques_ocupados)}/{len(self.simulador.memoria.bloques_totales)}")
        self.label_algoritmo_actual.config(text=f"Algoritmo: {self.algoritmo_reemplazo.get()}")

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

    def _eliminar_proceso_seleccionado(self):
        """Eliminar el proceso seleccionado de la tabla"""
        seleccion = self.tabla_procesos.selection()
        
        if not seleccion:
            messagebox.showwarning("Sin selección", "Por favor selecciona un proceso para eliminar")
            return
        
        # Obtener el PID del proceso seleccionado
        item = seleccion[0]
        valores = self.tabla_procesos.item(item, 'values')
        pid_seleccionado = int(valores[0])
        nombre_proceso = valores[1]
        estado_proceso = valores[2]
        
        # Verificar que el proceso no esté ejecutándose
        if estado_proceso in ["Ejecutando", "En CPU"]:
            messagebox.showerror("Error", f"No se puede eliminar el proceso '{nombre_proceso}' porque está ejecutándose")
            return
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno("Confirmar eliminación", 
                                       f"¿Estás seguro de eliminar el proceso '{nombre_proceso}' (PID: {pid_seleccionado})?")
        
        if not respuesta:
            return
        
        # Buscar y eliminar el proceso del simulador
        proceso_eliminado = False
        
        # Buscar en procesos nuevos
        for i, proceso in enumerate(self.simulador.procesos_nuevos):
            if proceso.pid == pid_seleccionado:
                self.simulador.procesos_nuevos.pop(i)
                proceso_eliminado = True
                break
        
        # Buscar en cola de listos
        if not proceso_eliminado:
            for i, proceso in enumerate(self.simulador.cola_listos):
                if proceso.pid == pid_seleccionado:
                    # Liberar memoria del proceso
                    self.simulador.memoria.liberar_memoria(proceso)
                    self.simulador.cola_listos.pop(i)
                    proceso_eliminado = True
                    break
        
        # Buscar en procesos terminados
        if not proceso_eliminado:
            for i, proceso in enumerate(self.simulador.procesos_terminados):
                if proceso.pid == pid_seleccionado:
                    self.simulador.procesos_terminados.pop(i)
                    proceso_eliminado = True
                    break
        
        if proceso_eliminado:
            # Actualizar la tabla
            self._actualizar_tabla_procesos()
            print(f"🗑️ Proceso P{pid_seleccionado} '{nombre_proceso}' eliminado exitosamente")
            messagebox.showinfo("Proceso eliminado", f"El proceso '{nombre_proceso}' ha sido eliminado")
        else:
            messagebox.showerror("Error", f"No se pudo encontrar el proceso con PID {pid_seleccionado}")

    def _abrir_ventana_agregar_proceso(self):
        ventana = tk.Toplevel(self.master)
        ventana.title("Añadir Proceso o Programa")
        ventana.configure(bg="#2c2c2c")
        ventana.geometry("450x500")
        ventana.resizable(False, False)

        # Crear notebook para pestañas
        notebook = ttk.Notebook(ventana)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña 1: Proceso Manual
        frame_manual = tk.Frame(notebook, bg="#2c2c2c")
        notebook.add(frame_manual, text="Proceso Manual")
        
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
        form_frame = tk.Frame(frame_manual, bg="#2c2c2c")
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

        # Función para añadir el proceso manual
        def agregar_proceso_manual():
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

        # Botones para proceso manual
        btn_frame_manual = tk.Frame(frame_manual, bg="#2c2c2c")
        btn_frame_manual.pack(pady=10)
        
        tk.Button(
            btn_frame_manual, 
            text="Añadir Proceso", 
            command=agregar_proceso_manual,
            width=15,
            bg="#2ECC71",
            fg="white"
        ).pack(pady=5)

        # Pestaña 2: Programas Predefinidos
        frame_programas = tk.Frame(notebook, bg="#2c2c2c")
        notebook.add(frame_programas, text="Programas Predefinidos")
        
        # Título
        tk.Label(
            frame_programas,
            text="🖥️ Selecciona un Programa",
            bg="#2c2c2c",
            fg="white",
            font=('Helvetica', 12, 'bold')
        ).pack(pady=10)
        
        # Frame para la lista de programas
        lista_frame = tk.Frame(frame_programas, bg="#2c2c2c")
        lista_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Crear gestor de programas si no existe
        if not hasattr(self, 'gestor_programas'):
            from programa import GestorProgramas
            self.gestor_programas = GestorProgramas()
        
        # Lista de programas con información
        programas_info = {
            "Word": "📝 Microsoft Word - Editor de texto (400MB)",
            "Excel": "📊 Microsoft Excel - Hoja de cálculo (350MB)", 
            "Chrome": "🌐 Google Chrome - Navegador web (800MB)",
            "Photoshop": "🎨 Adobe Photoshop - Editor de imágenes (1200MB)",
            "Visual Studio": "⚙️ Visual Studio - IDE de desarrollo (900MB)",
            "Steam": "🎮 Steam - Plataforma de juegos (600MB)",
            "Zoom": "📹 Zoom - Videoconferencias (200MB)",
            "Spotify": "🎵 Spotify - Reproductor de música (250MB)"
        }
        
        # Variable para programa seleccionado
        programa_seleccionado = tk.StringVar()
        
        # Crear botones de radio para cada programa
        for programa, descripcion in programas_info.items():
            tk.Radiobutton(
                lista_frame,
                text=descripcion,
                variable=programa_seleccionado,
                value=programa,
                bg="#2c2c2c",
                fg="white",
                selectcolor="#424242",
                font=('Helvetica', 10),
                anchor="w"
            ).pack(fill="x", pady=2)
        
        # Establecer selección por defecto
        programa_seleccionado.set("Word")
        
        # Campo para tiempo de llegada del programa
        tiempo_frame = tk.Frame(frame_programas, bg="#2c2c2c")
        tiempo_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(tiempo_frame, text="Tiempo de llegada:", bg="#2c2c2c", fg="white").pack(side="left")
        var_tiempo_programa = tk.StringVar(value="0")
        tk.Entry(
            tiempo_frame, 
            textvariable=var_tiempo_programa, 
            width=10,
            validate="key", 
            validatecommand=vcmd
        ).pack(side="right")
        
        # Función para lanzar programa
        def lanzar_programa():
            try:
                nombre_programa = programa_seleccionado.get()
                tiempo_llegada = int(var_tiempo_programa.get() or "0")
                
                if not nombre_programa:
                    messagebox.showwarning("Advertencia", "Selecciona un programa")
                    return
                
                # Crear programa predefinido
                programa = self.gestor_programas.crear_programa_predefinido(
                    nombre_programa, tiempo_llegada
                )
                
                # Lanzar programa (esto lo divide en procesos hijos)
                procesos_hijos = self.gestor_programas.lanzar_programa(programa, self.simulador)
                
                # Actualizar UI
                self._actualizar_ui_memoria()
                self._actualizar_tabla_procesos()
                ventana.destroy()
                
                print(f"🚀 Programa '{nombre_programa}' lanzado:")
                print(f"   📦 Dividido en {len(procesos_hijos)} procesos hijos")
                print(f"   💾 Tamaño total: {programa.tamano_total_mb}MB")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al lanzar programa: {str(e)}")
        
        # Botón para lanzar programa
        tk.Button(
            frame_programas,
            text="🚀 Lanzar Programa",
            command=lanzar_programa,
            bg="#3498DB",
            fg="white",
            font=('Helvetica', 11, 'bold'),
            width=20
        ).pack(pady=15)
        
        # Botón de cerrar (común para ambas pestañas)
        tk.Button(
            ventana,
            text="Cerrar",
            command=ventana.destroy,
            bg="#E74C3C",
            fg="white",
            width=15
        ).pack(pady=10)

        # Generar valores aleatorios iniciales para la pestaña manual
        generar_aleatorio()

        # Hacer la ventana modal
        ventana.grab_set()


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
        Proceso(nombre="Reproductor", tiempo_llegada=2, duracion=6, tamano_memoria=300*1024*1024),
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
                self.master.after(2000, self._paso_simulacion)  # Paso cada 2 segundos
            else:
                self.simulacion_iniciada = False
                print("🏁 Simulación completada")
                self.mostrar_estadisticas() # Mostrar estadísticas al finalizar
                
    def mostrar_estadisticas(self):
        """Muestra una ventana con las estadísticas de la simulación"""
        # Obtener estadísticas del simulador
        estadisticas = self.simulador.calcular_estadisticas()
        
        # DEBUG: Imprimir estadísticas para verificar
        print(f"🔍 DEBUG - Estadísticas obtenidas:")
        print(f"   Procesos terminados: {len(self.simulador.procesos_terminados)}")
        print(f"   Estadísticas de procesos: {len(estadisticas.get('procesos', []))}")
        if estadisticas.get('procesos'):
            for proc in estadisticas['procesos']:
                print(f"   - {proc.get('nombre', 'Sin nombre')} (PID {proc.get('pid', '?')})")
        
        # Crear ventana de estadísticas
        ventana = tk.Toplevel(self.master)
        ventana.title("Estadísticas de Simulación")
        ventana.geometry("800x600")
        
        # Crear notebook (pestañas)
        notebook = ttk.Notebook(ventana)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña 1: Tabla detallada
        frame_tabla = ttk.Frame(notebook)
        notebook.add(frame_tabla, text="Detalle por Proceso")
        
        # Crear tabla
        tabla = ttk.Treeview(frame_tabla, columns=("PID", "Nombre", "T. Espera", "T. Respuesta", "T. Retorno"), show="headings")
        tabla.heading("PID", text="PID")
        tabla.heading("Nombre", text="Nombre")
        tabla.heading("T. Espera", text="T. Espera")
        tabla.heading("T. Respuesta", text="T. Respuesta")
        tabla.heading("T. Retorno", text="T. Retorno")
        
        # Configurar columnas
        tabla.column("PID", width=50, anchor="center")
        tabla.column("Nombre", width=150, anchor="w")
        tabla.column("T. Espera", width=100, anchor="center")
        tabla.column("T. Respuesta", width=100, anchor="center")
        tabla.column("T. Retorno", width=100, anchor="center")
        
        # Insertar datos
        if "procesos" in estadisticas:
            for proc in estadisticas["procesos"]:
                tabla.insert("", "end", values=(
                    proc["pid"],
                    proc["nombre"],
                    f'{proc["tiempo_espera"]:.2f}',
                    f'{proc["tiempo_respuesta"]:.2f}',
                    f'{proc["tiempo_retorno"]:.2f}'
                ))
        
        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tabla.pack(fill="both", expand=True)
        
        # Pestaña 2: Resumen y comparativa
        frame_resumen = ttk.Frame(notebook)
        notebook.add(frame_resumen, text="Resumen")
        
        # Mostrar promedios
        ttk.Label(frame_resumen, text="Métricas Promedio:", font=("Arial", 12, "bold")).pack(pady=10)
        
        if estadisticas["promedios"]:
            promedios = estadisticas["promedios"]
            ttk.Label(frame_resumen, text=f"Tiempo de Espera: {promedios['tiempo_espera']:.2f} unidades").pack(pady=5)
            ttk.Label(frame_resumen, text=f"Tiempo de Respuesta: {promedios['tiempo_respuesta']:.2f} unidades").pack(pady=5)
            ttk.Label(frame_resumen, text=f"Tiempo de Retorno: {promedios['tiempo_retorno']:.2f} unidades").pack(pady=5)
        else:
            ttk.Label(frame_resumen, text="No hay procesos terminados para calcular estadísticas").pack(pady=10)
    
    def _mostrar_ayuda(self):
        """Muestra una ventana de ayuda con información sobre el simulador y los controles"""
        ventana_ayuda = tk.Toplevel(self.master)
        ventana_ayuda.title("Ayuda - Simulador de Sistema Operativo")
        ventana_ayuda.configure(bg="#2c2c2c")
        ventana_ayuda.geometry("700x600")
        ventana_ayuda.resizable(True, True)
        
        # Hacer la ventana modal
        ventana_ayuda.grab_set()
        
        # Frame principal con scrollbar
        main_frame = tk.Frame(ventana_ayuda, bg="#2c2c2c")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas y scrollbar para contenido scrolleable
        canvas = tk.Canvas(main_frame, bg="#2c2c2c", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2c2c2c")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurar estilos de texto
        titulo_font = font.Font(family="Helvetica", size=16, weight="bold")
        subtitulo_font = font.Font(family="Helvetica", size=12, weight="bold")
        texto_font = font.Font(family="Helvetica", size=10)
        
        # Título principal
        tk.Label(
            scrollable_frame, 
            text="🖥️ Simulador de Sistema Operativo", 
            font=titulo_font, 
            fg="#4CAF50", 
            bg="#2c2c2c"
        ).pack(pady=(0, 20))
        
        # Sección: ¿Qué es este simulador?
        tk.Label(
            scrollable_frame, 
            text="📋 ¿Qué es este simulador?", 
            font=subtitulo_font, 
            fg="white", 
            bg="#2c2c2c"
        ).pack(anchor="w", pady=(0, 5))
        
        descripcion = """Este simulador reproduce el comportamiento de un sistema operativo simplificado, 
incluyendo la gestión de procesos, memoria (RAM y SWAP) y planificación de CPU. 
Permite visualizar en tiempo real cómo el sistema asigna recursos y ejecuta procesos."""
        
        tk.Label(
            scrollable_frame, 
            text=descripcion, 
            font=texto_font, 
            fg="lightgray", 
            bg="#2c2c2c",
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=(0, 15))
        
        # Sección: Algoritmos de planificación
        tk.Label(
            scrollable_frame, 
            text="⚙️ Algoritmos de Planificación", 
            font=subtitulo_font, 
            fg="white", 
            bg="#2c2c2c"
        ).pack(anchor="w", pady=(0, 5))
        
        algoritmos = """• FCFS (First Come First Served): Los procesos se ejecutan en orden de llegada.
• SJF (Shortest Job First): Se ejecuta primero el proceso de menor duración.
• Round Robin (RR): Cada proceso recibe un quantum de tiempo, rotando cíclicamente.
• Prioridad: Los procesos con mayor prioridad se ejecutan primero."""
        
        tk.Label(
            scrollable_frame, 
            text=algoritmos, 
            font=texto_font, 
            fg="lightgray", 
            bg="#2c2c2c",
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=(0, 15))
        
        # Sección: Controles de la interfaz
        tk.Label(
            scrollable_frame, 
            text="🎮 Controles de la Interfaz", 
            font=subtitulo_font, 
            fg="white", 
            bg="#2c2c2c"
        ).pack(anchor="w", pady=(0, 5))
        
        controles = """• Iniciar: Comienza la simulación con los procesos configurados.
• Finalizar: Detiene la simulación en curso.
• Añadir Proceso: Abre una ventana para agregar un nuevo proceso personalizado.
• Selección de Algoritmo: Cambia el algoritmo de planificación (FCFS, SJF, RR, Prioridad).
• Quantum (solo RR): Define el tiempo máximo que un proceso puede ejecutarse antes de ser interrumpido."""
        
        tk.Label(
            scrollable_frame, 
            text=controles, 
            font=texto_font, 
            fg="lightgray", 
            bg="#2c2c2c",
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=(0, 15))
        
        # Sección: Visualización de memoria
        tk.Label(
            scrollable_frame, 
            text="💾 Visualización de Memoria", 
            font=subtitulo_font, 
            fg="white", 
            bg="#2c2c2c"
        ).pack(anchor="w", pady=(0, 5))
        
        memoria = """• Barras de RAM y SWAP: Muestran el uso actual de memoria.
• Colores: Cada proceso tiene un color único para identificarlo fácilmente.
• Porcentajes: Indican el porcentaje de memoria utilizada en tiempo real.
• Bloques: Representan segmentos de memoria de 64MB cada uno."""
        
        tk.Label(
            scrollable_frame, 
            text=memoria, 
            font=texto_font, 
            fg="lightgray", 
            bg="#2c2c2c",
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=(0, 15))
        
        # Sección: Tabla de procesos
        tk.Label(
            scrollable_frame, 
            text="📊 Tabla de Procesos", 
            font=subtitulo_font, 
            fg="white", 
            bg="#2c2c2c"
        ).pack(anchor="w", pady=(0, 5))
        
        tabla = """• PID: Identificador único del proceso.
• Nombre: Nombre descriptivo del proceso.
• Estado: Nuevo, Listo, Ejecutando, Terminado.
• Llegada: Tiempo en que el proceso llega al sistema.
• Duración: Tiempo total de CPU que necesita el proceso.
• Memoria: Cantidad de memoria RAM requerida."""
        
        tk.Label(
            scrollable_frame, 
            text=tabla, 
            font=texto_font, 
            fg="lightgray", 
            bg="#2c2c2c",
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=(0, 15))
        
        # Sección: Estadísticas
        tk.Label(
            scrollable_frame, 
            text="📈 Estadísticas de Rendimiento", 
            font=subtitulo_font, 
            fg="white", 
            bg="#2c2c2c"
        ).pack(anchor="w", pady=(0, 5))
        
        estadisticas = """Al finalizar la simulación se muestran métricas importantes:
• Tiempo de Espera: Tiempo que un proceso espera en la cola de listos.
• Tiempo de Respuesta: Tiempo desde la llegada hasta la primera ejecución.
• Tiempo de Retorno: Tiempo total desde la llegada hasta la finalización.
• Promedios: Valores promedio de todas las métricas para evaluar eficiencia."""
        
        tk.Label(
            scrollable_frame, 
            text=estadisticas, 
            font=texto_font, 
            fg="lightgray", 
            bg="#2c2c2c",
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=(0, 15))
        
        # Sección: Consejos de uso
        tk.Label(
            scrollable_frame, 
            text="💡 Consejos de Uso", 
            font=subtitulo_font, 
            fg="white", 
            bg="#2c2c2c"
        ).pack(anchor="w", pady=(0, 5))
        
        consejos = """• Experimenta con diferentes algoritmos para comparar su eficiencia.
• Ajusta el quantum en Round Robin para ver cómo afecta el rendimiento.
• Añade procesos durante la simulación para ver la respuesta en tiempo real.
• Observa cómo la memoria se fragmenta y reorganiza dinámicamente.
• Compara las estadísticas entre diferentes configuraciones."""
        
        tk.Label(
            scrollable_frame, 
            text=consejos, 
            font=texto_font, 
            fg="lightgray", 
            bg="#2c2c2c",
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=(0, 20))
        
        # Botón de cerrar
        tk.Button(
            scrollable_frame, 
            text="Cerrar", 
            command=ventana_ayuda.destroy,
            bg="#4CAF50",
            fg="white",
            font=texto_font,
            width=15,
            pady=8
        ).pack(pady=(10, 0))
        
        # Configurar el canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Limpiar binding al cerrar ventana
        def on_closing():
            canvas.unbind_all("<MouseWheel>")
            ventana_ayuda.destroy()
        
        ventana_ayuda.protocol("WM_DELETE_WINDOW", on_closing)

    def _demostrar_algoritmos(self):
        """Ejecuta una demostración de los algoritmos de reemplazo"""
        try:
            # Crear ventana de demostración
            demo_window = tk.Toplevel(self.root)
            demo_window.title("🎯 Demostración de Algoritmos")
            demo_window.geometry("600x400")
            demo_window.configure(bg="#2E2E2E")
            
            # Marco principal
            main_frame = tk.Frame(demo_window, bg="#2E2E2E")
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Título
            titulo = tk.Label(
                main_frame,
                text="🎯 Demostración de Algoritmos de Reemplazo",
                font=('Helvetica', 14, 'bold'),
                bg="#2E2E2E",
                fg="white"
            )
            titulo.pack(pady=(0, 20))
            
            # Texto explicativo
            explicacion = tk.Label(
                main_frame,
                text="Esta demostración simula accesos a páginas para mostrar\nlas diferencias entre los algoritmos FIFO, LRU y LFU.",
                font=('Helvetica', 10),
                bg="#2E2E2E",
                fg="#CCCCCC",
                justify='center'
            )
            explicacion.pack(pady=(0, 20))
            
            # Área de resultados
            resultados_frame = tk.Frame(main_frame, bg="#424242")
            resultados_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            resultados_text = tk.Text(
                resultados_frame,
                bg="#424242",
                fg="white",
                font=('Courier', 9),
                wrap='word'
            )
            resultados_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Función para ejecutar la demo
            def ejecutar_demo():
                resultados_text.delete(1.0, tk.END)
                resultados_text.insert(tk.END, "🎯 Iniciando demostración de algoritmos...\n\n")
                
                # Simular secuencia de accesos a páginas
                secuencia_paginas = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
                
                # Obtener algoritmo actual
                algoritmo_actual = self.var_algoritmo.get()
                resultados_text.insert(tk.END, f"🧠 Algoritmo seleccionado: {algoritmo_actual}\n")
                resultados_text.insert(tk.END, f"📄 Secuencia de páginas: {secuencia_paginas}\n\n")
                
                # Simular métricas iniciales
                page_faults = 0
                hits = 0
                
                for i, pagina in enumerate(secuencia_paginas):
                    # Simular si es hit o fault (aleatorio para demo)
                    import random
                    es_hit = random.choice([True, False]) if i > 3 else False
                    
                    if es_hit:
                        hits += 1
                        resultados_text.insert(tk.END, f"✅ Acceso {i+1}: Página {pagina} - HIT\n")
                    else:
                        page_faults += 1
                        resultados_text.insert(tk.END, f"❌ Acceso {i+1}: Página {pagina} - PAGE FAULT\n")
                    
                    demo_window.update()
                    import time
                    time.sleep(0.5)
                
                # Mostrar resultados finales
                total_accesos = hits + page_faults
                hit_ratio = (hits / total_accesos * 100) if total_accesos > 0 else 0
                
                resultados_text.insert(tk.END, f"\n📊 RESULTADOS FINALES:\n")
                resultados_text.insert(tk.END, f"   Total accesos: {total_accesos}\n")
                resultados_text.insert(tk.END, f"   Hits: {hits}\n")
                resultados_text.insert(tk.END, f"   Page Faults: {page_faults}\n")
                resultados_text.insert(tk.END, f"   Hit Ratio: {hit_ratio:.1f}%\n\n")
                resultados_text.insert(tk.END, f"💡 Prueba cambiar el algoritmo en la configuración\n")
                resultados_text.insert(tk.END, f"   y ejecutar la demo nuevamente para comparar.\n")
                
                resultados_text.see(tk.END)
            
            # Botones
            botones_frame = tk.Frame(main_frame, bg="#2E2E2E")
            botones_frame.pack(pady=20)
            
            btn_ejecutar = tk.Button(
                botones_frame,
                text="🚀 Ejecutar Demostración",
                bg="#4CAF50",
                fg="white",
                font=('Helvetica', 10, 'bold'),
                command=ejecutar_demo
            )
            btn_ejecutar.pack(side='left', padx=10)
            
            btn_cerrar = tk.Button(
                botones_frame,
                text="❌ Cerrar",
                bg="#F44336",
                fg="white",
                font=('Helvetica', 10, 'bold'),
                command=demo_window.destroy
            )
            btn_cerrar.pack(side='left', padx=10)
            
            # Mensaje inicial
            resultados_text.insert(tk.END, "👆 Presiona 'Ejecutar Demostración' para comenzar\n\n")
            resultados_text.insert(tk.END, "🎯 Esta demo mostrará cómo el algoritmo seleccionado\n")
            resultados_text.insert(tk.END, "   maneja una secuencia de accesos a páginas.\n\n")
            resultados_text.insert(tk.END, "💡 Cambia el algoritmo en 'Configuración Avanzada'\n")
            resultados_text.insert(tk.END, "   y ejecuta la demo nuevamente para comparar.\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en demostración: {str(e)}")

# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    # 1. Crear la instancia de la ventana raíz
    root = tk.Tk()

    # 2. Crear una instancia de nuestra clase de UI, pasándole la ventana raíz
    app = SimuladorUI(root)

    # 3. Iniciar la aplicación
    app.iniciar()
