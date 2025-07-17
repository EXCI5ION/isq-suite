import os
import sys
import platform
import subprocess
from pathlib import Path

def create_windows_shortcuts():
    try:
        import win32com.client
        from win32com.client import Dispatch
    except ImportError:
        print("pywin32 not available. Skipping Windows shortcut creation.")
        return

    desktop = Path.home() / "Desktop"
    start_menu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "ISQ Suite"

    # Crear carpeta en el menú de inicio
    start_menu.mkdir(parents=True, exist_ok=True)

    # Crear accesos directos
    apps = [
        ("ISQ Suite", "isq-suite.exe"),
        ("iNMR", "isq-inmr.exe"),
        ("qNMR", "isq-qnmr.exe"),
        ("sNMR", "isq-snmr.exe"),
    ]

    shell = win32com.client.Dispatch("WScript.Shell")
    for name, exe in apps:
        # Acceso directo en el menú de inicio
        shortcut = shell.CreateShortcut(str(start_menu / f"{name}.lnk"))
        shortcut.TargetPath = str(Path(sys.prefix) / "Scripts" / exe)
        shortcut.WorkingDirectory = str(Path.home())
        shortcut.Save()

        # Acceso directo en el escritorio (opcional)
        desktop_shortcut = shell.CreateShortcut(str(desktop / f"{name}.lnk"))
        desktop_shortcut.TargetPath = str(Path(sys.prefix) / "Scripts" / exe)
        desktop_shortcut.WorkingDirectory = str(Path.home())
        desktop_shortcut.Save()

def create_linux_shortcuts():
    # Crear archivos .desktop en ~/.local/share/applications
    applications_dir = Path.home() / ".local" / "share" / "applications"
    applications_dir.mkdir(parents=True, exist_ok=True)

    apps = [
        ("ISQ Suite", "isq-suite", "ISQ.ico"),
        ("iNMR", "isq-inmr", "iNMR.ico"),
        ("qNMR", "isq-qnmr", "qNMR.ico"),
        ("sNMR", "isq-snmr", "sNMR.ico"),
    ]

    for name, exec_name, icon in apps:
        desktop_file = applications_dir / f"{name}.desktop"
        with open(desktop_file, "w") as f:
            f.write(f"""[Desktop Entry]
Name={name}
Exec={exec_name}
Icon={Path(sys.prefix) / 'resources' / 'icons' / icon}
Terminal=false
Type=Application
""")

def create_macos_shortcuts():
    # En macOS, crear aplicaciones en ~/Applications
    applications_dir = Path.home() / "Applications" / "ISQ Suite"
    applications_dir.mkdir(parents=True, exist_ok=True)

    apps = [
        ("ISQ Suite", "isq-suite"),
        ("iNMR", "isq-inmr"),
        ("qNMR", "isq-qnmr"),
        ("sNMR", "isq-snmr"),
    ]

    for name, exec_name in apps:
        app_dir = applications_dir / f"{name}.app" / "Contents" / "MacOS"
        app_dir.mkdir(parents=True, exist_ok=True)
        script_path = app_dir / f"{name}"
        
        with open(script_path, "w") as f:
            f.write(f"""#!/bin/bash
source "{Path(sys.prefix)}/bin/activate"
exec "{exec_name}" "$@"
""")
        os.chmod(script_path, 0o755)
        
        # Crear Info.plist básico
        with open(app_dir.parent / "Info.plist", "w") as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{name}</string>
    <key>CFBundleName</key>
    <string>{name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.exci5ion.isq-suite.{name.replace(" ", "-")}</string>
</dict>
</plist>
""")

if __name__ == "__main__":
    system = platform.system()
    try:
        if system == "Windows":
            create_windows_shortcuts()
        elif system == "Linux":
            create_linux_shortcuts()
        elif system == "Darwin":
            create_macos_shortcuts()
        print("Shortcuts created successfully!")
    except Exception as e:
        print(f"Error creating shortcuts: {str(e)}")
        sys.exit(1)
