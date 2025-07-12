import os
import sys
from win32com.client import Dispatch

def crear_acceso(target, name, icono, menu_inicio=True):
    # Configurar rutas
    escritorio = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    menu = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
    
    # Crear acceso en escritorio
    acceso_escritorio = os.path.join(escritorio, f"{name}.lnk")
    shell = Dispatch('WScript.Shell')
    acceso = shell.CreateShortCut(acceso_escritorio)
    acceso.TargetPath = target
    acceso.IconLocation = icono
    acceso.save()
    
    # Crear acceso en menú inicio
    if menu_inicio:
        acceso_menu = os.path.join(menu, f"{name}.lnk")
        acceso = shell.CreateShortCut(acceso_menu)
        acceso.TargetPath = target
        acceso.IconLocation = icono
        acceso.save()

if __name__ == "__main__":
    # Ruta donde se instaló el programa
    base_dir = sys.prefix
    
    # Directorio de ejecutables
    bin_dir = os.path.join(base_dir, "Scripts")
    
    # Directorio de iconos
    icon_dir = os.path.join(base_dir, "resources", "icons")
    
    # Crear accesos para la suite completa
    crear_acceso(
        os.path.join(bin_dir, "rmn-suite.exe"),
        "ISQ Suite",
        os.path.join(icon_dir, "ISQ.ico")
    )
    
    # Crear accesos para programas individuales
    programas = [
        ("rmn-inmr.exe", "iNMR", "iNMR.ico"),
        ("rmn-qnmr.exe", "qNMR", "qNMR.ico"),
        ("rmn-snmr.exe", "sNMR", "sNMR.ico")
    ]
    
    for exe, nombre, icono in programas:
        crear_acceso(
            os.path.join(bin_dir, exe),
            nombre,
            os.path.join(icon_dir, icono)
        )