import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.suite.core.handler import load_nmr_data, save_processed_data
from src.suite.core.trnsf import transform
from src.suite.core.norm import normalize
from src.suite.core.scaling import scale
from pathlib import Path
import numpy as np
import sys


class ScalingApp:
    def __init__(self):
        self.raiz = tk.Tk()
        self.raiz.title("sNMR")
        self.raiz.geometry("375x450")
        self.raiz.resizable(False, False)
        self.base_path = self.get_base_path()  # Obtener la ruta base del proyecto
        icon_path = self.get_resource_path("icons", "sNMR.ico")  # Cargar el icono de la ventana
        self.raiz.iconbitmap(str(icon_path))

        # Variables de datos
        self.ppm = None
        self.data = None
        self.processed_data = None
        self.sample_names = None

        # Variables de control
        self.file_path = tk.StringVar()
        self.transform_method = tk.StringVar(value="ninguna")
        self.norm_method = tk.StringVar(value="ninguna")
        self.scale_method = tk.StringVar(value="ninguna")
        self.ref_ppm_min = tk.DoubleVar(value=0.0)
        self.ref_ppm_max = tk.DoubleVar(value=0.0)
        self.glog_lambda = tk.DoubleVar(value=1.0)

        # Crear interfaz
        self.create_widgets()
        self.create_menu()
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

    def create_widgets(self):
        # 1. Sección de archivo
        file_frame = ttk.LabelFrame(self.raiz, text="Ingrese su set de datos")
        file_frame.pack(pady=10, padx=20, fill="x")

        ttk.Entry(file_frame, textvariable=self.file_path, width=40).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Examinar...", command=self.browse_file).pack(side="right", padx=5)

        # 2. Sección de transformación
        trans_frame = ttk.LabelFrame(self.raiz, text="Transformación")
        trans_frame.pack(pady=10, padx=20, fill="x")

        ttk.Radiobutton(trans_frame, text="Ninguna", variable=self.transform_method, value="ninguna").pack(anchor="w")
        ttk.Radiobutton(trans_frame, text="Logarítmica", variable=self.transform_method, value="log").pack(anchor="w")
        rb_glog = ttk.Radiobutton(trans_frame, text="Generalized Log (glog)",
                                  variable=self.transform_method, value="glog")
        rb_glog.pack(anchor="w")

        # Frame para parámetro glog
        self.glog_frame = ttk.Frame(trans_frame)
        ttk.Label(self.glog_frame, text="λ value:").pack(side="left")
        ttk.Entry(self.glog_frame, textvariable=self.glog_lambda, width=8).pack(side="left")
        self.glog_frame.pack_forget()  # Ocultar inicialmente

        # 3. Sección de normalización
        norm_frame = ttk.LabelFrame(self.raiz, text="Normalización")
        norm_frame.pack(pady=10, padx=20, fill="x")

        methods = ["Ninguna", "Área Total", "PQN", "Vector Unitario", "Estándar Interno"]
        norm_combo = ttk.Combobox(norm_frame, textvariable=self.norm_method, values=methods, state="readonly")
        norm_combo.pack(fill="x", padx=5, pady=5)
        norm_combo.bind("<<ComboboxSelected>>", self.toggle_norm_params)

        # Frame para parámetros de estándar interno
        self.ref_frame = ttk.Frame(norm_frame)
        ttk.Label(self.ref_frame, text="Región referencia:").pack(side="left")
        ttk.Entry(self.ref_frame, textvariable=self.ref_ppm_min, width=8).pack(side="left")
        ttk.Label(self.ref_frame, text="a").pack(side="left")
        ttk.Entry(self.ref_frame, textvariable=self.ref_ppm_max, width=8).pack(side="left")
        ttk.Label(self.ref_frame, text="ppm").pack(side="left")
        self.ref_frame.pack_forget()  # Ocultar inicialmente

        # 4. Sección de escalado
        scale_frame = ttk.LabelFrame(self.raiz, text="Escalado")
        scale_frame.pack(pady=10, padx=20, fill="x")

        scale_methods = ["Ninguno", "Autoescalado", "Pareto", "Rango"]
        scale_combo = ttk.Combobox(scale_frame, textvariable=self.scale_method, values=scale_methods, state="readonly")
        scale_combo.pack(fill="x", padx=5, pady=5)

        # 5. Botón de procesamiento
        ttk.Button(self.raiz, text="PROCESAR", command=self.process_data, style="Accent.TButton").pack(pady=20)

        # Estilo para botón destacado
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="black", background="#4CAF50", font=("Arial", 10, "bold"))

    def create_menu(self):
        """Crea el menú principal de la aplicación"""
        bm = tk.Menu(self.raiz)
        self.raiz.config(menu=bm)
        archivo = tk.Menu(bm, tearoff=0)
        ayuda = tk.Menu(bm, tearoff=0)

        bm.add_cascade(label="Archivo", menu=archivo)
        bm.add_cascade(label="Ayuda", menu=ayuda)

        archivo.add_command(label="Nuevo", command=self.nuevo, accelerator="Ctrl+N")
        archivo.add_command(label="Guardar", command=self.guardar, accelerator="Ctrl+S")
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.salir, accelerator="Alt+F4")

        ayuda.add_command(label="Acerca de...", command=self.acerca, accelerator="")

        self.raiz.bind("<Control-n>", self.nuevo)
        self.raiz.bind("<Control-s>", self.guardar)
        self.raiz.bind("<Alt-F4>", self.salir)

    def toggle_norm_params(self, event=None):
        """Muestra u oculta los parámetros según la selección actual"""
        # Mostrar/ocultar parámetros de estándar interno
        if self.norm_method.get() == "Estándar Interno":
            self.ref_frame.pack(pady=5, fill="x")
        else:
            self.ref_frame.pack_forget()

        # Mostrar/ocultar parámetro glog
        if self.transform_method.get() == "glog":
            self.glog_frame.pack(pady=5, fill="x")
        else:
            self.glog_frame.pack_forget()

    def browse_file(self):
        """Abre un diálogo para seleccionar un archivo de datos"""
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.file_path.set(filename)
            try:
                # Cargar y validar los datos
                self.ppm, self.data, self.sample_names = load_nmr_data(filename)
                messagebox.showinfo("Éxito", "Datos cargados correctamente!")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar los datos:\n{str(e)}")

    def process_data(self):
        """Procesa los datos según las opciones seleccionadas"""
        if not self.file_path.get():
            messagebox.showerror("Error", "Por favor, seleccioné un archivo primero.")
            return

        if self.data is None:
            messagebox.showerror("Error", "No hay datos cargados para procesar.")
            return

        try:
            # Copiar los datos para procesamiento
            processed_data = self.data.copy()

            # 1. Verificar y limpiar datos antes de procesar
            if np.isnan(processed_data).any():
                # Reemplazar NaNs por 0 con advertencia
                nan_count = np.isnan(processed_data).sum()
                processed_data = np.nan_to_num(processed_data, nan=0.0)
                messagebox.showwarning(
                    "Advertencia",
                    f"Se encontraron {nan_count} valores NaN en los datos. Se reemplazaron por 0."
                )

            # 2. Aplicar transformación
            transform_method = self.transform_method.get()
            if transform_method != "ninguna":
                transform_kwargs = {}
                if transform_method == "glog":
                    transform_kwargs["lambda_val"] = self.glog_lambda.get()

                processed_data = transform(processed_data, method=transform_method, **transform_kwargs)

            # 3. Aplicar normalización
            norm_method = self.norm_method.get()
            if norm_method != "Ninguna":
                norm_kwargs = {}
                if norm_method == "Estándar Interno":
                    norm_kwargs["ppm"] = self.ppm
                    norm_kwargs["ppm_min"] = self.ref_ppm_min.get()
                    norm_kwargs["ppm_max"] = self.ref_ppm_max.get()

                # Para normalización por área total, escalar a 100
                if norm_method == "Área Total":
                    norm_kwargs["scale_to"] = 100.0

                # Mapear nombres de métodos
                method_map = {
                    "Área Total": "total_area",
                    "PQN": "pqn",
                    "Vector Unitario": "vector",
                    "Estándar Interno": "internal_standard"
                }
                processed_data = normalize(
                    processed_data,
                    method=method_map[norm_method],
                    **norm_kwargs
                )

            # 4. Aplicar escalado
            scale_method = self.scale_method.get()
            if scale_method != "Ninguno":
                # Mapear nombres de métodos
                method_map = {
                    "Autoescalado": "auto",
                    "Pareto": "pareto",
                    "Rango": "range"
                }
                scale_kwargs = {}
                if scale_method == "Rango":
                    scale_kwargs["feature_range"] = (0, 1)

                processed_data = scale(
                    processed_data,
                    method=method_map[scale_method],
                    **scale_kwargs
                )

            # Guardar los datos procesados
            self.processed_data = processed_data
            messagebox.showinfo("Éxito", "Procesamiento completado correctamente!")

        except Exception as e:
            messagebox.showerror("Error", f"Error durante el procesamiento:\n{str(e)}")

    def nuevo(self, event=None):
        """Reinicia la aplicación a su estado inicial"""
        self.file_path.set("")
        self.transform_method.set("ninguna")
        self.norm_method.set("ninguna")
        self.scale_method.set("ninguna")
        self.ref_ppm_min.set(0.0)
        self.ref_ppm_max.set(0.0)
        self.glog_lambda.set(1.0)
        self.ppm = None
        self.data = None
        self.processed_data = None
        self.sample_names = None
        self.toggle_norm_params()  # Actualizar la UI
        messagebox.showinfo("Nuevo", "Configuración reiniciada. Puede cargar un nuevo archivo.")

    def guardar(self, event=None):
        """Guarda los datos procesados"""
        if self.processed_data is None:
            messagebox.showerror("Error", "No hay datos procesados para guardar.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Guardar datos procesados"
        )

        if filename:
            try:
                save_processed_data(
                    filename,
                    self.ppm,
                    self.processed_data,
                    self.sample_names
                )
                messagebox.showinfo("Éxito", f"Datos guardados en:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar los datos:\n{str(e)}")

    def acerca(self):
        """Muestra información acerca de la aplicación"""
        messagebox.showinfo("Acerca de",
                            "iRMN - Herramienta de análisis de espectros\n\n"
                            "Versión 1.0\n"
                            "Desarrollado para procesamiento de datos de RMN\n"
                            "© 2023 Todos los derechos reservados")

    def salir(self, event=None):
        """Cierra la aplicación"""
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.raiz.quit()
            self.raiz.destroy()

    def on_close(self, event=None):
        """Maneja el cierre de la ventana"""
        self.salir()
