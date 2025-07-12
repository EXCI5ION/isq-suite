from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.suite.core.processor import RMNProcessor
from tkinter import ttk, messagebox, filedialog
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
from pathlib import Path
import tkinter as tk
import pandas as pd
import sys


class MainApp:
    def __init__(self):
        self.raiz = tk.Tk()
        self.raiz.title("iNMR")
        self.raiz.resizable(True, True)
        self.base_path = self.get_base_path()  # Obtener la ruta base del proyecto
        icon_path = self.get_resource_path("icons", "iNMR.ico")  # Cargar el icono de la ventana
        self.raiz.iconbitmap(str(icon_path))
        self.raiz.geometry("854x480")
        self.processor = RMNProcessor()

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

    def create_menu(self):
        bm = tk.Menu(self.raiz)
        self.raiz.config(menu=bm)
        archivo = tk.Menu(bm, tearoff=0)
        herramientas = tk.Menu(bm, tearoff=0)
        ayuda = tk.Menu(bm, tearoff=0)

        bm.add_cascade(label="Archivo", menu=archivo)
        bm.add_cascade(label="Herramientas", menu=herramientas)
        bm.add_cascade(label="Ayuda", menu=ayuda)

        archivo.add_command(label="Nuevo", command=self.nuevo, accelerator="Ctrl+N")
        archivo.add_command(label="Abrir", command=self.abrir, accelerator="Ctrl+O")
        archivo.add_command(label="Guardar absolutas", command=self.guardar_absolutas, accelerator="Ctrl+G")
        archivo.add_command(label="Guardar relativas", command=self.guardar_relativas, accelerator="Ctrl+S")
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.salir, accelerator="Alt+F4")
        herramientas.add_command(label="Seleccionar", command=self.seleccionar, accelerator="z")
        herramientas.add_command(label="Mostrar absolutas", command=self.mostrar_integrales, accelerator="m")
        herramientas.add_command(label="Mostrar relativas", command=self.mostrar_integrales_relativas, accelerator="r")
        herramientas.add_command(label="Mostrar totales", command=self.mostrar_totales, accelerator="t")

        ayuda.add_command(label="Acerca de...", command=self.acerca, accelerator="")

        self.raiz.bind("<Control-n>", self.nuevo)
        self.raiz.bind("<Control-o>", self.abrir)
        self.raiz.bind("<Control-s>", self.guardar_absolutas)
        self.raiz.bind("<Control-s>", self.guardar_relativas)
        self.raiz.bind("<m>", self.mostrar_integrales)
        self.raiz.bind("<r>", self.mostrar_integrales_relativas)
        self.raiz.bind("<t>", self.mostrar_totales)
        self.raiz.bind("<Alt-F4>", self.salir)

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

    def mostrar_integrales(self, event=None):
        """Muestra las integrales absolutas calculadas en una ventana"""
        integrales_df = self.processor.get_integrales()
        if integrales_df.empty:
            messagebox.showinfo("Información", "No hay integrales calculadas")
            return
        self._mostrar_tabla(integrales_df.round(4), "Tabla de Integrales Absolutas")

    def mostrar_integrales_relativas(self, event=None):
        """Muestra las integrales relativas en una ventana"""
        relativas_df = self.processor.calcular_integrales_relativas()
        if relativas_df.empty:
            messagebox.showinfo("Información", "No hay integrales para calcular relativas")
            return
        self._mostrar_tabla(relativas_df, "Tabla de Integrales Relativas")

    def mostrar_totales(self, event=None):
        """Muestra las integrales totales de cada muestra"""
        totales_series = self.processor.get_integrales_totales()
        if totales_series is None:
            messagebox.showinfo("Información", "No se han calculado las integrales totales")
            return

        # Convertir Series a DataFrame para usar _mostrar_tabla
        totales_df = pd.DataFrame(totales_series)
        self._mostrar_tabla(totales_df, "Integrales Totales")

    def _mostrar_tabla(self, df, title):
        """Función auxiliar para mostrar cualquier DataFrame en una tabla"""
        int_wind = tk.Toplevel(self.raiz)
        int_wind.title(title)
        self.base_path = self.get_base_path()  # Obtener la ruta base del proyecto
        icon_path = self.get_resource_path("icons", "iNMR.ico")  # Cargar el icono de la ventana
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

    def guardar_absolutas(self, event=None):
        """Guarda las integrales en un archivo"""
        integrales_df = self.processor.get_integrales()
        if integrales_df.empty:
            messagebox.showinfo("Información", "No hay integrales para guardar")
            return

        destino = filedialog.asksaveasfilename(
            title="Guardar integrales",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if destino:
            try:
                integrales_df.round(4).to_csv(destino)
                messagebox.showinfo("Éxito", f"Integrales guardadas en:\n{destino}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron guardar las integrales:\n{str(e)}")

    def guardar_relativas(self, event=None):
        """Guarda las integrales en un archivo"""
        relativas_df = self.processor.calcular_integrales_relativas()
        if relativas_df.empty:
            messagebox.showinfo("Información", "No hay integrales para guardar")
            return

        destino = filedialog.asksaveasfilename(
            title="Guardar integrales",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if destino:
            try:
                relativas_df.to_csv(destino)
                messagebox.showinfo("Éxito", f"Integrales guardadas en:\n{destino}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron guardar las integrales:\n{str(e)}")

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
