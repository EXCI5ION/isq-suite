import os
import sys
from pathlib import Path

def resource_path(relative_path):
    """Obtiene la ruta absoluta a los recursos (misma función que en launcher)"""
    try:
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).parent
        else:
            base_path = Path(__file__).resolve().parent.parent.parent.parent
    except Exception:
        base_path = Path.cwd()
    
    if isinstance(relative_path, str):
        relative_path = Path(relative_path)
    
    paths_to_try = [
        base_path / relative_path,
        base_path / "resources" / relative_path,
        base_path / "src" / "suite" / "resources" / relative_path,
        base_path / "src" / relative_path,
        base_path / ".." / "resources" / relative_path
    ]
    
    for path in paths_to_try:
        if path.exists():
            return str(path)
    
    print(f"[ADVERTENCIA] Recurso no encontrado: {relative_path}")
    return str(paths_to_try[0])

# Configuración crítica: Agregar ruta base al PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Diagnóstico (puedes comentar después de pruebas)
print("\n=== SYS PATH ===")
for p in sys.path:
    print(p)

if __name__ == "__main__":
    try:
        # Importar después de configurar el path
        from src.suite.gui.q_app import QuantifyApp
        
        # Obtener ruta del ícono
        icon_path = resource_path("icons/qNMR.ico")
        print(f"Usando ícono en: {icon_path}")
        
        # Iniciar aplicación principal
        app = QuantifyApp(icon_path)
        app.run()
    except ImportError as e:
        print(f"Error de importación: {str(e)}")
        # Mostrar estructura de directorios para diagnóstico
        print("\n=== DIRECTORIO ACTUAL ===")
        for root, dirs, files in os.walk('.'):
            for file in files:
                print(os.path.join(root, file))
        # Re-lanzar excepción para ver traza completa
        raise
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        raise
