from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import tkinter as tk
import subprocess
import sys
import os

def main():
    root = tk.Tk()
    app = SuiteApp(root)
    root.mainloop()

class SuiteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ISQ Suite")
        self.root.geometry("500x200")
        self.root.resizable(False, False)
        
        # Obtener la ruta base correcta para recursos
        self.base_path = self.get_base_path()
        
        # Cargar el icono de la ventana
        icon_path = self.resource_path("icons/ISQ.ico")
        if icon_path and os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        self.app_icons = []
        self.create_widgets()
        self.center_window()
    
    def get_base_path(self):
        """Obtiene la ruta base correcta según el entorno"""
        if getattr(sys, 'frozen', False):  # Ejecución como binario empaquetado
            return Path(sys.executable).parent
        else:  # Ejecución desde código fuente
            return Path(__file__).resolve().parent.parent.parent
    
    def resource_path(self, relative_path):
        """Convierte una ruta relativa a una ruta absoluta válida para PyInstaller"""
        try:
            # PyInstaller crea una carpeta temporal en _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        # Primero intentar en la ruta de recursos empaquetados
        packaged_path = os.path.join(base_path, relative_path)
        if os.path.exists(packaged_path):
            return packaged_path
        
        # Luego intentar en la ruta base del proyecto
        project_path = os.path.join(self.base_path, "resources", relative_path)
        if os.path.exists(project_path):
            return project_path
        
        # Finalmente intentar en la estructura de desarrollo alternativa
        dev_path = os.path.join(self.base_path.parent, "resources", relative_path)
        if os.path.exists(dev_path):
            return dev_path
        
        print(f"Recurso no encontrado: {relative_path}")
        return None

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def create_widgets(self):
        """Crea la interfaz de la suite con botones que son imágenes de íconos"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            main_frame,
            text="Bienvenido a la Suite de Procesamiento ISQ",
            font=("Times", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        apps_frame = ttk.Frame(main_frame)
        apps_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        app_config = [
            {"name": "iRMN", "app": "inmr", "icon": "iNMR.ico"},
            {"name": "sNMR", "app": "snmr", "icon": "sNMR.ico"},
            {"name": "qNMR", "app": "qnmr", "icon": "qNMR.ico"}
        ]

        for app in app_config:
            app_frame = ttk.Frame(apps_frame, padding=10)
            app_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=15)

            icon_path = self.resource_path(f"icons/{app['icon']}")
            if icon_path and os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    base_size = 64
                    img.thumbnail((base_size, base_size))
                    
                    icon = ImageTk.PhotoImage(img)
                    self.app_icons.append(icon)
                    
                    app_btn = tk.Button(
                        app_frame,
                        image=icon,
                        command=lambda a=app['app']: self.launch_app(a),
                        borderwidth=1,
                        relief="flat",
                        bg="#f0f0f0",
                        activebackground="#e0e0e0"
                    )
                    app_btn.pack(pady=(0, 5))
                    
                    app_label = ttk.Label(
                        app_frame,
                        text=app["name"],
                        font=("Arial", 10, "bold"),
                        justify=tk.CENTER
                    )
                    app_label.pack()
                except Exception as e:
                    print(f"Error cargando ícono: {str(e)}")
                    self.create_text_button(app_frame, app)
            else:
                print(f"Ícono no encontrado: {icon_path}")
                self.create_text_button(app_frame, app)

    def create_text_button(self, parent, app):
        """Crea un botón de texto como alternativa"""
        app_btn = ttk.Button(
            parent,
            text=app["name"],
            command=lambda a=app['app']: self.launch_app(a),
            width=15
        )
        app_btn.pack(pady=(0, 10))

    def launch_app(self, app_name):
        """Lanza la aplicación seleccionada por su nombre corto"""
        try:
            # Determinar el nombre del ejecutable según la plataforma
            executable = f"isq-{app_name}"
            if sys.platform == "win32":
                executable += ".exe"
            
            # Ruta base donde buscar los ejecutables
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.join(self.base_path, "dist")
            
            app_path = os.path.join(base_dir, executable)
            
            if not os.path.exists(app_path):
                # Segunda opción: buscar en el mismo directorio que el launcher
                app_path = os.path.join(os.path.dirname(sys.executable), executable)
                
            if os.path.exists(app_path):
                subprocess.Popen([app_path])
            else:
                messagebox.showerror(
                    "Error", 
                    f"No se encontró el ejecutable para {app_name}:\n{app_path}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n{str(e)}")


if __name__ == "__main__":
    main()
