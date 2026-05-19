# erp.py - Programa principal del ERP
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import sys
import hashlib

# Configurar la base de datos
def obtener_ruta_db():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'autovidrio.db')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autovidrio.db')

class Database:
    def __init__(self):
        self.db_path = obtener_ruta_db()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.crear_tablas()
    
    def crear_tablas(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT, apellido TEXT, email TEXT UNIQUE, password TEXT, rol TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE, nombre TEXT, descripcion TEXT, categoria TEXT,
                precio_compra REAL, precio_venta REAL, stock_actual INTEGER, stock_minimo INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula TEXT UNIQUE, nombre TEXT, apellido TEXT, telefono TEXT, direccion TEXT, email TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER, fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subtotal REAL, iva REAL, total REAL, metodo_pago TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER, id_producto INTEGER, cantidad INTEGER, precio_unitario REAL, subtotal REAL
            )
        ''')
        
        self.cursor.execute("SELECT COUNT(*) FROM usuarios")
        if self.cursor.fetchone()[0] == 0:
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute("INSERT INTO usuarios (nombre, apellido, email, password, rol) VALUES ('Admin', 'Sistema', 'admin@autovidrio.com', ?, 'admin')", (password_hash,))
            self.conn.commit()
    
    def verificar_login(self, email, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT id_usuario, nombre, apellido, email, rol FROM usuarios WHERE email = ? AND password = ?", (email, password_hash))
        return self.cursor.fetchone()
    
    def obtener_productos(self):
        self.cursor.execute("SELECT * FROM productos ORDER BY id_producto DESC")
        return self.cursor.fetchall()
    
    def agregar_producto(self, codigo, nombre, desc, cat, pc, pv, stock, stock_min):
        self.cursor.execute("INSERT INTO productos (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo) VALUES (?,?,?,?,?,?,?,?)", (codigo, nombre, desc, cat, pc, pv, stock, stock_min))
        self.conn.commit()
    
    def eliminar_producto(self, id_prod):
        self.cursor.execute("DELETE FROM productos WHERE id_producto=?", (id_prod,))
        self.conn.commit()
    
    def obtener_producto_por_id(self, id_prod):
        self.cursor.execute("SELECT * FROM productos WHERE id_producto=?", (id_prod,))
        return self.cursor.fetchone()
    
    def actualizar_producto(self, id_prod, codigo, nombre, desc, cat, pc, pv, stock, stock_min):
        self.cursor.execute("UPDATE productos SET codigo=?, nombre=?, descripcion=?, categoria=?, precio_compra=?, precio_venta=?, stock_actual=?, stock_minimo=? WHERE id_producto=?", (codigo, nombre, desc, cat, pc, pv, stock, stock_min, id_prod))
        self.conn.commit()
    
    def obtener_clientes(self):
        self.cursor.execute("SELECT * FROM clientes ORDER BY id_cliente DESC")
        return self.cursor.fetchall()
    
    def agregar_cliente(self, cedula, nombre, apellido, telefono, direccion, email):
        try:
            self.cursor.execute("INSERT INTO clientes (cedula, nombre, apellido, telefono, direccion, email) VALUES (?,?,?,?,?,?)", (cedula, nombre, apellido, telefono, direccion, email))
            self.conn.commit()
            return True, "Cliente agregado"
        except:
            return False, "Cédula ya existe"
    
    def eliminar_cliente(self, id_cli):
        self.cursor.execute("DELETE FROM clientes WHERE id_cliente=?", (id_cli,))
        self.conn.commit()
    
    def registrar_venta(self, id_cliente, items, metodo):
        subtotal = sum(i['precio'] * i['cantidad'] for i in items)
        iva = subtotal * 0.16
        total = subtotal + iva
        
        self.cursor.execute("INSERT INTO ventas (id_cliente, subtotal, iva, total, metodo_pago) VALUES (?,?,?,?,?)", (id_cliente if id_cliente != 0 else None, subtotal, iva, total, metodo))
        id_venta = self.cursor.lastrowid
        
        for item in items:
            self.cursor.execute("INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)", (id_venta, item['id_producto'], item['cantidad'], item['precio'], item['precio'] * item['cantidad']))
            self.cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto=?", (item['cantidad'], item['id_producto']))
        
        self.conn.commit()
        return id_venta
    
    def obtener_ventas(self):
        self.cursor.execute("SELECT v.id_venta, v.fecha_venta, COALESCE(c.nombre || ' ' || c.apellido, 'Cliente General'), v.subtotal, v.iva, v.total, v.metodo_pago FROM ventas v LEFT JOIN clientes c ON v.id_cliente = c.id_cliente ORDER BY v.id_venta DESC LIMIT 50")
        return self.cursor.fetchall()
    
    def obtener_estadisticas(self):
        self.cursor.execute("SELECT COUNT(*) FROM productos")
        total_prod = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM clientes")
        total_cli = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM ventas")
        ventas = self.cursor.fetchone()
        self.cursor.execute("SELECT COUNT(*) FROM productos WHERE stock_actual <= stock_minimo")
        stock_bajo = self.cursor.fetchone()[0]
        return {'total_productos': total_prod, 'total_clientes': total_cli, 'total_ventas': ventas[0], 'monto_ventas': ventas[1], 'stock_bajo': stock_bajo}
    
    def cerrar(self):
        self.conn.close()

# ==================== VENTANA DE LOGIN ====================
class LoginApp:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("Auto Vidrio ERP - Inicio")
        self.root.geometry("400x450")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a3c34')
        self.db = Database()
        self.centrar()
        self.crear_widgets()
    
    def centrar(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 200
        y = (self.root.winfo_screenheight() // 2) - 225
        self.root.geometry(f'400x450+{x}+{y}')
    
    def crear_widgets(self):
        frame = tk.Frame(self.root, bg='white')
        frame.place(relx=0.5, rely=0.5, anchor='center', width=340, height=380)
        
        tk.Label(frame, text="🏢 Auto Vidrio Venezuela C.A.", font=('Arial', 12, 'bold'), bg='white', fg='#1a3c34').pack(pady=(30,5))
        tk.Label(frame, text="Sistema ERP de Gestión", font=('Arial', 9), bg='white', fg='#666').pack(pady=(0,30))
        
        tk.Label(frame, text="Correo Electrónico", font=('Arial', 9), bg='white').pack(anchor='w', padx=30)
        self.email = tk.Entry(frame, font=('Arial', 10), relief='solid', bd=1)
        self.email.pack(fill='x', padx=30, pady=(5,15))
        self.email.insert(0, "admin@autovidrio.com")
        
        tk.Label(frame, text="Contraseña", font=('Arial', 9), bg='white').pack(anchor='w', padx=30)
        self.password = tk.Entry(frame, font=('Arial', 10), relief='solid', bd=1, show="•")
        self.password.pack(fill='x', padx=30, pady=(5,20))
        self.password.insert(0, "admin123")
        
        btn = tk.Button(frame, text="Iniciar Sesión", bg='#1a3c34', fg='white', font=('Arial', 10, 'bold'), relief='flat', cursor='hand2', command=self.login)
        btn.pack(fill='x', padx=30, pady=10)
        
        self.password.bind('<Return>', lambda e: self.login())
    
    def login(self):
        usuario = self.db.verificar_login(self.email.get(), self.password.get())
        if usuario:
            self.on_success(usuario)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

# ==================== VENTANA PRINCIPAL ====================
class ERPApp:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.db = Database()
        self.root.title(f"Auto Vidrio ERP - {usuario[1]} {usuario[2]}")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f2f5')
        self.centrar()
        self.crear_menu()
        self.mostrar_dashboard()
    
    def centrar(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 600
        y = (self.root.winfo_screenheight() // 2) - 350
        self.root.geometry(f'1200x700+{x}+{y}')
    
    def crear_menu(self):
        toolbar = tk.Frame(self.root, bg='#1a3c34', height=50)
        toolbar.pack(fill='x')
        
        tk.Label(toolbar, text="🏢 Auto Vidrio ERP", font=('Arial', 14, 'bold'), bg='#1a3c34', fg='white').pack(side='left', padx=20)
        
        botones = [
            ("📊 Dashboard", self.mostrar_dashboard),
            ("📦 Productos", self.mostrar_productos),
            ("👥 Clientes", self.mostrar_clientes),
            ("💰 Ventas", self.mostrar_ventas)
        ]
        if self.usuario[4] == 'admin':
            botones.append(("📈 Reportes", self.mostrar_reportes))
        
        for texto, comando in botones:
            btn = tk.Button(toolbar, text=texto, bg='#1a3c34', fg='white', relief='flat', cursor='hand2', command=comando)
            btn.pack(side='left', padx=10, pady=10)
        
        tk.Label(toolbar, text=f"👤 {self.usuario[1]} ({self.usuario[4]})", bg='#1a3c34', fg='white').pack(side='right', padx=20)
        
        self.frame = tk.Frame(self.root, bg='#f0f2f5')
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    def limpiar(self):
        for w in self.frame.winfo_children():
            w.destroy()
    
    def mostrar_dashboard(self):
        self.limpiar()
        stats = self.db.obtener_estadisticas()
        tk.Label(self.frame, text="Panel de Control", font=('Arial', 20, 'bold'), bg='#f0f2f5').pack(anchor='w', pady=10)
        
        frame_stats = tk.Frame(self.frame, bg='#f0f2f5')
        frame_stats.pack(fill='x', pady=20)
        
        datos = [
            (stats['total_productos'], "📦 Productos", "#1a3c34"),
            (stats['total_clientes'], "👥 Clientes", "#28a745"),
            (stats['total_ventas'], "💰 Ventas Totales", "#17a2b8"),
            (f"Bs {stats['monto_ventas']:,.0f}", "💵 Monto Facturado", "#ffc107"),
            (stats['stock_bajo'], "⚠️ Stock Bajo", "#dc3545")
        ]
        
        for i, (valor, label, color) in enumerate(datos):
            card = tk.Frame(frame_stats, bg='white', relief='raised', bd=1)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            tk.Label(card, text=str(valor), font=('Arial', 24, 'bold'), bg='white', fg=color).pack(pady=(20,5))
            tk.Label(card, text=label, font=('Arial', 10), bg='white').pack(pady=(0,20))
            frame_stats.grid_columnconfigure(i, weight=1)
    
    def mostrar_productos(self):
        self.limpiar()
        tk.Button(self.frame, text="➕ Agregar Producto", bg='#28a745', fg='white', command=self.form_producto).pack(anchor='w', pady=10)
        
        tree = ttk.Treeview(self.frame, columns=('cod','nom','cat','stock','precio'), show='headings', height=20)
        tree.heading('cod', text='Código'); tree.heading('nom', text='Nombre'); tree.heading('cat', text='Categoría')
        tree.heading('stock', text='Stock'); tree.heading('precio', text='Precio Venta')
        tree.column('cod', width=100); tree.column('nom', width=250); tree.column('cat', width=120)
        tree.column('stock', width=80); tree.column('precio', width=120)
        
        for p in self.db.obtener_productos():
            tree.insert('', 'end', values=(p[1], p[2], p[4], p[6], f"Bs {p[5]:.2f}"), tags=(p[0],))
        
        def on_click(e):
            item = tree.identify_row(e.y)
            if item:
                id_prod = tree.item(item)['tags'][0]
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Editar", command=lambda: self.editar_producto(id_prod, tree))
                menu.add_command(label="Eliminar", command=lambda: self.eliminar_producto(id_prod, tree))
                menu.post(e.x_root, e.y_root)
        
        tree.bind('<Button-3>', on_click)
        tree.pack(fill='both', expand=True)
        self.productos_tree = tree
    
    def form_producto(self):
        win = tk.Toplevel(self.root)
        win.title("Nuevo Producto")
        win.geometry("400x500")
        win.configure(bg='white')
        
        campos = [("Código", "entry_cod"), ("Nombre", "entry_nom"), ("Categoría", "entry_cat"),
                  ("Stock", "entry_stock"), ("Stock Mínimo", "entry_min"), ("Precio Compra", "entry_pc"), ("Precio Venta", "entry_pv")]
        entries = {}
        
        for i, (label, key) in enumerate(campos):
            tk.Label(win, text=label, bg='white').pack(anchor='w', padx=20, pady=(10 if i>0 else 20,0))
            e = tk.Entry(win, font=('Arial', 10))
            e.pack(fill='x', padx=20, pady=(5,0))
            entries[key] = e
        
        tk.Label(win, text="Descripción", bg='white').pack(anchor='w', padx=20, pady=(10,0))
        text_desc = tk.Text(win, height=4)
        text_desc.pack(fill='x', padx=20, pady=(5,0))
        
        def guardar():
            self.db.agregar_producto(
                entries['entry_cod'].get(), entries['entry_nom'].get(), text_desc.get('1.0','end').strip(),
                entries['entry_cat'].get(), float(entries['entry_pc'].get()), float(entries['entry_pv'].get()),
                int(entries['entry_stock'].get()), int(entries['entry_min'].get())
            )
            win.destroy()
            self.mostrar_productos()
            messagebox.showinfo("Éxito", "Producto agregado")
        
        tk.Button(win, text="Guardar", bg='#1a3c34', fg='white', command=guardar).pack(pady=20)
    
    def editar_producto(self, id_prod, tree):
        p = self.db.obtener_producto_por_id(id_prod)
        if not p: return
        
        win = tk.Toplevel(self.root)
        win.title("Editar Producto")
        win.geometry("400x500")
        win.configure(bg='white')
        
        tk.Label(win, text="Código", bg='white').pack(anchor='w', padx=20, pady=(20,0))
        e_cod = tk.Entry(win); e_cod.insert(0, p[1]); e_cod.pack(fill='x', padx=20)
        
        tk.Label(win, text="Nombre", bg='white').pack(anchor='w', padx=20)
        e_nom = tk.Entry(win); e_nom.insert(0, p[2]); e_nom.pack(fill='x', padx=20)
        
        tk.Label(win, text="Categoría", bg='white').pack(anchor='w', padx=20)
        e_cat = tk.Entry(win); e_cat.insert(0, p[4] or ''); e_cat.pack(fill='x', padx=20)
        
        tk.Label(win, text="Stock", bg='white').pack(anchor='w', padx=20)
        e_stock = tk.Entry(win); e_stock.insert(0, p[6]); e_stock.pack(fill='x', padx=20)
        
        tk.Label(win, text="Stock Mínimo", bg='white').pack(anchor='w', padx=20)
        e_min = tk.Entry(win); e_min.insert(0, p[7]); e_min.pack(fill='x', padx=20)
        
        tk.Label(win, text="Precio Compra", bg='white').pack(anchor='w', padx=20)
        e_pc = tk.Entry(win); e_pc.insert(0, p[5]); e_pc.pack(fill='x', padx=20)
        
        tk.Label(win, text="Precio Venta", bg='white').pack(anchor='w', padx=20)
        e_pv = tk.Entry(win); e_pv.insert(0, p[6]); e_pv.pack(fill='x', padx=20)
        
        tk.Label(win, text="Descripción", bg='white').pack(anchor='w', padx=20)
        text_desc = tk.Text(win, height=4)
        text_desc.insert('1.0', p[3] or '')
        text_desc.pack(fill='x', padx=20)
        
        def actualizar():
            self.db.actualizar_producto(id_prod, e_cod.get(), e_nom.get(), text_desc.get('1.0','end').strip(),
                                       e_cat.get(), float(e_pc.get()), float(e_pv.get()),
                                       int(e_stock.get()), int(e_min.get()))
            win.destroy()
            self.mostrar_productos()
            messagebox.showinfo("Éxito", "Producto actualizado")
        
        tk.Button(win, text="Guardar", bg='#1a3c34', fg='white', command=actualizar).pack(pady=20)
    
    def eliminar_producto(self, id_prod, tree):
        if messagebox.askyesno("Confirmar", "¿Eliminar producto?"):
            self.db.eliminar_producto(id_prod)
            self.mostrar_productos()
            messagebox.showinfo("Éxito", "Producto eliminado")
    
    def mostrar_clientes(self):
        self.limpiar()
        tk.Button(self.frame, text="➕ Agregar Cliente", bg='#28a745', fg='white', command=self.form_cliente).pack(anchor='w', pady=10)
        
        tree = ttk.Treeview(self.frame, columns=('ced','nom','ape','tel','email'), show='headings', height=20)
        tree.heading('ced', text='Cédula'); tree.heading('nom', text='Nombre')
        tree.heading('ape', text='Apellido'); tree.heading('tel', text='Teléfono')
        tree.heading('email', text='Email')
        
        for c in self.db.obtener_clientes():
            tree.insert('', 'end', values=(c[1], c[2], c[3], c[4], c[5]), tags=(c[0],))
        
        def on_click(e):
            item = tree.identify_row(e.y)
            if item:
                id_cli = tree.item(item)['tags'][0]
                if messagebox.askyesno("Confirmar", "¿Eliminar cliente?"):
                    self.db.eliminar_cliente(id_cli)
                    self.mostrar_clientes()
                    messagebox.showinfo("Éxito", "Cliente eliminado")
        
        tree.bind('<Button-3>', on_click)
        tree.pack(fill='both', expand=True)
    
    def form_cliente(self):
        win = tk.Toplevel(self.root)
        win.title("Nuevo Cliente")
        win.geometry("400" if sys.platform == "win32" else "500")
        win.configure(bg='white')
        
        campos = [("Cédula", "ced"), ("Nombre", "nom"), ("Apellido", "ape"), ("Teléfono", "tel"), ("Email", "email")]
        entries = {}
        
        for label, key in campos:
            tk.Label(win, text=label, bg='white').pack(anchor='w', padx=20, pady=(10,0))
            e = tk.Entry(win, font=('Arial', 10))
            e.pack(fill='x', padx=20, pady=(5,0))
            entries[key] = e
        
        tk.Label(win, text="Dirección", bg='white').pack(anchor='w', padx=20, pady=(10,0))
        text_dir = tk.Text(win, height=3)
        text_dir.pack(fill='x', padx=20, pady=(5,0))
        
        def guardar():
            ok, msg = self.db.agregar_cliente(entries['ced'].get(), entries['nom'].get(), entries['ape'].get(),
                                             entries['tel'].get(), text_dir.get('1.0','end').strip(), entries['email'].get())
            if ok:
                win.destroy()
                self.mostrar_clientes()
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)
        
        tk.Button(win, text="Guardar", bg='#1a3c34', fg='white', command=guardar).pack(pady=20)
    
    def mostrar_ventas(self):
        self.limpiar()
        
        # Frame nueva venta
        frame_nueva = tk.LabelFrame(self.frame, text="Nueva Venta", font=('Arial', 12, 'bold'), bg='white', fg='#1a3c34')
        frame_nueva.pack(fill='x', pady=(0,20))
        
        # Cliente
        row1 = tk.Frame(frame_nueva, bg='white')
        row1.pack(fill='x', padx=20, pady=10)
        tk.Label(row1, text="Cliente:", bg='white').pack(side='left')
        self.cliente_combo = ttk.Combobox(row1, width=50)
        self.cliente_combo.pack(side='left', padx=(10,0))
        clientes = [("0", "Cliente General")] + [(c[0], f"{c[2]} {c[3]} - {c[1]}") for c in self.db.obtener_clientes()]
        self.cliente_combo['values'] = [f"{id} - {nom}" for id, nom in clientes]
        
        # Método pago
        row2 = tk.Frame(frame_nueva, bg='white')
        row2.pack(fill='x', padx=20, pady=10)
        tk.Label(row2, text="Método de Pago:", bg='white').pack(side='left')
        self.metodo_var = tk.StringVar(value="Efectivo")
        for m in ["Efectivo", "Transferencia", "Tarjeta Débito", "Tarjeta Crédito"]:
            tk.Radiobutton(row2, text=m, variable=self.metodo_var, value=m, bg='white').pack(side='left', padx=5)
        
        # Producto
        row3 = tk.Frame(frame_nueva, bg='white')
        row3.pack(fill='x', padx=20, pady=10)
        tk.Label(row3, text="Producto:", bg='white').pack(side='left')
        self.prod_combo = ttk.Combobox(row3, width=40)
        self.prod_combo.pack(side='left', padx=(10,0))
        tk.Label(row3, text="Cantidad:", bg='white').pack(side='left', padx=(20,0))
        self.cant_entry = tk.Entry(row3, width=10)
        self.cant_entry.insert(0, "1")
        self.cant_entry.pack(side='left', padx=(10,0))
        tk.Button(row3, text="Agregar", bg='#28a745', fg='white', command=self.agregar_item).pack(side='left', padx=(20,0))
        
        # Lista items
        self.items_frame = tk.Frame(frame_nueva, bg='white')
        self.items_frame.pack(fill='x', padx=20, pady=10)
        self.items_venta = []
        
        # Botón registrar
        tk.Button(frame_nueva, text="Registrar Venta", bg='#1a3c34', fg='white', font=('Arial', 10, 'bold'), command=self.registrar_venta).pack(pady=20)
        
        # Historial
        frame_hist = tk.LabelFrame(self.frame, text="Últimas Ventas", font=('Arial', 12, 'bold'), bg='white')
        frame_hist.pack(fill='both', expand=True)
        
        tree = ttk.Treeview(frame_hist, columns=('id','fecha','cliente','sub','iva','total','pago'), show='headings', height=10)
        tree.heading('id', text='#'); tree.heading('fecha', text='Fecha'); tree.heading('cliente', text='Cliente')
        tree.heading('sub', text='Subtotal'); tree.heading('iva', text='IVA'); tree.heading('total', text='Total'); tree.heading('pago', text='Pago')
        
        for v in self.db.obtener_ventas():
            tree.insert('', 'end', values=(v[0], v[1], v[2], f"Bs {v[3]:.2f}", f"Bs {v[4]:.2f}", f"Bs {v[5]:.2f}", v[6]))
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.ventas_tree = tree
        self.actualizar_productos_combo()
    
    def actualizar_productos_combo(self):
        prods = [(p[0], f"{p[1]} - {p[2]} (Stock: {p[6]}) - Bs {p[5]:.2f}") for p in self.db.obtener_productos() if p[6] > 0]
        self.prod_combo['values'] = [f"{id} - {nom}" for id, nom in prods]
    
    def agregar_item(self):
        sel = self.prod_combo.get()
        if not sel:
            messagebox.showerror("Error", "Seleccione un producto")
            return
        try:
            cant = int(self.cant_entry.get())
            if cant <= 0: raise ValueError
        except:
            messagebox.showerror("Error", "Cantidad válida")
            return
        
        id_prod = int(sel.split(" - ")[0])
        prod = self.db.obtener_producto_por_id(id_prod)
        if prod[6] < cant:
            messagebox.showerror("Error", f"Stock insuficiente (solo {prod[6]})")
            return
        
        self.items_venta.append({'id': id_prod, 'nombre': prod[2], 'cant': cant, 'precio': prod[5]})
        self.actualizar_lista_items()
        self.prod_combo.set("")
        self.cant_entry.delete(0, tk.END)
        self.cant_entry.insert(0, "1")
    
    def actualizar_lista_items(self):
        for w in self.items_frame.winfo_children():
            w.destroy()
        total = 0
        for i, item in enumerate(self.items_venta):
            subt = item['cant'] * item['precio']
            total += subt
            row = tk.Frame(self.items_frame, bg='#f8f9fa', relief='solid', bd=1)
            row.pack(fill='x', pady=2)
            tk.Label(row, text=item['nombre'], bg='#f8f9fa', width=30, anchor='w').pack(side='left', padx=5)
            tk.Label(row, text=f"x{item['cant']}", bg='#f8f9fa', width=8).pack(side='left')
            tk.Label(row, text=f"Bs {item['precio']:.2f}", bg='#f8f9fa', width=12).pack(side='left')
            tk.Label(row, text=f"Bs {subt:.2f}", bg='#f8f9fa', width=12).pack(side='left')
            tk.Button(row, text="X", bg='#dc3545', fg='white', command=lambda idx=i: self.eliminar_item(idx)).pack(side='right', padx=5)
        
        if self.items_venta:
            iva = total * 0.16
            tk.Label(self.items_frame, text=f"Subtotal: Bs {total:.2f}", font=('Arial', 10, 'bold'), bg='white').pack()
            tk.Label(self.items_frame, text=f"IVA: Bs {iva:.2f}", font=('Arial', 10), bg='white').pack()
            tk.Label(self.items_frame, text=f"TOTAL: Bs {total + iva:.2f}", font=('Arial', 12, 'bold'), fg='#1a3c34', bg='white').pack()
    
    def eliminar_item(self, idx):
        del self.items_venta[idx]
        self.actualizar_lista_items()
    
    def registrar_venta(self):
        if not self.items_venta:
            messagebox.showerror("Error", "Agregue productos")
            return
        sel = self.cliente_combo.get()
        id_cli = int(sel.split(" - ")[0]) if sel and " - " in sel else 0
        items = [{'id_producto': i['id'], 'cantidad': i['cant'], 'precio': i['precio']} for i in self.items_venta]
        self.db.registrar_venta(id_cli, items, self.metodo_var.get())
        messagebox.showinfo("Éxito", "Venta registrada")
        self.items_venta = []
        self.actualizar_lista_items()
        self.actualizar_productos_combo()
        self.mostrar_ventas()
    
    def mostrar_reportes(self):
        self.limpiar()
        stats = self.db.obtener_estadisticas()
        texto = f"""
        📊 RESUMEN GENERAL
        📦 Productos: {stats['total_productos']}
        👥 Clientes: {stats['total_clientes']}
        💰 Ventas: {stats['total_ventas']}
        💵 Monto total: Bs {stats['monto_ventas']:,.0f}
        ⚠️ Stock bajo: {stats['stock_bajo']}
        """
        tk.Label(self.frame, text=texto, font=('Arial', 12), bg='#f0f2f5', justify='left').pack(anchor='w', pady=20)

# ==================== MAIN ====================
class Aplicacion:
    def __init__(self):
        self.root = tk.Tk()
        self.login = LoginApp(self.root, self.iniciar_erp)
    
    def iniciar_erp(self, usuario):
        for w in self.root.winfo_children():
            w.destroy()
        self.erp = ERPApp(self.root, usuario)
    
    def ejecutar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Aplicacion()
    app.ejecutar()