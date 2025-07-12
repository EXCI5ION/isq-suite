from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.suite.core.processor import RMNProcessor
from tkinter import ttk, messagebox, filedialog
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
from tksheet import Sheet
from pathlib import Path
import tkinter as tk
import pandas as pd
import numpy as np
import sys


class QuantificationFrame(tk.Toplevel):
        def __init__(self, parent, processor, factor_k=None, k_values=None):
            super().__init__(parent)
            self.title("Cuantificación")
            self.parent = parent
            self.processor = processor
            self.factor_k = factor_k  # Para estándar externo
            self.k_values = k_values  # Para estándar interno: diccionario {muestra: k}
            self.geometry("1000x600")
            self.base_path = self.get_base_path()  # Obtener la ruta base del proyecto
            icon_path = self.get_resource_path("icons", "qNMR.ico")  # Cargar el icono de la ventana
            self.iconbitmap(str(icon_path))
            self.resizable(True, True)

            # Frame principal
            main_frame = ttk.Frame(self)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Frame para la tabla
            table_frame = ttk.Frame(main_frame)
            table_frame.pack(fill=tk.BOTH, expand=True)

            # Crear la tabla
            self.create_table(table_frame)

            # Configurar menú en la ventana
            self.create_menu()

            # Frame para botones
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)

            # Botones
            ttk.Button(button_frame, text="Dividir por n° de Protones",
                       command=self.divide_by_protons).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Calcular Concentraciones",
                       command=self.calculate_concentrations).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Exportar Tabla",
                       command=self.export_table).pack(side=tk.LEFT, padx=5)

            # Cargar datos iniciales
            self.load_initial_data()

        def get_base_path(self):
            """Obtiene la ruta base del proyecto"""
            if getattr(sys, 'frozen', False):  # Ejecución como binario empaquetado
                return Path(sys.executable).parent
            else:  # Ejecución desde código fuente
                return Path(__file__).resolve().parent.parent.parent.parent

        def get_resource_path(self, *relative_path):
            """Obtiene la ruta absoluta a un recurso"""
            resource_path = self.base_path / "resources" / Path(*relative_path)

            # Verificar si existe
            if not resource_path.exists():
                # Intentar ruta alternativa para desarrollo
                dev_path = self.base_path.parent / "resources" / Path(*relative_path)
                if dev_path.exists():
                    return dev_path
                print(f"Recurso no encontrado: {resource_path}")
                return None

            return resource_path

        def create_menu(self):
            """Crea un menú en la ventana de cuantificación"""
            menu_bar = tk.Menu(self)
            self.config(menu=menu_bar)

            file_menu = tk.Menu(menu_bar, tearoff=0)
            edit_menu = tk.Menu(menu_bar, tearoff=0)

            menu_bar.add_cascade(label="Archivo", menu=file_menu)
            menu_bar.add_cascade(label="Editar", menu=edit_menu)

            file_menu.add_command(label="Exportar", command=self.export_table)
            file_menu.add_separator()
            file_menu.add_command(label="Cerrar", command=self.destroy)

            edit_menu.add_command(label="Deshacer", command=self.table.undo)
            edit_menu.add_command(label="Rehacer", command=self.table.redo)
            edit_menu.add_separator()
            edit_menu.add_command(label="Copiar", command=self.table.copy)
            edit_menu.add_command(label="Pegar", command=self.table.paste)
            edit_menu.add_command(label="Eliminar", command=self.table.delete)

        def create_table(self, parent):
            """Crea la tabla editable con tksheet"""
            self.table = Sheet(
                parent,
                show_x_scrollbar=True,
                show_y_scrollbar=True,
                width=950,
                height=450
            )

            # Habilitar funcionalidades
            self.table.enable_bindings(
                "single_select",
                "drag_select",
                "edit_cell",
                "column_select",
                "row_select",
                "copy",
                "paste",
                "delete",
                "arrowkeys",
                "right_click_popup_menu",
                "rc_insert_row",
                "rc_delete_row",
                "undo",
                "edit_header"
            )

            # Configurar encabezados
            self.table.headers(["Muestra"] + self.processor.get_integrales().columns.tolist())

            # Empaquetar la tabla
            self.table.pack(fill=tk.BOTH, expand=True)

        def load_initial_data(self):
            """Carga los datos iniciales en la tabla"""
            df = self.processor.get_integrales()

            # Agregar fila para protones
            protones_row = ["n° protones"] + [1] * len(df.columns)

            # Preparar datos para la tabla
            data = [protones_row]
            for idx, row in df.iterrows():
                data.append([idx] + row.tolist())

            # Establecer datos en la tabla
            self.table.set_sheet_data(data)

            # Formatear fila de protones
            self.table.highlight_cells(row=0, bg="lightblue")
            self.table.readonly_cells(row=0, readonly=False)

        def divide_by_protons(self):
            """Divide los valores por el número de protones especificado"""
            try:
                # Obtener datos de la tabla
                all_data = self.table.get_sheet_data()

                # Obtener fila de protones (primera fila de datos)
                protones_row = all_data[0][1:]  # Excluye la primera celda ("Protones")

                # Convertir a números
                protones = []
                for val in protones_row:
                    try:
                        protones.append(float(val))
                    except ValueError:
                        protones.append(1.0)  # Valor por defecto si no es número

                # Procesar cada fila de muestra
                for i in range(1, len(all_data)):  # Comenzar desde la segunda fila
                    row = all_data[i]
                    for j in range(1, len(row)):
                        try:
                            value = float(row[j])
                            all_data[i][j] = value / protones[j - 1]
                        except (ValueError, TypeError):
                            pass  # Mantener el valor original si no es número

                # Actualizar la tabla
                self.table.set_sheet_data(all_data)

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo dividir por protones: {str(e)}")

        def calculate_concentrations(self):
            """Calcula las concentraciones usando el factor K apropiado"""
            try:
                # Determinar qué método de calibración se usó
                if self.factor_k is not None:
                    # Estándar externo: usar factor único
                    self.calculate_with_external_std()
                elif self.k_values:
                    # Estándar interno: usar factor por muestra
                    self.calculate_with_internal_std()
                else:
                    messagebox.showerror("Error", "No se ha configurado un método de calibración")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo calcular concentraciones: {str(e)}")

        def calculate_with_external_std(self):
            """Calcula concentraciones usando factor K de estándar externo"""
            all_data = self.table.get_sheet_data()

            # Procesar cada fila de muestra
            for i in range(1, len(all_data)):
                row = all_data[i]
                for j in range(1, len(row)):
                    try:
                        value = float(row[j])
                        all_data[i][j] = value * self.factor_k
                    except (ValueError, TypeError):
                        pass  # Mantener el valor original si no es número

            # Actualizar la tabla
            self.table.set_sheet_data(all_data)

        def calculate_with_internal_std(self):
            """Calcula concentraciones usando factores K por muestra de estándar interno"""
            all_data = self.table.get_sheet_data()

            # Procesar cada fila de muestra
            for i in range(1, len(all_data)):
                sample_name = all_data[i][0]
                k_value = self.k_values.get(sample_name)

                if k_value is None:
                    continue  # Saltar muestra sin factor K

                for j in range(1, len(all_data[i])):
                    try:
                        value = float(all_data[i][j])
                        all_data[i][j] = value * k_value
                    except (ValueError, TypeError):
                        pass  # Mantener el valor original si no es número

            # Actualizar la tabla
            self.table.set_sheet_data(all_data)
            messagebox.showinfo("Éxito", "Concentraciones calculadas usando estándar interno")

        def export_table(self):
            """Exporta la tabla a un archivo CSV"""
            try:
                # Obtener datos de la tabla
                all_data = self.table.get_sheet_data()
                headers = self.table.headers()

                # Crear DataFrame
                df = pd.DataFrame(all_data[1:], columns=headers)  # Excluir fila de protones

                # Pedir ubicación para guardar
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("Archivo CSV", "*.csv"), ("Archivo de Texto", "*.txt"), ("All Files", "*.*")]
                )

                if file_path:
                    df.to_csv(file_path, index=False)
                    messagebox.showinfo("Éxito", f"Tabla exportada a:\n{file_path}")  # Necesario?

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar la tabla: {str(e)}")


class QuantifyApp:
    def __init__(self):
        self.raiz = tk.Tk()
        self.raiz.title("qNMR")
        self.raiz.resizable(True, True)
        self.base_path = self.get_base_path()  # Obtener la ruta base del proyecto
        icon_path = self.get_resource_path("icons", "qNMR.ico")  # Cargar el icono de la ventana
        self.raiz.iconbitmap(str(icon_path))
        self.raiz.geometry("854x480")
        self.processor = RMNProcessor()
        self.factor_k = None  # Variable para almacenar el factor K de calibración externa
        self.k_values = {}  # Nuevo: almacenará una K por muestra (estándar interno)

        # Variables para selección
        self.selected_columns = []
        self.selecting_points = False

        self.create_menu()
        self.create_plot_frame()
        self.raiz.protocol("WM_DELETE_WINDOW", self.on_close)
        self.raiz.mainloop()

    def get_base_path(self):
        """Obtiene la ruta base del proyecto"""
        if getattr(sys, 'frozen', False):  # Ejecución como binario empaquetado
            return Path(sys.executable).parent
        else:  # Ejecución desde código fuente
            return Path(__file__).resolve().parent.parent.parent.parent

    def get_resource_path(self, *relative_path):
        """Obtiene la ruta absoluta a un recurso"""
        resource_path = self.base_path / "resources" / Path(*relative_path)

        # Verificar si existe
        if not resource_path.exists():
            # Intentar ruta alternativa para desarrollo
            dev_path = self.base_path.parent / "resources" / Path(*relative_path)
            if dev_path.exists():
                return dev_path
            print(f"Recurso no encontrado: {resource_path}")
            return None

        return resource_path

    def open_quantification(self, event=None):
        """Abre la ventana de cuantificación"""
        if self.processor.get_integrales().empty:
            messagebox.showerror("Error", "No hay integrales calculadas")
            return

        QuantificationFrame(
            self.raiz,
            processor=self.processor,
            factor_k=self.factor_k,  # Para estándar externo
            k_values=self.k_values  # Para estándar interno
        )

    def create_menu(self):
        bm = tk.Menu(self.raiz)
        self.raiz.config(menu=bm)
        archivo = tk.Menu(bm, tearoff=0)
        herramientas = tk.Menu(bm, tearoff=0)
        ayuda = tk.Menu(bm, tearoff=0)
        calibrar = tk.Menu(herramientas, tearoff=0)

        bm.add_cascade(label="Archivo", menu=archivo)
        bm.add_cascade(label="Herramientas", menu=herramientas)
        bm.add_cascade(label="Ayuda", menu=ayuda)

        archivo.add_command(label="Nuevo", command=self.nuevo, accelerator="Ctrl+N")
        archivo.add_command(label="Abrir", command=self.abrir, accelerator="Ctrl+O")
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.salir, accelerator="Alt+F4")
        herramientas.add_command(label="Seleccionar", command=self.seleccionar, accelerator="z")
        herramientas.add_command(label="Mostrar", command=self.mostrar_integrales, accelerator="m")
        herramientas.add_cascade(label="Calibrar", menu=calibrar)
        calibrar.add_command(label="Estandar Interno", command=self.open_internal_frame, accelerator="R")
        calibrar.add_command(label="Estandar Externo", command=self.open_external_frame, accelerator="Q")
        herramientas.add_command(label="Cuantificar", command=self.open_quantification, accelerator="c")

        ayuda.add_command(label="Acerca de...", command=self.acerca, accelerator="")

        self.raiz.bind("<Control-n>", self.nuevo)
        self.raiz.bind("<Control-o>", self.abrir)
        self.raiz.bind("<q>", self.open_external_frame)
        self.raiz.bind("<r>", self.open_internal_frame)
        self.raiz.bind("<c>", self.open_quantification)
        self.raiz.bind("<Alt-F4>", self.salir)

    def open_internal_frame(self, event=None):
        """Abre la ventana de calibración con estándar interno"""
        self.internal_frame = self.InternalStandardFrame(self.raiz, self, self.processor)
        self.internal_frame.grab_set()

    def open_external_frame(self, event=None):
        """Abre la ventana de calibración con estándar externo"""
        self.external_frame = self.ExternalFrame(self.raiz, self)  # Pasar self.raiz como padre
        self.external_frame.grab_set()  # Hacer la ventana modal

    def seleccionar(self, event=None):
        self.selecting_points = not self.selecting_points
        if not self.selecting_points:
            self.selected_columns.clear()

    def create_plot_frame(self):
        self.plot_frame = ttk.Frame(self.raiz)
        self.plot_frame.pack(expand=True, fill=tk.BOTH)

        # Mensaje inicial
        self.initial_label = tk.Label(
            self.plot_frame,
            text="Seleccione 'Abrir' para cargar un set de datos",
            font=("Arial", 14)
        )
        self.initial_label.pack(expand=True)

    def plot_graph(self):
        """Crea la gráfica con los datos cargados"""
        # Limpiar frame existente
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        plot_data = self.processor.get_plot_data()
        if plot_data is None:
            return

        # Extraer valores
        val_x = plot_data['val_x']
        prom_y = plot_data['prom_y']
        lim_inf = plot_data['lim_inf']
        lim_sup = plot_data['lim_sup']

        # Crear figura
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(left=0.04, right=0.99, top=0.99, bottom=0.04)
        ax.plot(val_x, prom_y, linewidth=0.5, color='red')
        ax.grid(True, which="both", color="gray", linestyle=":", linewidth=0.5)
        ax.set_xlim(lim_inf, lim_sup)
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        ax.invert_xaxis()

        # Eventos
        def on_key(event):
            if event.key == "z":
                self.selecting_points = not self.selecting_points
                if not self.selecting_points:
                    self.selected_columns.clear()
            elif event.key == "escape":
                self.selected_columns.clear()
                self.selecting_points = False

        def on_click(event):
            if self.selecting_points and event.xdata and event.inaxes == ax:
                x_value = event.xdata
                column_index = min(range(len(val_x)), key=lambda i: abs(val_x[i] - x_value))
                self.selected_columns.append(column_index)

                if len(self.selected_columns) == 2:
                    # Calcular integral usando el procesador
                    x1_val, x2_val, x_region, y_integral = self.processor.calculate_integral(
                        self.selected_columns[0], self.selected_columns[1]
                    )

                    # Dibujar región
                    offset = 0.3 * max(y_integral) if max(y_integral) > 0 else 0
                    ax.plot(x_region[::-1], y_integral + offset, color='green', linewidth=0.5)
                    ax.hlines(0, x1_val, x2_val, colors='green', linewidth=0.8)
                    plt.draw()
                    self.selected_columns.clear()

        def on_scroll(event):
            if event.inaxes != ax:
                return
            y_min, y_max = ax.get_ylim()
            y_center = event.ydata
            zoom_factor = 0.9 if event.button == "up" else 1.1
            new_y_min = (y_min - y_center) * zoom_factor + y_center
            new_y_max = (y_max - y_center) * zoom_factor + y_center
            ax.set_ylim(new_y_min, new_y_max)
            plt.draw()

        fig.canvas.mpl_connect("scroll_event", on_scroll)
        fig.canvas.mpl_connect("key_press_event", on_key)
        fig.canvas.mpl_connect("button_press_event", on_click)

        # Integrar en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, self.plot_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def abrir(self, event=None):
        """Abre un archivo de espectro"""
        file = filedialog.askopenfilename(
            title="Abrir espectro",
            filetypes=[("Archivos de espectro", "*.csv;*.txt")]
        )
        if file:
            try:
                self.processor.load_file(file)
                self.plot_graph()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")

    class ExternalFrame(tk.Toplevel):
        def __init__(self, parent, app):
            super().__init__(parent)
            self.title("Calibración - Estándar Externo")
            self.app = app
            self.base_path = self.get_base_path()  # Obtener la ruta base del proyecto
            icon_path = self.get_resource_path("icons", "qNMR.ico")  # Cargar el icono de la ventana
            self.iconbitmap(str(icon_path))
            self.resizable(False, False)
            self.ref_processor = RMNProcessor()

            # Variables para almacenar los valores
            self.integral_value = tk.DoubleVar()
            self.factor_k = tk.DoubleVar()

            self.create_widgets()

        def get_base_path(self):
            """Obtiene la ruta base del proyecto"""
            if getattr(sys, 'frozen', False):  # Ejecución como binario empaquetado
                return Path(sys.executable).parent
            else:  # Ejecución desde código fuente
                return Path(__file__).resolve().parent.parent.parent.parent

        def get_resource_path(self, *relative_path):
            """Obtiene la ruta absoluta a un recurso"""
            resource_path = self.base_path / "resources" / Path(*relative_path)

            # Verificar si existe
            if not resource_path.exists():
                # Intentar ruta alternativa para desarrollo
                dev_path = self.base_path.parent / "resources" / Path(*relative_path)
                if dev_path.exists():
                    return dev_path
                print(f"Recurso no encontrado: {resource_path}")
                return None

            return resource_path

        def create_widgets(self):
            # Frame principal
            main_frame = ttk.Frame(self)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Sección: Espectro de referencia
            ref_frame = ttk.LabelFrame(main_frame, text="Configuración de la referencia")
            ref_frame.pack(fill=tk.X, pady=5)
            ref_frame.columnconfigure(1, weight=1)  # Hace que la columna 1 se expanda

            ttk.Label(ref_frame, text="Espectro de referencia:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.diag = tk.Entry(ref_frame, width=30, font=("Arial", 10))
            self.diag.grid(row=0, column=1, padx=5, pady=5, sticky="we", columnspan=2)
            self.btn_load = tk.Button(ref_frame, text="Examinar...", command=self.load_reference)
            self.btn_load.grid(row=0, column=3, padx=5, pady=5, sticky="we")

            # Sección: Selección de pico
            peak_frame = ttk.Frame(ref_frame)
            peak_frame.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="we")

            ttk.Label(peak_frame, text="Desplazamiento del pico:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.peak_start = ttk.Entry(peak_frame, width=10, font=("Arial", 10))
            self.peak_start.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
            ttk.Label(peak_frame, text="a").grid(row=0, column=3, padx=5, pady=5)
            self.peak_end = ttk.Entry(peak_frame, width=10, font=("Arial", 10))
            self.peak_end.grid(row=0, column=4, padx=5, pady=5)
            ttk.Label(peak_frame, text="ppm").grid(row=0, column=5, padx=5, pady=5)

            # Sección: Parámetros de referencia
            param_frame = ttk.Frame(ref_frame)
            param_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="we")

            ttk.Label(param_frame, text="n° de protones:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.proton_count = ttk.Entry(param_frame, width=8)
            self.proton_count.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(param_frame, text="Concentración:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
            self.concentration = ttk.Entry(param_frame, width=8)
            self.concentration.grid(row=0, column=3, padx=5, pady=5)
            ttk.Label(param_frame, text="mmol/L").grid(row=0, column=4, padx=5, pady=5, sticky="w")

            # Sección: Resultados
            result_frame = ttk.Frame(ref_frame)
            result_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="we")

            ttk.Label(result_frame, text="Integral calculada:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(result_frame, textvariable=self.integral_value).grid(row=0, column=1, padx=5, pady=5, sticky="w")

            # Solo un botón para calcular todo
            ttk.Button(result_frame, text="Calcular K", command=self.calculate_factor_k).grid(
                row=1, column=0, padx=5, pady=10)
            ttk.Label(result_frame, text="K =").grid(row=1, column=1, padx=5, pady=5, sticky="w")
            ttk.Label(result_frame, textvariable=self.factor_k).grid(row=1, column=2, padx=5, pady=5, sticky="w")

            # Botón para usar este factor en la aplicación principal
            ttk.Button(main_frame, text="Usar este factor para cuantificación",
                       command=self.use_factor).pack(pady=10)

        def load_reference(self):
            file = filedialog.askopenfilename(
                title="Cargar espectro de referencia",
                filetypes=[("Archivos de espectro", "*.csv;*.txt")]
            )
            if file:
                try:
                    # Cargar el archivo en el procesador
                    self.ref_processor.load_file(file)

                    # Actualizar la interfaz
                    self.diag.delete(0, tk.END)
                    self.diag.insert(0, file)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")

        def calculate_factor_k(self):
            try:
                # Obtener los desplazamientos
                start = float(self.peak_start.get())
                end = float(self.peak_end.get())

                # Verificar que no estén vacíos
                if not start or not end:
                    messagebox.showerror("Error", "Todos los campos deben estar completos")
                    return

                # Convertir a números
                start = float(start)
                end = float(end)

                # Obtener datos del espectro
                val_x = self.ref_processor.val_x
                val_y = self.ref_processor.val_y[0]  # Solo la primera muestra

                # Encontrar índices más cercanos a los desplazamientos
                idx_start = np.argmin(np.abs(val_x - start))
                idx_end = np.argmin(np.abs(val_x - end))

                # Asegurar orden correcto
                if idx_start > idx_end:
                    idx_start, idx_end = idx_end, idx_start

                # Calcular integral
                integral = np.sum(val_y[idx_start:idx_end + 1])
                self.integral_value.set(integral)

                # Obtener otros parámetros
                protons = float(self.proton_count.get())
                concentration = float(self.concentration.get())

                if protons == 0:
                    messagebox.showerror("Error", "El número de protones no puede ser cero")
                    return

                # Calcular factor K: K = Concentración / (Integral / Número de protones)
                k_value = concentration / (integral / protons)
                self.factor_k.set(k_value)

            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos")

        def use_factor(self):
            try:
                k_value = float(self.factor_k.get())
                self.app.factor_k = k_value
                messagebox.showinfo("Éxito", f"Factor K ({k_value:.6f}) configurado para cuantificación")  #Necesario?
                self.destroy()
            except ValueError:
                messagebox.showerror("Error", "Primero calcule un factor K válido")

    class InternalStandardFrame(tk.Toplevel):
        def __init__(self, parent, app, processor):
            super().__init__(parent)
            self.title("Configuración Estándar Interno")
            self.app = app
            self.processor = processor
            self.base_path = self.get_base_path()  # Obtener la ruta base del proyecto
            icon_path = self.get_resource_path("icons", "qNMR.ico")  # Cargar el icono de la ventana
            self.iconbitmap(str(icon_path))
            self.resizable(False, False)

            # Variables para almacenar valores
            self.std_concentration = tk.DoubleVar()
            self.std_protons = tk.IntVar()
            self.file_path = tk.StringVar()
            self.k_values = {}

            self.create_widgets()

        def get_base_path(self):
            """Obtiene la ruta base del proyecto"""
            if getattr(sys, 'frozen', False):  # Ejecución como binario empaquetado
                return Path(sys.executable).parent
            else:  # Ejecución desde código fuente
                return Path(__file__).resolve().parent.parent.parent.parent

        def get_resource_path(self, *relative_path):
            """Obtiene la ruta absoluta a un recurso"""
            resource_path = self.base_path / "resources" / Path(*relative_path)

            # Verificar si existe
            if not resource_path.exists():
                # Intentar ruta alternativa para desarrollo
                dev_path = self.base_path.parent / "resources" / Path(*relative_path)
                if dev_path.exists():
                    return dev_path
                print(f"Recurso no encontrado: {resource_path}")
                return None

            return resource_path

        def create_widgets(self):
            # Frame principal
            main_frame = ttk.Frame(self)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Sección: Parámetros del estándar
            param_frame = ttk.LabelFrame(main_frame, text="Parámetros del Estándar Interno")
            param_frame.pack(fill=tk.X, pady=5)

            # Configurar expansión de columnas
            param_frame.columnconfigure(1, weight=1)

            # Concentración
            ttk.Label(param_frame, text="Concentración estándar (mM):").grid(
                row=0, column=0, padx=5, pady=5, sticky="w")
            ttk.Entry(param_frame, textvariable=self.std_concentration, width=15).grid(
                row=0, column=1, padx=5, pady=5, sticky="we")

            # Número de protones
            ttk.Label(param_frame, text="Número de protones:").grid(
                row=1, column=0, padx=5, pady=5, sticky="w")
            ttk.Entry(param_frame, textvariable=self.std_protons, width=15).grid(
                row=1, column=1, padx=5, pady=5, sticky="we")

            # Sección: Rango del pico
            peak_frame = ttk.LabelFrame(main_frame, text="Rango del pico del estándar")
            peak_frame.pack(fill=tk.X, pady=5)

            # Configurar expansión de columnas
            peak_frame.columnconfigure(1, weight=1)

            ttk.Label(peak_frame, text="Desplazamiento inicial:").grid(
                row=0, column=0, padx=5, pady=5, sticky="w")
            self.peak_start = ttk.Entry(peak_frame, width=10)
            self.peak_start.grid(row=0, column=1, padx=5, pady=5, sticky="w")

            ttk.Label(peak_frame, text="Desplazamiento final:").grid(
                row=1, column=0, padx=5, pady=5, sticky="w")
            self.peak_end = ttk.Entry(peak_frame, width=10)
            self.peak_end.grid(row=1, column=1, padx=5, pady=5, sticky="w")

            # Sección: Resultados
            result_frame = ttk.LabelFrame(main_frame, text="Resultados")
            result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

            # Treeview para mostrar K por muestra
            columns = ("Muestra", "K")
            self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=8)

            # Configurar columnas
            self.tree.heading("Muestra", text="Muestra")
            self.tree.column("Muestra", width=150, anchor="w")
            self.tree.heading("K", text="Factor K")
            self.tree.column("K", width=150, anchor="center")

            # Scrollbar
            scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)

            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Botones
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=10)

            ttk.Button(btn_frame, text="Calcular K para todas las muestras",
                       command=self.calculate_k_all).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Usar estos factores",
                       command=self.use_factors).pack(side=tk.RIGHT, padx=5)

        def calculate_k_all(self):
            """Calcula K para todas las muestras usando el estándar interno"""
            try:
                # Obtener parámetros
                conc = float(self.std_concentration.get())
                protons = int(self.std_protons.get())
                start = float(self.peak_start.get())
                end = float(self.peak_end.get())

                if protons <= 0:
                    raise ValueError("Número de protones debe ser positivo")

            # VERIFICACIÓN CORREGIDA (usa hasattr y verifica muestras)
                if not hasattr(self.processor, 'muestras') or not self.processor.muestras:
                    messagebox.showerror("Error", "Primero cargue un set de datos en la aplicación principal")
                    return

                # Limpiar resultados previos
                self.k_values = {}
                self.tree.delete(*self.tree.get_children())

                # Para cada muestra
                for muestra in self.processor.muestras:
                    # Obtener índice de la muestra
                    idx = self.processor.muestras.index(muestra)

                    # Obtener datos de la muestra
                    val_x = self.processor.val_x
                    val_y = self.processor.val_y[idx]

                    # Encontrar índices para el rango del estándar
                    idx_start = np.argmin(np.abs(val_x - start))
                    idx_end = np.argmin(np.abs(val_x - end))

                    if idx_start > idx_end:
                        idx_start, idx_end = idx_end, idx_start

                    # Calcular integral del estándar en esta muestra
                    integral_std = np.sum(val_y[idx_start:idx_end + 1])

                    # Calcular K para esta muestra
                    # K = Concentración / (Integral / Protones)
                    k_value = conc / (integral_std / protons)

                    # Guardar K para esta muestra
                    self.k_values[muestra] = k_value

                    # Añadir a la tabla
                    self.tree.insert("", "end", values=(muestra, f"{k_value:.6f}"))

                #messagebox.showinfo("Éxito", "Factores K calculados para todas las muestras")

            except ValueError as e:
                messagebox.showerror("Error", f"Datos inválidos: {str(e)}")

        def use_factors(self):
            """Guarda los factores K en la aplicación principal"""
            if not self.k_values:
                messagebox.showerror("Error", "Primero calcule los factores K")
                return

            self.app.k_values = self.k_values
            messagebox.showinfo("Éxito", "Factores K configurados para cuantificación")
            self.destroy()

    def mostrar_integrales(self, event=None):
        """Muestra las integrales absolutas calculadas en una ventana"""
        integrales_df = self.processor.get_integrales()
        if integrales_df.empty:
            messagebox.showinfo("Información", "No hay integrales calculadas")
            return
        self._mostrar_tabla(integrales_df.round(4), "Tabla de Integrales Absolutas")##########

    def _mostrar_tabla(self, df, title):
        """Función auxiliar para mostrar cualquier DataFrame en una tabla"""
        int_wind = tk.Toplevel(self.raiz)
        int_wind.title(title)
        self.base_path = self.get_base_path()  # Obtener la ruta base del proyecto
        icon_path = self.get_resource_path("icons", "qNMR.ico")  # Cargar el icono de la ventana
        int_wind.iconbitmap(str(icon_path))
        int_wind.geometry("650x350")

        # Crear Treeview
        tree_frame = ttk.Frame(int_wind)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # CORRECCIÓN: Crear el Treeview con las columnas apropiadas
        tree = ttk.Treeview(tree_frame, columns=("muestra",) + tuple(df.columns), show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # CORRECCIÓN: Configurar columnas correctamente
        tree.heading("muestra", text="Muestra")
        tree.column("muestra", width=150, anchor="w")

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        # CORRECCIÓN: Insertar datos con los nombres de muestra
        for idx, row in df.iterrows():
            tree.insert("", "end", values=(idx,) + tuple(row))

    def nuevo(self, event=None):
        """Reinicia la aplicación"""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        self.processor.reset()

    def acerca(self):
        """Muestra información acerca de la aplicación"""
        messagebox.showinfo("Acerca de", "iRMN - Herramienta de análisis de espectros\nVersión 1.0")

    def salir(self, event=None):
        """Cierra la aplicación"""
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.raiz.quit()
            self.raiz.destroy()

    def on_close(self, event=None):
        """Maneja el cierre de la ventana"""
        self.salir()
