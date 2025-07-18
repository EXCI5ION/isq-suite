import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from suite.utils import get_resource_path
from PIL import Image, ImageTk
from pathlib import Path


class SuiteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ISQ Suite")
        self.root.geometry("500x200")
        self.root.resizable(False, False)
        
        # Cargar icono de la ventana
        icon_path = get_resource_path("icons/ISQ.ico")
        self.root.iconbitmap(icon_path)
        if icon_path and os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"Error cargando ícono de ventana: {str(e)}")
        else:
            print(f"Ícono de ventana no encontrado: {icon_path}")
        
        self.app_icons = []  # Para mantener referencias a imágenes
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def create_widgets(self):
        """Crea la interfaz con botones de íconos para cada aplicación"""
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

        # Configuración de aplicaciones disponibles
        app_config = [
            {"name": "iNMR", "app": "iNMR", "icon": "iNMR.ico"},
            {"name": "sNMR", "app": "sNMR", "icon": "sNMR.ico"},
            {"name": "qNMR", "app": "qNMR", "icon": "qNMR.ico"}
        ]

        for app in app_config:
            app_frame = ttk.Frame(apps_frame, padding=10)
            app_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=15)

            icon_path = get_resource_path(f"icons/{app['icon']}")
            if icon_path and os.path.exists(icon_path):
                try:
                    # Cargar y procesar imagen
                    img = Image.open(icon_path)
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    img.thumbnail((64, 64))
                    icon = ImageTk.PhotoImage(img)
                    self.app_icons.append(icon)  # Mantener referencia
                    
                    # Crear botón con imagen
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
                    
                    # Etiqueta con nombre de la aplicación
                    app_label = ttk.Label(
                        app_frame,
                        text=app["name"],
                        font=("Arial", 10, "bold"),
                        justify=tk.CENTER
                    )
                    app_label.pack()
                except Exception as e:
                    print(f"Error procesando ícono: {str(e)}")
                    self.create_text_button(app_frame, app)
            else:
                print(f"Ícono no encontrado: {icon_path}")
                self.create_text_button(app_frame, app)

    def create_text_button(self, parent, app):
        """Crea un botón de texto cuando no hay ícono disponible"""
        app_btn = ttk.Button(
            parent,
            text=app["name"],
            command=lambda a=app['app']: self.launch_app(a),
            width=15
        )
        app_btn.pack(pady=(0, 10))

    def launch_app(self, app_name):
        """Inicia la aplicación seleccionada"""
        try:
            # Determinar rutas según el entorno
            if getattr(sys, 'frozen', False):
                # Modo empaquetado
                base_dir = Path(sys.executable).parent
                app_path = base_dir / app_name / f"{app_name}.exe"
                
                # Fallback: Buscar en dist/
                if not app_path.exists():
                    app_path = base_dir / "dist" / app_name / f"{app_name}.exe"
            else:
                # Modo desarrollo
                base_dir = Path(__file__).resolve().parent.parent.parent
                app_path = base_dir / "dist" / app_name / app_name
                if sys.platform == "win32":
                    app_path = app_path.with_suffix(".exe")
            
            # Verificar existencia y ejecutar
            if app_path.exists():
                # Configurar entorno para las dependencias
                env = os.environ.copy()
                env["PYTHONPATH"] = str(base_dir) + os.pathsep + env.get("PYTHONPATH", "")
                
                subprocess.Popen([str(app_path)], env=env)
            else:
                messagebox.showerror(
                    "Error", 
                    f"Ejecutable no encontrado:\n{app_path}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n{str(e)}")

def run():
    """Función principal para iniciar la aplicación"""
    root = tk.Tk()
    app = SuiteApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Diagnóstico inicial (opcional)
    print("=== Entorno de ejecución ===")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"Base path: {Path(__file__).resolve().parent.parent.parent}")
    
    run()
