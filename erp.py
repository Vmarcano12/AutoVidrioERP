# erp.py - Archivo principal para ejecutar el ERP
import tkinter as tk
from login import LoginApp
from main import ERPApp
import sys

class AplicacionERP:
    def __init__(self):
        self.root = tk.Tk()
        self.mostrar_login()
    
    def mostrar_login(self):
        self.login_frame = LoginApp(self.root, self.iniciar_sesion_exitosa)
    
    def iniciar_sesion_exitosa(self, usuario):
        # Destruir la ventana de login
        for widget in self.root.winfo_children():
            widget.destroy()
        # Iniciar el ERP principal
        self.app = ERPApp(self.root, usuario)
    
    def ejecutar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AplicacionERP()
    app.ejecutar()