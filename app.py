from flask import Flask, render_template, g, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash 

import config 

app = Flask(__name__)
app.secret_key = config.SECRET_KEY  
DATABASE = config.DATABASE_PATH    

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row 
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/login', methods=('GET', 'POST'))
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = get_db().cursor()
        cur.execute("SELECT * FROM Usuario WHERE email = ?", (email,))
        user = cur.fetchone()

        if user is None:
            error = 'Correo incorrecto.'
        elif not check_password_hash(user['hash_password'], password):
            error = 'Contraseña incorrecta.'
        else:
            session.clear()
            session['user_id'] = user['id_usuario']
            session['user_name'] = user['nombre']
            session['user_role'] = user['rol']
            return redirect(url_for('index'))

    return render_template('auth/login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.before_request
def require_login():
    rutas_libres = ['login', 'static']
    if request.endpoint not in rutas_libres and 'user_id' not in session:
        return redirect(url_for('login'))


@app.route('/')
def index():
    return listar_productos()

@app.route('/productos')
def listar_productos():
    cur = get_db().cursor()
    
    busqueda = request.args.get('q')

    if busqueda:
       
        query = """
            SELECT p.id_producto, p.nombre, p.descripcion, p.precio_unitario, 
                   p.stock_actual, p.stock_minimo, c.nombre as categoria, u.codigo_ubicacion
            FROM Producto p
            LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
            LEFT JOIN Ubicacion u ON p.id_ubicacion = u.id_ubicacion
            WHERE p.activo = 1 AND p.nombre LIKE ?
        """
        parametro = '%' + busqueda + '%'
        cur.execute(query, (parametro,))
    else:
        query = """
            SELECT p.id_producto, p.nombre, p.descripcion, p.precio_unitario, 
                   p.stock_actual, p.stock_minimo, c.nombre as categoria, u.codigo_ubicacion
            FROM Producto p
            LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
            LEFT JOIN Ubicacion u ON p.id_ubicacion = u.id_ubicacion
            WHERE p.activo = 1
        """
        cur.execute(query)
    
    productos = cur.fetchall()
    return render_template('productos/lista.html', productos=productos)

@app.route('/productos/nuevo', methods=('GET', 'POST'))
def nuevo_producto():
    cur = get_db().cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock_min = request.form['stock_min']
        stock_max = request.form['stock_max'] 
        categoria = request.form['categoria']
        ubicacion = request.form['ubicacion']

        if int(stock_max) < int(stock_min):
            return "Error: El Stock Máximo debe ser mayor al Mínimo", 400

        try:
            cur.execute("""
                INSERT INTO Producto (nombre, descripcion, precio_unitario, stock_minimo, stock_maximo, id_categoria, id_ubicacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nombre, descripcion, precio, stock_min, stock_max, categoria, ubicacion))
            get_db().commit()
            return redirect(url_for('listar_productos'))
        except sqlite3.IntegrityError as e:
            return f"Error de integridad de datos: {e}", 400

    cur.execute("SELECT * FROM Categoria")
    categorias = cur.fetchall()
    cur.execute("SELECT * FROM Ubicacion")
    ubicaciones = cur.fetchall()
    
    @app.route('/categorias', methods=('GET', 'POST'))
    def gestionar_categorias():
        cur = get_db().cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        
        try:
            cur.execute("INSERT INTO Categoria (nombre, descripcion) VALUES (?, ?)", 
                        (nombre, descripcion))
            get_db().commit()
            flash("Categoría agregada correctamente") 
            return redirect(url_for('gestionar_categorias'))
        except sqlite3.Error as e:
            return f"Error: {e}", 400

    cur.execute("SELECT * FROM Categoria WHERE activo = 1")
    categorias = cur.fetchall()
    return render_template('productos/categorias.html', categorias=categorias)
    
    return render_template('productos/nuevo.html', categorias=categorias, ubicaciones=ubicaciones)
@app.route('/movimientos/entrada', methods=('GET', 'POST'))
def registrar_entrada():
    cur = get_db().cursor()

    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = int(request.form['cantidad'])
        motivo = request.form['motivo']
        id_usuario = request.form['id_usuario']

        try:
            cur.execute("""
                INSERT INTO Movimiento (tipo_movimiento, cantidad, motivo, id_producto, id_usuario)
                VALUES ('Entrada', ?, ?, ?, ?)
            """, (cantidad, motivo, id_producto, id_usuario))

            cur.execute("""
                UPDATE Producto 
                SET stock_actual = stock_actual + ? 
                WHERE id_producto = ?
            """, (cantidad, id_producto))
            
            get_db().commit()
            return redirect(url_for('listar_productos'))
            
        except sqlite3.Error as e:
            return f"Error en la base de datos: {e}", 400

    cur.execute("SELECT id_producto, nombre, stock_actual FROM Producto WHERE activo = 1")
    productos = cur.fetchall()
    return render_template('movimientos/entrada.html', productos=productos)
@app.route('/movimientos/salida', methods=('GET', 'POST'))
def registrar_salida():
    cur = get_db().cursor()
    error = None

    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = int(request.form['cantidad'])
        motivo = request.form['motivo']
        id_usuario = request.form['id_usuario']

        cur.execute("SELECT stock_actual FROM Producto WHERE id_producto = ?", (id_producto,))
        producto = cur.fetchone()

        if producto is None:
            error = "Producto no encontrado."
        elif producto['stock_actual'] < cantidad:
            error = f"¡Error! Stock insuficiente. Solo tienes {producto['stock_actual']} disponibles."
        else:
            try:
                cur.execute("""
                    INSERT INTO Movimiento (tipo_movimiento, cantidad, motivo, id_producto, id_usuario)
                    VALUES ('Salida', ?, ?, ?, ?)
                """, (cantidad, motivo, id_producto, id_usuario))

                cur.execute("""
                    UPDATE Producto 
                    SET stock_actual = stock_actual - ? 
                    WHERE id_producto = ?
                """, (cantidad, id_producto))
                
                get_db().commit()
                return redirect(url_for('listar_productos'))
            except sqlite3.Error as e:
                error = f"Error de base de datos: {e}"

    cur.execute("SELECT id_producto, nombre, stock_actual FROM Producto WHERE activo = 1")
    productos = cur.fetchall()
    return render_template('movimientos/salida.html', productos=productos, error=error)
@app.route('/reportes/alertas')
def ver_alertas():
    cur = get_db().cursor()
    
    cur.execute("""
        SELECT p.nombre, p.stock_actual, p.stock_minimo, c.nombre as categoria
        FROM Producto p
        JOIN Categoria c ON p.id_categoria = c.id_categoria
        WHERE p.stock_actual <= p.stock_minimo AND p.activo = 1
    """)
    alertas = cur.fetchall()
    
    return render_template('reportes/alertas.html', alertas=alertas)

@app.route('/categorias', methods=('GET', 'POST'))
def gestionar_categorias():
    cur = get_db().cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        
        try:
            cur.execute("INSERT INTO Categoria (nombre, descripcion) VALUES (?, ?)", 
                        (nombre, descripcion))
            get_db().commit()
            return redirect(url_for('gestionar_categorias'))
        except sqlite3.Error as e:
            return f"Error: {e}", 400

    cur.execute("SELECT * FROM Categoria WHERE activo = 1")
    categorias = cur.fetchall()
    return render_template('productos/categorias.html', categorias=categorias)

@app.route('/reportes/valorizacion')
def reporte_valorizacion():
    cur = get_db().cursor()
    
    query = """
        SELECT nombre, precio_unitario, stock_actual, 
               (precio_unitario * stock_actual) as subtotal 
        FROM Producto 
        WHERE activo = 1
    """
    cur.execute(query)
    datos = cur.fetchall()
    
    gran_total = sum(item['subtotal'] for item in datos)
    
    return render_template('reportes/valorizacion.html', datos=datos, gran_total=gran_total)
@app.route('/reportes/inventario')
def reporte_inventario():
    cur = get_db().cursor()
    
    query = """
        SELECT p.nombre, p.stock_actual, c.nombre as categoria, u.codigo_ubicacion, u.descripcion as ubicacion_desc
        FROM Producto p
        LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
        LEFT JOIN Ubicacion u ON p.id_ubicacion = u.id_ubicacion
        WHERE p.activo = 1
        ORDER BY u.codigo_ubicacion ASC
    """
    cur.execute(query)
    datos = cur.fetchall()
    
    return render_template('reportes/inventario.html', datos=datos)
if __name__ == '__main__':
    app.run(debug=True, port=5000)