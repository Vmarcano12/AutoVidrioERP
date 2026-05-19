# login.py - Pantalla de inicio de sesión
import tkinter as tk
from tkinter import messagebox
from database import Database

class LoginApp:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Auto Vidrio ERP - Inicio de Sesión")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a3c34')
        
        self.db = Database()
        self.centrar_ventana()
        self.crear_widgets()
    
    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = 450
        alto = 500
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def crear_widgets(self):
        # Frame principal
        frame = tk.Frame(self.root, bg='white', bd=2, relief='flat')
        frame.place(relx=0.5, rely=0.5, anchor='center', width=380, height=420)
        
        # Título
        titulo = tk.Label(frame, text="🏢 Auto Vidrio Venezuela C.A.", 
                          font=('Arial', 14, 'bold'), bg='white', fg='#1a3c34')
        titulo.pack(pady=(30, 5))
        
        subtitulo = tk.Label(frame, text="Sistema ERP de Gestión", 
                             font=('Arial', 10), bg='white', fg='#666')
        subtitulo.pack(pady=(0, 30))
        
        # Email
        lbl_email = tk.Label(frame, text="📧 Correo Electrónico", 
                             font=('Arial', 10), bg='white', fg='#333')
        lbl_email.pack(anchor='w', padx=40, pady=(0, 5))
        
        self.entry_email = tk.Entry(frame, font=('Arial', 11), relief='solid', bd=1)
        self.entry_email.pack(fill='x', padx=40, pady=(0, 20))
        self.entry_email.insert(0, "admin@autovidrio.com")
        
        # Contraseña
        lbl_pass = tk.Label(frame, text="🔒 Contraseña", 
                            font=('Arial', 10), bg='white', fg='#333')
        lbl_pass.pack(anchor='w', padx=40, pady=(0, 5))
        
        self.entry_password = tk.Entry(frame, font=('Arial', 11), relief='solid', bd=1, show="•")
        self.entry_password.pack(fill='x', padx=40, pady=(0, 20))
        self.entry_password.insert(0, "admin123")
        
        # Botón login
        btn_login = tk.Button(frame, text="Iniciar Sesión", 
                              font=('Arial', 11, 'bold'),
                              bg='#1a3c34', fg='white',
                              relief='flat', cursor='hand2',
                              command=self.login)
        btn_login.pack(fill='x', padx=40, pady=(10, 10))
        
        # Información
        info = tk.Label(frame, text="Sistema para Contabilidad y Almacén\nAuto Vidrio Venezuela C.A.", 
                        font=('Arial', 8), bg='white', fg='#999')
        info.pack(pady=(20, 0))
        
        # Bind Enter
        self.entry_password.bind('<Return>', lambda e: self.login())
    
    def login(self):
        email = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        usuario = self.db.verificar_login(email, password)
        
        if usuario:
            self.on_login_success(usuario)
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos")