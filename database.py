# database.py - Base de datos SQLITE (funciona 100% sin internet)
import sqlite3
import os
import hashlib

class Database:
    def __init__(self):
        # La base de datos se guarda en la carpeta data (archivo local, sin internet)
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'autovidrio.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.crear_tablas()
    
    def crear_tablas(self):
        # Tabla de usuarios
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                rol TEXT DEFAULT 'almacen'
            )
        ''')
        
        # Tabla de productos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                categoria TEXT,
                precio_compra REAL NOT NULL,
                precio_venta REAL NOT NULL,
                stock_actual INTEGER DEFAULT 0,
                stock_minimo INTEGER DEFAULT 5
            )
        ''')
        
        # Tabla de clientes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                telefono TEXT,
                direccion TEXT,
                email TEXT
            )
        ''')
        
        # Tabla de ventas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subtotal REAL NOT NULL,
                iva REAL DEFAULT 0,
                total REAL NOT NULL,
                metodo_pago TEXT,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
            )
        ''')
        
        # Tabla de detalle ventas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER,
                id_producto INTEGER,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            )
        ''')
        
        # Insertar usuario administrador por defecto (si no existe)
        self.cursor.execute("SELECT COUNT(*) FROM usuarios")
        if self.cursor.fetchone()[0] == 0:
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO usuarios (nombre, apellido, email, password, rol)
                VALUES ('Admin', 'Sistema', 'admin@autovidrio.com', ?, 'admin')
            ''', (password_hash,))
            self.conn.commit()
    
    # ========== LOGIN ==========
    def verificar_login(self, email, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute('''
            SELECT id_usuario, nombre, apellido, email, rol 
            FROM usuarios WHERE email = ? AND password = ?
        ''', (email, password_hash))
        return self.cursor.fetchone()
    
    # ========== PRODUCTOS ==========
    def obtener_productos(self):
        self.cursor.execute("SELECT * FROM productos ORDER BY id_producto DESC")
        return self.cursor.fetchall()
    
    def agregar_producto(self, codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo):
        self.cursor.execute('''
            INSERT INTO productos (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo))
        self.conn.commit()
        return True
    
    def actualizar_producto(self, id_producto, codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo):
        self.cursor.execute('''
            UPDATE productos SET codigo=?, nombre=?, descripcion=?, categoria=?, 
            precio_compra=?, precio_venta=?, stock_actual=?, stock_minimo=?
            WHERE id_producto=?
        ''', (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo, id_producto))
        self.conn.commit()
    
    def eliminar_producto(self, id_producto):
        self.cursor.execute("DELETE FROM productos WHERE id_producto=?", (id_producto,))
        self.conn.commit()
    
    def obtener_producto_por_id(self, id_producto):
        self.cursor.execute("SELECT * FROM productos WHERE id_producto=?", (id_producto,))
        return self.cursor.fetchone()
    
    def actualizar_stock(self, id_producto, cantidad):
        self.cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto=?", (cantidad, id_producto))
        self.conn.commit()
    
    # ========== CLIENTES ==========
    def obtener_clientes(self):
        self.cursor.execute("SELECT * FROM clientes ORDER BY id_cliente DESC")
        return self.cursor.fetchall()
    
    def agregar_cliente(self, cedula, nombre, apellido, telefono, direccion, email):
        try:
            self.cursor.execute('''
                INSERT INTO clientes (cedula, nombre, apellido, telefono, direccion, email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cedula, nombre, apellido, telefono, direccion, email))
            self.conn.commit()
            return True, "Cliente agregado"
        except sqlite3.IntegrityError:
            return False, "Ya existe un cliente con esa cédula"
    
    def eliminar_cliente(self, id_cliente):
        self.cursor.execute("DELETE FROM clientes WHERE id_cliente=?", (id_cliente,))
        self.conn.commit()
    
    # ========== VENTAS ==========
    def registrar_venta(self, id_cliente, items, metodo_pago):
        subtotal = sum(item['precio'] * item['cantidad'] for item in items)
        iva = subtotal * 0.16
        total = subtotal + iva
        
        self.cursor.execute('''
            INSERT INTO ventas (id_cliente, subtotal, iva, total, metodo_pago)
            VALUES (?, ?, ?, ?, ?)
        ''', (id_cliente if id_cliente != 0 else None, subtotal, iva, total, metodo_pago))
        
        id_venta = self.cursor.lastrowid
        
        for item in items:
            self.cursor.execute('''
                INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_venta, item['id_producto'], item['cantidad'], item['precio'], item['precio'] * item['cantidad']))
            
            # Actualizar stock
            self.cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto=?", 
                                (item['cantidad'], item['id_producto']))
        
        self.conn.commit()
        return id_venta
    
    def obtener_ventas(self):
        self.cursor.execute('''
            SELECT v.id_venta, v.fecha_venta, 
                   COALESCE(c.nombre || ' ' || c.apellido, 'Cliente General') as cliente,
                   v.subtotal, v.iva, v.total, v.metodo_pago
            FROM ventas v
            LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
            ORDER BY v.id_venta DESC
            LIMIT 50
        ''')
        return self.cursor.fetchall()
    
    # ========== ESTADÍSTICAS ==========
    def obtener_estadisticas(self):
        # Total productos
        self.cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = self.cursor.fetchone()[0]
        
        # Total clientes
        self.cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = self.cursor.fetchone()[0]
        
        # Total ventas
        self.cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM ventas")
        ventas = self.cursor.fetchone()
        total_ventas = ventas[0]
        monto_ventas = ventas[1]
        
        # Productos stock bajo
        self.cursor.execute("SELECT COUNT(*) FROM productos WHERE stock_actual <= stock_minimo")
        stock_bajo = self.cursor.fetchone()[0]
        
        # Ventas hoy
        self.cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM ventas WHERE DATE(fecha_venta) = DATE('now')")
        ventas_hoy = self.cursor.fetchone()
        
        return {
            'total_productos': total_productos,
            'total_clientes': total_clientes,
            'total_ventas': total_ventas,
            'monto_ventas': monto_ventas,
            'stock_bajo': stock_bajo,
            'ventas_hoy_cantidad': ventas_hoy[0],
            'ventas_hoy_monto': ventas_hoy[1]
        }
    
    def obtener_ventas_por_mes(self):
        self.cursor.execute('''
            SELECT strftime('%Y-%m', fecha_venta) as mes, 
                   COUNT(*) as cantidad, 
                   COALESCE(SUM(total), 0) as total
            FROM ventas
            GROUP BY strftime('%Y-%m', fecha_venta)
            ORDER BY mes DESC
            LIMIT 6
        ''')
        return self.cursor.fetchall()
    
    def obtener_productos_top(self):
        self.cursor.execute('''
            SELECT p.nombre, COALESCE(SUM(dv.cantidad), 0) as total_vendido
            FROM productos p
            LEFT JOIN detalle_ventas dv ON p.id_producto = dv.id_producto
            GROUP BY p.id_producto
            ORDER BY total_vendido DESC
            LIMIT 10
        ''')
        return self.cursor.fetchall()
    
    def obtener_productos_stock_bajo(self):
        self.cursor.execute("SELECT * FROM productos WHERE stock_actual <= stock_minimo ORDER BY stock_actual ASC")
        return self.cursor.fetchall()
    
    def cerrar(self):
        self.conn.close()