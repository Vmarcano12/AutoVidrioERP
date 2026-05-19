# setup.py - Instalador del ERP
import os
import sys
import shutil
import subprocess

def instalar_erp():
    # Obtener la ruta donde se está ejecutando el instalador
    if getattr(sys, 'frozen', False):
        origen = os.path.dirname(sys.executable)
    else:
        origen = os.path.dirname(os.path.abspath(__file__))
    
    # Carpeta de destino (escritorio del usuario)
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    destino = os.path.join(escritorio, "AutoVidrioERP")
    
    # Crear carpeta de destino
    if not os.path.exists(destino):
        os.makedirs(destino)
    
    # Copiar el archivo erp.py como .exe (o el archivo que se ejecutará)
    erp_origen = os.path.join(origen, "AutoVidrioERP.exe")
    erp_destino = os.path.join(destino, "AutoVidrioERP.exe")
    
    if os.path.exists(erp_origen):
        shutil.copy2(erp_origen, erp_destino)
    else:
        # Si no hay .exe, copiamos el .py
        erp_origen = os.path.join(origen, "erp.py")
        shutil.copy2(erp_origen, erp_destino)
    
    # Crear acceso directo en el escritorio
    crear_acceso_directo(erp_destino, os.path.join(escritorio, "AutoVidrioERP.lnk"))
    
    # Mostrar mensaje de éxito
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Instalación Completa", 
                        f"✅ ERP instalado correctamente en:\n{destino}\n\n"
                        "Se ha creado un acceso directo en el escritorio.\n"
                        "Usuario: admin@autovidrio.com\n"
                        "Contraseña: admin123")
    root.destroy()

def crear_acceso_directo(origen, destino):
    try:
        import ctypes
        from ctypes import wintypes
        import pythoncom
        from win32com.client import Dispatch
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(destino)
        shortcut.Targetpath = origen
        shortcut.WorkingDirectory = os.path.dirname(origen)
        shortcut.save()
    except:
        # Si falla, crear un archivo .bat simple
        with open(destino.replace('.lnk', '.bat'), 'w') as f:
            f.write(f'@echo off\nstart "" "{origen}"\nexit')

if __name__ == "__main__":
    instalar_erp()