# main.py - Programa principal del ERP
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Database

class ERPApp:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.db = Database()
        
        self.root.title(f"Auto Vidrio ERP - Bienvenido {usuario[1]} {usuario[2]}")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f2f5')
        
        self.centrar_ventana()
        self.crear_menu()
        self.mostrar_dashboard()
    
    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = 1200
        alto = 700
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def crear_menu(self):
        # Barra superior
        toolbar = tk.Frame(self.root, bg='#1a3c34', height=60)
        toolbar.pack(fill='x')
        
        # Logo
        logo = tk.Label(toolbar, text="🏢 Auto Vidrio ERP", 
                        font=('Arial', 16, 'bold'), bg='#1a3c34', fg='white')
        logo.pack(side='left', padx=20, pady=15)
        
        # Botones del menú
        btn_dashboard = tk.Button(toolbar, text="📊 Dashboard", 
                                  font=('Arial', 10), bg='#1a3c34', fg='white',
                                  relief='flat', cursor='hand2',
                                  command=self.mostrar_dashboard)
        btn_dashboard.pack(side='left', padx=5, pady=15)
        
        btn_productos = tk.Button(toolbar, text="📦 Productos", 
                                  font=('Arial', 10), bg='#1a3c34', fg='white',
                                  relief='flat', cursor='hand2',
                                  command=self.mostrar_productos)
        btn_productos.pack(side='left', padx=5, pady=15)
        
        btn_clientes = tk.Button(toolbar, text="👥 Clientes", 
                                 font=('Arial', 10), bg='#1a3c34', fg='white',
                                 relief='flat', cursor='hand2',
                                 command=self.mostrar_clientes)
        btn_clientes.pack(side='left', padx=5, pady=15)
        
        btn_ventas = tk.Button(toolbar, text="💰 Ventas", 
                               font=('Arial', 10), bg='#1a3c34', fg='white',
                               relief='flat', cursor='hand2',
                               command=self.mostrar_ventas)
        btn_ventas.pack(side='left', padx=5, pady=15)
        
        if self.usuario[4] == 'admin':
            btn_reportes = tk.Button(toolbar, text="📈 Reportes", 
                                     font=('Arial', 10), bg='#1a3c34', fg='white',
                                     relief='flat', cursor='hand2',
                                     command=self.mostrar_reportes)
            btn_reportes.pack(side='left', padx=5, pady=15)
        
        # Usuario
        lbl_usuario = tk.Label(toolbar, text=f"👤 {self.usuario[1]} {self.usuario[2]} ({self.usuario[4]})", 
                               font=('Arial', 9), bg='#1a3c34', fg='#ccc')
        lbl_usuario.pack(side='right', padx=20, pady=15)
        
        # Frame contenedor principal
        self.frame_contenido = tk.Frame(self.root, bg='#f0f2f5')
        self.frame_contenido.pack(fill='both', expand=True, padx=20, pady=20)
    
    def limpiar_contenido(self):
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()
    
    # ==================== DASHBOARD ====================
    def mostrar_dashboard(self):
        self.limpiar_contenido()
        
        stats = self.db.obtener_estadisticas()
        
        # Título
        titulo = tk.Label(self.frame_contenido, text="Panel de Control", 
                          font=('Arial', 18, 'bold'), bg='#f0f2f5', fg='#333')
        titulo.pack(anchor='w', pady=(0, 20))
        
        # Tarjetas de estadísticas
        frame_stats = tk.Frame(self.frame_contenido, bg='#f0f2f5')
        frame_stats.pack(fill='x', pady=(0, 20))
        
        tarjetas = [
            (f"{stats['total_productos']}", "📦 Productos", "#1a3c34"),
            (f"{stats['total_clientes']}", "👥 Clientes", "#28a745"),
            (f"{stats['total_ventas']}", "💰 Ventas Totales", "#17a2b8"),
            (f"Bs {stats['monto_ventas']:,.2f}", "💵 Monto Facturado", "#ffc107"),
            (f"{stats['stock_bajo']}", "⚠️ Stock Bajo", "#dc3545")
        ]
        
        for i, (valor, label, color) in enumerate(tarjetas):
            card = tk.Frame(frame_stats, bg='white', relief='raised', bd=1)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            
            lbl_valor = tk.Label(card, text=valor, font=('Arial', 24, 'bold'), 
                                 bg='white', fg=color)
            lbl_valor.pack(pady=(20, 5))
            
            lbl_label = tk.Label(card, text=label, font=('Arial', 10), 
                                 bg='white', fg='#666')
            lbl_label.pack(pady=(0, 20))
            
            frame_stats.grid_columnconfigure(i, weight=1)
        
        # Ventas de hoy destacado
        frame_hoy = tk.Frame(self.frame_contenido, bg='white', relief='raised', bd=1)
        frame_hoy.pack(fill='x', pady=10)
        
        lbl_hoy = tk.Label(frame_hoy, text=f"🕐 Ventas de Hoy: {stats['ventas_hoy_cantidad']} ventas | Bs {stats['ventas_hoy_monto']:,.2f}", 
                           font=('Arial', 12), bg='white', fg='#1a3c34')
        lbl_hoy.pack(pady=15)
    
    # ==================== PRODUCTOS ====================
    def mostrar_productos(self):
        self.limpiar_contenido()
        
        # Botón agregar
        btn_agregar = tk.Button(self.frame_contenido, text="➕ Agregar Producto", 
                                bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                                relief='flat', cursor='hand2',
                                command=self.formulario_producto)
        btn_agregar.pack(anchor='w', pady=(0, 10))
        
        # Tabla de productos
        frame_tabla = tk.Frame(self.frame_contenido, bg='white', relief='sunken', bd=1)
        frame_tabla.pack(fill='both', expand=True)
        
        # Scrollbars
        scroll_y = tk.Scrollbar(frame_tabla)
        scroll_y.pack(side='right', fill='y')
        
        scroll_x = tk.Scrollbar(frame_tabla, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')
        
        self.tree_productos = ttk.Treeview(frame_tabla, columns=('codigo', 'nombre', 'categoria', 'stock', 'precio', 'acciones'),
                                           show='headings', yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree_productos.yview)
        scroll_x.config(command=self.tree_productos.xview)
        
        self.tree_productos.heading('codigo', text='Código')
        self.tree_productos.heading('nombre', text='Nombre')
        self.tree_productos.heading('categoria', text='Categoría')
        self.tree_productos.heading('stock', text='Stock')
        self.tree_productos.heading('precio', text='Precio Venta')
        self.tree_productos.heading('acciones', text='Acciones')
        
        self.tree_productos.column('codigo', width=100)
        self.tree_productos.column('nombre', width=250)
        self.tree_productos.column('categoria', width=120)
        self.tree_productos.column('stock', width=80)
        self.tree_productos.column('precio', width=120)
        self.tree_productos.column('acciones', width=100)
        
        self.tree_productos.pack(fill='both', expand=True)
        
        self.cargar_productos()
    
    def cargar_productos(self):
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        productos = self.db.obtener_productos()
        for p in productos:
            item = self.tree_productos.insert('', 'end', 
                values=(p[1], p[2], p[4], f"{p[6]}", f"Bs {p[5]:,.2f}", "✏️ 🗑️"),
                tags=(p[0],))
        
        self.tree_productos.bind('<ButtonRelease-1>', self.on_producto_click)
    
    def on_producto_click(self, event):
        region = self.tree_productos.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree_productos.identify_column(event.x)
            item = self.tree_productos.identify_row(event.y)
            if item:
                producto_id = self.tree_productos.item(item)['tags'][0]
                if column == '#6':
                    menu = tk.Menu(self.root, tearoff=0)
                    menu.add_command(label="✏️ Editar", command=lambda: self.editar_producto(producto_id))
                    menu.add_command(label="🗑️ Eliminar", command=lambda: self.eliminar_producto(producto_id))
                    menu.post(event.x_root, event.y_root)
    
    def formulario_producto(self):
        self.ventana_producto = tk.Toplevel(self.root)
        self.ventana_producto.title("Nuevo Producto")
        self.ventana_producto.geometry("500x550")
        self.ventana_producto.configure(bg='white')
        
        # Centrar
        self.ventana_producto.update_idletasks()
        x = (self.ventana_producto.winfo_screenwidth() // 2) - 250
        y = (self.ventana_producto.winfo_screenheight() // 2) - 275
        self.ventana_producto.geometry(f'500x550+{x}+{y}')
        
        campos = [
            ('Código *:', 'entry_codigo'),
            ('Nombre *:', 'entry_nombre'),
            ('Categoría:', 'entry_categoria'),
            ('Stock Actual *:', 'entry_stock'),
            ('Stock Mínimo *:', 'entry_stock_min'),
            ('Precio Compra *:', 'entry_precio_c'),
            ('Precio Venta *:', 'entry_precio_v'),
            ('Descripción:', 'text_desc')
        ]
        
        self.entries = {}
        
        for i, (label, key) in enumerate(campos):
            lbl = tk.Label(self.ventana_producto, text=label, font=('Arial', 10), bg='white')
            lbl.pack(anchor='w', padx=20, pady=(10 if i > 0 else 20, 0))
            
            if key == 'text_desc':
                self.entries[key] = tk.Text(self.ventana_producto, height=4, font=('Arial', 10), relief='solid', bd=1)
                self.entries[key].pack(fill='x', padx=20, pady=(5, 0))
            else:
                self.entries[key] = tk.Entry(self.ventana_producto, font=('Arial', 10), relief='solid', bd=1)
                self.entries[key].pack(fill='x', padx=20, pady=(5, 0))
        
        btn_guardar = tk.Button(self.ventana_producto, text="💾 Guardar Producto", 
                                bg='#1a3c34', fg='white', font=('Arial', 11, 'bold'),
                                relief='flat', cursor='hand2',
                                command=self.guardar_producto)
        btn_guardar.pack(pady=30)
    
    def guardar_producto(self):
        try:
            codigo = self.entries['entry_codigo'].get()
            nombre = self.entries['entry_nombre'].get()
            categoria = self.entries['entry_categoria'].get()
            stock = int(self.entries['entry_stock'].get())
            stock_min = int(self.entries['entry_stock_min'].get())
            precio_c = float(self.entries['entry_precio_c'].get())
            precio_v = float(self.entries['entry_precio_v'].get())
            descripcion = self.entries['text_desc'].get('1.0', 'end').strip()
            
            if not codigo or not nombre:
                messagebox.showerror("Error", "Código y nombre son obligatorios")
                return
            
            self.db.agregar_producto(codigo, nombre, descripcion, categoria, precio_c, precio_v, stock, stock_min)
            messagebox.showinfo("Éxito", "Producto registrado")
            self.ventana_producto.destroy()
            self.cargar_productos()
        except ValueError:
            messagebox.showerror("Error", "Verifique los valores numéricos")
    
    def editar_producto(self, producto_id):
        producto = self.db.obtener_producto_por_id(producto_id)
        if not producto:
            return
        
        self.ventana_editar = tk.Toplevel(self.root)
        self.ventana_editar.title("Editar Producto")
        self.ventana_editar.geometry("500x550")
        self.ventana_editar.configure(bg='white')
        
        self.ventana_editar.update_idletasks()
        x = (self.ventana_editar.winfo_screenwidth() // 2) - 250
        y = (self.ventana_editar.winfo_screenheight() // 2) - 275
        self.ventana_editar.geometry(f'500x550+{x}+{y}')
        
        # Entry fields
        tk.Label(self.ventana_editar, text="Código *:", font=('Arial', 10), bg='white').pack(anchor='w', padx=20, pady=(20, 0))
        entry_codigo = tk.Entry(self.ventana_editar, font=('Arial', 10), relief='solid', bd=1)
        entry_codigo.pack(fill='x', padx=20, pady=(5, 0))
        entry_codigo.insert(0, producto[1])
        
        tk.Label(self.ventana_editar, text="Nombre *:", font=('Arial', 10), bg='white').pack(anchor='w', padx=20, pady=(10, 0))
        entry_nombre = tk.Entry(self.ventana_editar, font=('Arial', 10), relief='solid', bd=1)
        entry_nombre.pack(fill='x', padx=20, pady=(5, 0))
        entry_nombre.insert(0, producto[2])
        
        tk.Label(self.ventana_editar, text="Categoría:", font=('Arial', 10), bg='white').pack(anchor='w', padx=20, pady=(10, 0))
        entry_categoria = tk.Entry(self.ventana_editar, font=('Arial', 10), relief='solid', bd=1)
        entry_categoria.pack(fill='x', padx=20, pady=(5, 0))
        entry_categoria.insert(0, producto[4] or '')
        
        tk.Label(self.ventana_editar, text="Stock Actual *:", font=('Arial', 10), bg='white').pack(anchor='w', padx=20, pady=(10, 0))
        entry_stock = tk.Entry(self.ventana_editar, font=('Arial', 10), relief='solid', bd=1)
        entry_stock.pack(fill='x', padx=20, pady=(5, 0))
        entry_stock.insert(0, producto[6])
        
        tk.Label(self.ventana_editar, text="Stock Mínimo *:", font=('Arial', 10), bg='white').pack(anchor='w', padx=20, pady=(10, 0))
        entry_stock_min = tk.Entry(self.ventana_editar, font=('Arial', 10), relief='solid', bd=1)
        entry_stock_min.pack(fill='x', padx=20, pady=(5, 0))
        entry_stock_min.insert(0, producto[7])
        
        tk.Label(self.ventana_editar, text="Precio Compra *:", font=('Arial', 10), bg='white').pack(anchor='w', padx=20, pady=(10, 0))
        entry_precio_c = tk.Entry(self.ventana_editar, font=('Arial', 10), relief='solid', bd=1)
        entry_precio_c.pack(fill='x', padx=20, pady=(5, 0))
        entry_precio_c.insert(0, producto[5])
        
        tk.Label(self.ventana_editar, text="Precio Venta *:", font=('Arial', 10), bg='white').pack(anchor='w', padx=20, pady=(10, 0))
        entry_precio_v = tk.Entry(self.ventana_editar, font=('Arial', 10), relief='solid', bd=1)
        entry_precio_v.pack(fill='x', padx=20, pady=(5, 0))
        entry_precio_v.insert(0, producto[6])
        
        tk.Label(self.ventana_editar, text="Descripción:", font=('Arial', 10), bg='white').pack(anchor='w', padx=20, pady=(10, 0))
        text_desc = tk.Text(self.ventana_editar, height=4, font=('Arial', 10), relief='solid', bd=1)
        text_desc.pack(fill='x', padx=20, pady=(5, 0))
        text_desc.insert('1.0', producto[3] or '')
        
        def actualizar():
            try:
                self.db.actualizar_producto(
                    producto_id,
                    entry_codigo.get(),
                    entry_nombre.get(),
                    text_desc.get('1.0', 'end').strip(),
                    entry_categoria.get(),
                    float(entry_precio_c.get()),
                    float(entry_precio_v.get()),
                    int(entry_stock.get()),
                    int(entry_stock_min.get())
                )
                messagebox.showinfo("Éxito", "Producto actualizado")
                self.ventana_editar.destroy()
                self.cargar_productos()
            except ValueError:
                messagebox.showerror("Error", "Verifique los valores numéricos")
        
        btn_guardar = tk.Button(self.ventana_editar, text="💾 Guardar Cambios", 
                                bg='#1a3c34', fg='white', font=('Arial', 11, 'bold'),
                                relief='flat', cursor='hand2',
                                command=actualizar)
        btn_guardar.pack(pady=30)
    
    def eliminar_producto(self, producto_id):
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            self.db.eliminar_producto(producto_id)
            self.cargar_productos()
            messagebox.showinfo("Éxito", "Producto eliminado")
    
    # ==================== CLIENTES ====================
    def mostrar_clientes(self):
        self.limpiar_contenido()
        
        # Botón agregar
        btn_agregar = tk.Button(self.frame_contenido, text="➕ Agregar Cliente", 
                                bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                                relief='flat', cursor='hand2',
                                command=self.formulario_cliente)
        btn_agregar.pack(anchor='w', pady=(0, 10))
        
        # Tabla de clientes
        frame_tabla = tk.Frame(self.frame_contenido, bg='white', relief='sunken', bd=1)
        frame_tabla.pack(fill='both', expand=True)
        
        scroll_y = tk.Scrollbar(frame_tabla)
        scroll_y.pack(side='right', fill='y')
        
        self.tree_clientes = ttk.Treeview(frame_tabla, columns=('cedula', 'nombre', 'apellido', 'telefono', 'email', 'acciones'),
                                           show='headings', yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree_clientes.yview)
        
        self.tree_clientes.heading('cedula', text='Cédula')
        self.tree_clientes.heading('nombre', text='Nombre')
        self.tree_clientes.heading('apellido', text='Apellido')
        self.tree_clientes.heading('telefono', text='Teléfono')
        self.tree_clientes.heading('email', text='Email')
        self.tree_clientes.heading('acciones', text='Acciones')
        
        self.tree_clientes.column('cedula', width=120)
        self.tree_clientes.column('nombre', width=150)
        self.tree_clientes.column('apellido', width=150)
        self.tree_clientes.column('telefono', width=120)
        self.tree_clientes.column('email', width=200)
        self.tree_clientes.column('acciones', width=80)
        
        self.tree_clientes.pack(fill='both', expand=True)
        
        self.cargar_clientes()
    
    def cargar_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        clientes = self.db.obtener_clientes()
        for c in clientes:
            self.tree_clientes.insert('', 'end', 
                values=(c[1], c[2], c[3], c[4], c[5], "🗑️"),
                tags=(c[0],))
        
        self.tree_clientes.bind('<ButtonRelease-1>', self.on_cliente_click)
    
    def on_cliente_click(self, event):
        region = self.tree_clientes.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree_clientes.identify_column(event.x)
            item = self.tree_clientes.identify_row(event.y)
            if item and column == '#6':
                cliente_id = self.tree_clientes.item(item)['tags'][0]
                if messagebox.askyesno("Confirmar", "¿Eliminar este cliente?"):
                    self.db.eliminar_cliente(cliente_id)
                    self.cargar_clientes()
                    messagebox.showinfo("Éxito", "Cliente eliminado")
    
    def formulario_cliente(self):
        self.ventana_cliente = tk.Toplevel(self.root)
        self.ventana_cliente.title("Nuevo Cliente")
        self.ventana_cliente.geometry("500x550")
        self.ventana_cliente.configure(bg='white')
        
        self.ventana_cliente.update_idletasks()
        x = (self.ventana_cliente.winfo_screenwidth() // 2) - 250
        y = (self.ventana_cliente.winfo_screenheight() // 2) - 275
        self.ventana_cliente.geometry(f'500x550+{x}+{y}')
        
        campos = [
            ('Cédula/RIF *:', 'entry_cedula'),
            ('Nombre *:', 'entry_nombre'),
            ('Apellido *:', 'entry_apellido'),
            ('Teléfono:', 'entry_telefono'),
            ('Email:', 'entry_email'),
            ('Dirección:', 'text_direccion')
        ]
        
        self.cliente_entries = {}
        
        for i, (label, key) in enumerate(campos):
            lbl = tk.Label(self.ventana_cliente, text=label, font=('Arial', 10), bg='white')
            lbl.pack(anchor='w', padx=20, pady=(10 if i > 0 else 20, 0))
            
            if key == 'text_direccion':
                self.cliente_entries[key] = tk.Text(self.ventana_cliente, height=3, font=('Arial', 10), relief='solid', bd=1)
                self.cliente_entries[key].pack(fill='x', padx=20, pady=(5, 0))
            else:
                self.cliente_entries[key] = tk.Entry(self.ventana_cliente, font=('Arial', 10), relief='solid', bd=1)
                self.cliente_entries[key].pack(fill='x', padx=20, pady=(5, 0))
        
        def guardar_cliente():
            cedula = self.cliente_entries['entry_cedula'].get()
            nombre = self.cliente_entries['entry_nombre'].get()
            apellido = self.cliente_entries['entry_apellido'].get()
            telefono = self.cliente_entries['entry_telefono'].get()
            email = self.cliente_entries['entry_email'].get()
            direccion = self.cliente_entries['text_direccion'].get('1.0', 'end').strip()
            
            if not cedula or not nombre or not apellido:
                messagebox.showerror("Error", "Cédula, nombre y apellido son obligatorios")
                return
            
            success, msg = self.db.agregar_cliente(cedula, nombre, apellido, telefono, direccion, email)
            if success:
                messagebox.showinfo("Éxito", msg)
                self.ventana_cliente.destroy()
                self.cargar_clientes()
            else:
                messagebox.showerror("Error", msg)
        
        btn_guardar = tk.Button(self.ventana_cliente, text="💾 Guardar Cliente", 
                                bg='#1a3c34', fg='white', font=('Arial', 11, 'bold'),
                                relief='flat', cursor='hand2',
                                command=guardar_cliente)
        btn_guardar.pack(pady=30)
    
    # ==================== VENTAS ====================
    def mostrar_ventas(self):
        self.limpiar_contenido()
        
        # Frame para nueva venta
        frame_nueva = tk.LabelFrame(self.frame_contenido, text="🛒 Nueva Venta", 
                                    font=('Arial', 12, 'bold'), bg='white', fg='#1a3c34')
        frame_nueva.pack(fill='x', pady=(0, 20))
        
        # Selección de cliente
        row1 = tk.Frame(frame_nueva, bg='white')
        row1.pack(fill='x', padx=20, pady=10)
        
        tk.Label(row1, text="Cliente:", font=('Arial', 10), bg='white').pack(side='left')
        self.cliente_var = tk.StringVar()
        self.cliente_combo = ttk.Combobox(row1, textvariable=self.cliente_var, width=50)
        self.cliente_combo.pack(side='left', padx=(10, 0))
        
        clientes = self.db.obtener_clientes()
        cliente_lista = [("0", "Cliente General")]
        for c in clientes:
            cliente_lista.append((c[0], f"{c[1]} {c[2]} - {c[3]}"))
        self.cliente_combo['values'] = [f"{id} - {nombre}" for id, nombre in cliente_lista]
        
        # Método de pago
        row2 = tk.Frame(frame_nueva, bg='white')
        row2.pack(fill='x', padx=20, pady=10)
        
        tk.Label(row2, text="Método de Pago:", font=('Arial', 10), bg='white').pack(side='left')
        self.metodo_pago_var = tk.StringVar(value="Efectivo")
        metodos = ["Efectivo", "Transferencia", "Tarjeta Débito", "Tarjeta Crédito"]
        for m in metodos:
            tk.Radiobutton(row2, text=m, variable=self.metodo_pago_var, value=m, bg='white').pack(side='left', padx=10)
        
        # Productos
        row3 = tk.Frame(frame_nueva, bg='white')
        row3.pack(fill='x', padx=20, pady=10)
        
        tk.Label(row3, text="Producto:", font=('Arial', 10), bg='white').pack(side='left')
        self.producto_var = tk.StringVar()
        self.producto_combo = ttk.Combobox(row3, textvariable=self.producto_var, width=40)
        self.producto_combo.pack(side='left', padx=(10, 0))
        
        tk.Label(row3, text="Cantidad:", font=('Arial', 10), bg='white').pack(side='left', padx=(20, 0))
        self.cantidad_var = tk.StringVar(value="1")
        self.cantidad_entry = tk.Entry(row3, textvariable=self.cantidad_var, width=10, font=('Arial', 10))
        self.cantidad_entry.pack(side='left', padx=(10, 0))
        
        btn_agregar = tk.Button(row3, text="➕ Agregar", bg='#28a745', fg='white', 
                                font=('Arial', 10), relief='flat', cursor='hand2',
                                command=self.agregar_item_venta)
        btn_agregar.pack(side='left', padx=(20, 0))
        
        # Lista de productos en la venta
        row4 = tk.Frame(frame_nueva, bg='white')
        row4.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.lista_items_frame = tk.Frame(row4, bg='white')
        self.lista_items_frame.pack(fill='both', expand=True)
        
        self.items_venta = []
        self.actualizar_lista_items()
        
        # Botón registrar venta
        row5 = tk.Frame(frame_nueva, bg='white')
        row5.pack(fill='x', padx=20, pady=20)
        
        btn_registrar = tk.Button(row5, text="💰 Registrar Venta", bg='#1a3c34', fg='white', 
                                  font=('Arial', 12, 'bold'), relief='flat', cursor='hand2',
                                  command=self.registrar_venta)
        btn_registrar.pack()
        
        # Historial de ventas
        frame_historial = tk.LabelFrame(self.frame_contenido, text="📋 Últimas Ventas", 
                                        font=('Arial', 12, 'bold'), bg='white', fg='#1a3c34')
        frame_historial.pack(fill='both', expand=True)
        
        # Tabla de ventas
        frame_tabla = tk.Frame(frame_historial, bg='white')
        frame_tabla.pack(fill='both', expand=True, padx=10, pady=10)
        
        scroll_y = tk.Scrollbar(frame_tabla)
        scroll_y.pack(side='right', fill='y')
        
        self.tree_ventas = ttk.Treeview(frame_tabla, columns=('id', 'fecha', 'cliente', 'subtotal', 'iva', 'total', 'pago'),
                                        show='headings', yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree_ventas.yview)
        
        self.tree_ventas.heading('id', text='#')
        self.tree_ventas.heading('fecha', text='Fecha')
        self.tree_ventas.heading('cliente', text='Cliente')
        self.tree_ventas.heading('subtotal', text='Subtotal')
        self.tree_ventas.heading('iva', text='IVA')
        self.tree_ventas.heading('total', text='Total')
        self.tree_ventas.heading('pago', text='Método')
        
        self.tree_ventas.column('id', width=50)
        self.tree_ventas.column('fecha', width=150)
        self.tree_ventas.column('cliente', width=200)
        self.tree_ventas.column('subtotal', width=100)
        self.tree_ventas.column('iva', width=100)
        self.tree_ventas.column('total', width=100)
        self.tree_ventas.column('pago', width=120)
        
        self.tree_ventas.pack(fill='both', expand=True)
        
        self.cargar_ventas()
        self.cargar_productos_combo()
    
    def cargar_productos_combo(self):
        productos = self.db.obtener_productos()
        lista = [f"{p[0]} - {p[2]} (Stock: {p[6]}) - Bs {p[5]:.2f}" for p in productos if p[6] > 0]
        self.producto_combo['values'] = lista
    
    def agregar_item_venta(self):
        seleccion = self.producto_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un producto")
            return
        
        try:
            cantidad = int(self.cantidad_var.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")
            return
        
        # Extraer ID del producto
        producto_id = int(seleccion.split(" - ")[0])
        producto = self.db.obtener_producto_por_id(producto_id)
        
        if producto[6] < cantidad:
            messagebox.showerror("Error", f"Stock insuficiente. Solo hay {producto[6]} unidades")
            return
        
        self.items_venta.append({
            'id_producto': producto_id,
            'nombre': producto[2],
            'cantidad': cantidad,
            'precio': producto[5]
        })
        
        self.actualizar_lista_items()
        self.producto_var.set("")
        self.cantidad_var.set("1")
    
    def actualizar_lista_items(self):
        for widget in self.lista_items_frame.winfo_children():
            widget.destroy()
        
        total = 0
        for i, item in enumerate(self.items_venta):
            subtotal = item['cantidad'] * item['precio']
            total += subtotal
            
            row = tk.Frame(self.lista_items_frame, bg='#f8f9fa', relief='solid', bd=1)
            row.pack(fill='x', pady=2)
            
            tk.Label(row, text=f"{item['nombre']}", bg='#f8f9fa', width=30, anchor='w').pack(side='left', padx=10)
            tk.Label(row, text=f"x{item['cantidad']}", bg='#f8f9fa', width=8).pack(side='left')
            tk.Label(row, text=f"Bs {item['precio']:.2f}", bg='#f8f9fa', width=12).pack(side='left')
            tk.Label(row, text=f"Bs {subtotal:.2f}", bg='#f8f9fa', width=12).pack(side='left')
            
            btn_eliminar = tk.Button(row, text="❌", bg='#dc3545', fg='white', 
                                     font=('Arial', 8), relief='flat', cursor='hand2',
                                     command=lambda idx=i: self.eliminar_item_venta(idx))
            btn_eliminar.pack(side='right', padx=5)
        
        if self.items_venta:
            iva = total * 0.16
            total_final = total + iva
            
            total_frame = tk.Frame(self.lista_items_frame, bg='white')
            total_frame.pack(fill='x', pady=10)
            
            tk.Label(total_frame, text=f"Subtotal: Bs {total:.2f}", font=('Arial', 10, 'bold'), bg='white').pack()
            tk.Label(total_frame, text=f"IVA (16%): Bs {iva:.2f}", font=('Arial', 10), bg='white').pack()
            tk.Label(total_frame, text=f"TOTAL: Bs {total_final:.2f}", font=('Arial', 12, 'bold'), fg='#1a3c34', bg='white').pack()
    
    def eliminar_item_venta(self, idx):
        del self.items_venta[idx]
        self.actualizar_lista_items()
    
    def registrar_venta(self):
        if not self.items_venta:
            messagebox.showerror("Error", "Agregue al menos un producto")
            return
        
        # Obtener ID del cliente
        cliente_seleccion = self.cliente_var.get()
        id_cliente = 0
        if cliente_seleccion and cliente_seleccion != "Cliente General":
            try:
                id_cliente = int(cliente_seleccion.split(" - ")[0])
            except:
                pass
        
        items = [{'id_producto': item['id_producto'], 'cantidad': item['cantidad'], 'precio': item['precio']} 
                 for item in self.items_venta]
        
        self.db.registrar_venta(id_cliente, items, self.metodo_pago_var.get())
        
        messagebox.showinfo("Éxito", "Venta registrada correctamente")
        self.items_venta = []
        self.actualizar_lista_items()
        self.cargar_ventas()
        self.cargar_productos_combo()
        self.mostrar_dashboard()
    
    def cargar_ventas(self):
        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)
        
        ventas = self.db.obtener_ventas()
        for v in ventas:
            self.tree_ventas.insert('', 'end', values=(
                v[0], v[1], v[2], f"Bs {v[3]:.2f}", f"Bs {v[4]:.2f}", f"Bs {v[5]:.2f}", v[6]
            ))
    
    # ==================== REPORTES ====================
    def mostrar_reportes(self):
        if self.usuario[4] != 'admin':
            messagebox.showerror("Acceso denegado", "Solo administradores")
            return
        
        self.limpiar_contenido()
        
        stats = self.db.obtener_estadisticas()
        
        # Resumen
        frame_resumen = tk.LabelFrame(self.frame_contenido, text="📊 Resumen General", 
                                      font=('Arial', 12, 'bold'), bg='white', fg='#1a3c34')
        frame_resumen.pack(fill='x', pady=(0, 20))
        
        resumen_texto = f"""
        📦 Total Productos: {stats['total_productos']}
        👥 Total Clientes: {stats['total_clientes']}
        💰 Total Ventas: {stats['total_ventas']}
        💵 Monto Total Facturado: Bs {stats['monto_ventas']:,.2f}
        ⚠️ Productos con Stock Bajo: {stats['stock_bajo']}
        """
        
        lbl_resumen = tk.Label(frame_resumen, text=resumen_texto, font=('Arial', 11), 
                               bg='white', justify='left', anchor='w')
        lbl_resumen.pack(padx=20, pady=15, anchor='w')
        
        # Ventas por mes
        frame_mes = tk.LabelFrame(self.frame_contenido, text="📈 Ventas por Mes", 
                                  font=('Arial', 12, 'bold'), bg='white', fg='#1a3c34')
        frame_mes.pack(fill='x', pady=(0, 20))
        
        ventas_mes = self.db.obtener_ventas_por_mes()
        
        for v in ventas_mes:
            mes_texto = f"{v[0]}: {v[1]} ventas - Bs {v[2]:,.2f}"
            tk.Label(frame_mes, text=mes_texto, font=('Arial', 10), bg='white', anchor='w').pack(padx=20, pady=5, fill='x')
        
        # Productos más vendidos
        frame_top = tk.LabelFrame(self.frame_contenido, text="🏆 Productos Más Vendidos", 
                                  font=('Arial', 12, 'bold'), bg='white', fg='#1a3c34')
        frame_top.pack(fill='x', pady=(0, 20))
        
        top_productos = self.db.obtener_productos_top()
        
        for p in top_productos:
            tk.Label(frame_top, text=f"{p[0]}: {p[1]} unidades", font=('Arial', 10), 
                     bg='white', anchor='w').pack(padx=20, pady=5, fill='x')
        
        # Productos con stock bajo
        frame_stock = tk.LabelFrame(self.frame_contenido, text="⚠️ Productos con Stock Bajo (Revisar)", 
                                    font=('Arial', 12, 'bold'), bg='white', fg='#dc3545')
        frame_stock.pack(fill='x', pady=(0, 20))
        
        stock_bajo = self.db.obtener_productos_stock_bajo()
        
        if stock_bajo:
            for s in stock_bajo:
                tk.Label(frame_stock, text=f"{s[1]} - {s[2]} | Stock: {s[6]} / Mínimo: {s[7]}", 
                         font=('Arial', 10), bg='white', fg='#dc3545', anchor='w').pack(padx=20, pady=5, fill='x')
        else:
            tk.Label(frame_stock, text="✅ No hay productos con stock bajo", 
                     font=('Arial', 10), bg='white', fg='green', anchor='w').pack(padx=20, pady=5, fill='x')