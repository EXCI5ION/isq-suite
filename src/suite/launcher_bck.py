from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import tkinter as tk
import subprocess
import sys
import os


class SuiteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ISQ Suite")
        self.root.geometry("600x250")
        self.root.resizable(False, False)

        # Obtener la ruta base del proyecto
        self.base_path = self.get_base_path()

        # Cargar el icono de la ventana
        icon_path = self.get_resource_path("icons", "iNMR.ico")
        if icon_path and icon_path.exists():
            self.root.iconbitmap(str(icon_path))
        else:
            print(f"Advertencia: No se encontró el ícono principal en {icon_path}")

        self.app_icons = []  # Lista para mantener las referencias de las imágenes

        self.create_widgets()
        self.center_window()
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def get_base_path(self):
        """Obtiene la ruta base del proyecto"""
        if getattr(sys, 'frozen', False):  # Ejecución como binario empaquetado
            return Path(sys.executable).parent
        else:  # Ejecución desde código fuente
            return Path(__file__).resolve().parent.parent.parent

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

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def create_widgets(self):
        """Crea la interfaz de la suite con botones horizontales e íconos .ico"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="Bienvenido a la Suite de Aplicaciones ISQ",
            font=("Times", 14, "bold")
        )
        title_label.pack(pady=(0, 30))

        # Frame para contener las aplicaciones (horizontal)
        apps_frame = ttk.Frame(main_frame)
        apps_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Configuración de las aplicaciones
        app_config = [
            {
                "name": "iRMN",
                "module": "apps.inmr.maini",  # Usar módulo en lugar de archivo
                "icon": "iNMR.ico"
            },
            {
                "name": "sNMR",
                "module": "apps.snmr.mains",
                "icon": "SNMR.ico"
            },
            {
                "name": "qNMR",
                "module": "apps.qnmr.mainq",
                "icon": "qNMR.ico"
            }
        ]

        # Crear contenedores para cada aplicación
        for app in app_config:
            app_frame = ttk.Frame(apps_frame, padding=10)
            app_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=15)

            # Obtener ruta al ícono
            icon_path = self.get_resource_path("icons", app["icon"])

            if icon_path and icon_path.exists():
                try:
                    # Cargar imagen con Pillow
                    img = Image.open(icon_path)

                    # Convertir a modo RGBA para mantener transparencia
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')

                    # Redimensionar manteniendo relación de aspecto
                    base_size = 64
                    img.thumbnail((base_size, base_size), Image.LANCZOS)

                    # Crear imagen Tkinter-compatible
                    icon = ImageTk.PhotoImage(img)

                    # Guardar referencia para evitar garbage collection
                    self.app_icons.append(icon)

                    # Crear etiqueta para mostrar el ícono
                    icon_label = ttk.Label(app_frame, image=icon)
                    icon_label.image = icon  # Mantener referencia
                    icon_label.pack(pady=(0, 5))

                except Exception as e:
                    print(f"No se pudo cargar ícono para {app['name']}: {str(e)}")
            else:
                print(f"Ícono no encontrado para {app['name']}: {app['icon']}")

            # Botón para la aplicación
            app_btn = ttk.Button(
                app_frame,
                text=app["name"],
                command=lambda m=app["module"]: self.launch_app(m),
                width=15
            )
            app_btn.pack(pady=(0, 5))

    def launch_app(self, app_module):
        """Lanza la aplicación seleccionada como módulo Python"""
        try:
            # Usa el ejecutable de Python actual para lanzar la aplicación
            python_exec = sys.executable

            # Construir el comando para ejecutar el módulo
            command = [python_exec, "-m", app_module]

            # En desarrollo, configurar PYTHONPATH
            env = os.environ.copy()
            if not getattr(sys, 'frozen', False):
                env["PYTHONPATH"] = str(self.base_path) + os.pathsep + env.get("PYTHONPATH", "")

            # Lanzar la aplicación en un nuevo proceso
            subprocess.Popen(command, env=env)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SuiteApp(root)
    root.mainloop()
