import os
import sys
import subprocess

def fix_pywin32():
    try:
        # Buscar script de post-instalación de pywin32
        pywin32_postinstall = os.path.join(
            sys.prefix, 
            'Scripts', 
            'pywin32_postinstall.py'
        )
        
        if os.path.exists(pywin32_postinstall):
            print("Running pywin32 post-install script...")
            subprocess.run([
                sys.executable, 
                pywin32_postinstall, 
                '-install'
            ], check=True)
            print("pywin32 fixed successfully!")
        else:
            print("pywin32_postinstall.py not found")
    except Exception as e:
        print(f"Error fixing pywin32: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform == "win32":
        fix_pywin32()
    else:
        print("Skipping pywin32 fix (not on Windows)")
