import sys
import os

def get_resource_path(relative_path):
    """Retorna el path absoluto al recurso, detectando si la app está congelada (freezada) o no."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
    return os.path.join(base_path, relative_path)
