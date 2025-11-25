import sqlite3
import os

DB_NAME = "inventario.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    print(f"Creando base de datos: {DB_NAME} basada en Proyecto 7...")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usuario (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hash_password TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('Administrador', 'Vendedor', 'Jefe_Almacen')),
        activo INTEGER DEFAULT 1,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Categoria (
        id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        activo INTEGER DEFAULT 1
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Almacen (
        id_almacen INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        direccion TEXT,
        responsable TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Ubicacion (
        id_ubicacion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_almacen INTEGER,
        codigo_ubicacion TEXT NOT NULL,
        descripcion TEXT,
        FOREIGN KEY (id_almacen) REFERENCES Almacen(id_almacen)
    );
    """)

   
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Producto (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
        stock_actual INTEGER DEFAULT 0 CHECK (stock_actual >= 0),
        stock_minimo INTEGER DEFAULT 0 CHECK (stock_minimo >= 0),
        stock_maximo INTEGER DEFAULT 0 CHECK (stock_maximo >= stock_minimo),
        id_categoria INTEGER,
        id_ubicacion INTEGER,
        activo INTEGER DEFAULT 1,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria),
        FOREIGN KEY (id_ubicacion) REFERENCES Ubicacion(id_ubicacion)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Movimiento (
        id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_movimiento TEXT NOT NULL CHECK(tipo_movimiento IN ('Entrada', 'Salida', 'Ajuste')),
        cantidad INTEGER NOT NULL CHECK (cantidad > 0),
        fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
        motivo TEXT,
        referencia TEXT,
        id_producto INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        FOREIGN KEY (id_producto) REFERENCES Producto(id_producto),
        FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Alerta (
        id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_alerta TEXT NOT NULL CHECK(tipo_alerta IN ('Stock_Minimo', 'Stock_Maximo')),
        mensaje TEXT NOT NULL,
        fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        leida INTEGER DEFAULT 0,
        id_producto INTEGER NOT NULL,
        FOREIGN KEY (id_producto) REFERENCES Producto(id_producto)
    );
    """)

   
    print("Insertando datos de prueba del Proyecto 7...")

    users = [
        ('Admin Principal', 'admin@empresa.com', '$2y$10$hashedpassword', 'Administrador'),
        ('Vendedor 1', 'vendedor1@empresa.com', '$2y$10$hashedpassword', 'Vendedor'),
        ('Jefe Almacén', 'jefe.almacen@empresa.com', '$2y$10$hashedpassword', 'Jefe_Almacen')
    ]
    cursor.executemany("INSERT OR IGNORE INTO Usuario (nombre, email, hash_password, rol) VALUES (?, ?, ?, ?)", users)

    cats = [
        ('Electrónicos', 'Dispositivos electrónicos y accesorios'),
        ('Oficina', 'Material de oficina y papelería'),
        ('Limpieza', 'Productos de limpieza y mantenimiento')
    ]
    cursor.executemany("INSERT OR IGNORE INTO Categoria (nombre, descripcion) VALUES (?, ?)", cats)

    almacenes = [
        ('Almacén Central', 'Av. Principal 123, Salamanca', 'Juan Pérez'),
        ('Bodega Secundaria', 'Calle Secundaria 456, Irapuato', 'María García')
    ]
    cursor.executemany("INSERT OR IGNORE INTO Almacen (nombre, direccion, responsable) VALUES (?, ?, ?)", almacenes)

  
    ubicaciones = [
        (1, 'A-01-01', 'Estantería A, Nivel 1, Posición 1'),
        (1, 'A-01-02', 'Estantería A, Nivel 1, Posición 2'),
        (2, 'B-02-01', 'Estantería B, Nivel 2, Posición 1')
    ]
    cursor.executemany("INSERT OR IGNORE INTO Ubicacion (id_almacen, codigo_ubicacion, descripcion) VALUES (?, ?, ?)", ubicaciones)

    productos = [
        ('Laptop Dell i7', 'Laptop Dell Inspiron con procesador i7', 15000.00, 0, 5, 50, 1, 1),
        ('Mouse Inalámbrico', 'Mouse logitech inalámbrico', 450.50, 0, 10, 100, 1, 2),
        ('Resma Papel A4', 'Resma de papel bond A4 500 hojas', 120.00, 0, 20, 200, 2, 3)
    ]
   
    cursor.execute("""
    INSERT OR IGNORE INTO Producto (nombre, descripcion, precio_unitario, stock_minimo, stock_maximo, id_categoria, id_ubicacion) 
    VALUES 
    ('Laptop Dell i7', 'Laptop Dell Inspiron con procesador i7', 15000.00, 5, 50, 1, 1);
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO Producto (nombre, descripcion, precio_unitario, stock_minimo, stock_maximo, id_categoria, id_ubicacion) 
    VALUES 
    ('Mouse Inalámbrico', 'Mouse logitech inalámbrico', 450.50, 10, 100, 1, 2);
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO Producto (nombre, descripcion, precio_unitario, stock_minimo, stock_maximo, id_categoria, id_ubicacion) 
    VALUES 
    ('Resma Papel A4', 'Resma de papel bond A4 500 hojas', 120.00, 20, 200, 2, 3);
    """)

   
    movimientos = [
        ('Entrada', 50, 'Compra inicial', 1, 1),
        ('Entrada', 100, 'Compra inicial', 2, 1),
        ('Salida', 5, 'Venta a cliente', 1, 2)
    ]
    cursor.executemany("INSERT OR IGNORE INTO Movimiento (tipo_movimiento, cantidad, motivo, id_producto, id_usuario) VALUES (?, ?, ?, ?, ?)", movimientos)

   
    cursor.execute("UPDATE Producto SET stock_actual = 45 WHERE id_producto = 1")
    cursor.execute("UPDATE Producto SET stock_actual = 100 WHERE id_producto = 2")

    conn.commit()
    conn.close()
    print("¡Base de datos creada y poblada con éxito! Archivo: " + DB_NAME)

if __name__ == "__main__":
    create_database()