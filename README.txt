PROYECTO FINAL - SISTEMA DE CONTROL DE INVENTARIOS
Alumno: Daniel Josafath Manrique Mejía
Asignatura: Sistemas de Información
Fecha: Noviembre 2025

DESCRIPCIÓN:
Sistema web para la gestión administrativa de inventarios, permitiendo el control 
de stock (entradas/salidas), gestión de categorías, alertas automáticas de 
reabastecimiento y valoración financiera del almacén.

TECNOLOGÍAS:
- Python 3 (Lógica y Backend con Flask)
- SQLite (Base de Datos Relacional Normalizada)
- HTML5/CSS3 (Interfaz Gráfica estilo Dashboard)

INSTRUCCIONES DE INSTALACIÓN Y EJECUCIÓN (macOS)

1. Abrir la terminal en la carpeta del proyecto:
   cd ruta/a/tu/carpeta/SistemaInventariosWeb

2. Crear y activar el entorno virtual (Opcional pero recomendado):
   python3 -m venv venv
   source venv/bin/activate

3. Instalar las dependencias necesarias:
   pip install Flask werkzeug

4. Inicializar la Base de Datos (Solo la primera vez):
   python3 setup_database.py
   (Esto creará el archivo 'inventario.db' con datos de prueba iniciales).

5. Ejecutar la aplicación:
   python3 app.py

6. Abrir el navegador web e ingresar a:
   http://127.0.0.1:5000

CREDENCIALES DE ACCESO (LOGIN)
Usuario Administrador:
- Correo: admin@empresa.com
- Contraseña: admin123

FUNCIONALIDADES PRINCIPALES:
1. Dashboard: Vista general con estadísticas.
2. Productos: CRUD completo (Crear, Leer, Buscar).
3. Movimientos: Registro de Entradas (Compras) y Salidas (Ventas) con validación de stock.
4. Categorías: Gestión dinámica de familias de productos.
5. Alertas: Reporte automático de productos con stock crítico.
6. Finanzas: Reporte de valoración monetaria del inventario.