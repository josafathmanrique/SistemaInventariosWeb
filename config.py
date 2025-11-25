import os

# Configuración de seguridad y base de datos
SECRET_KEY = 'clave_super_secreta_para_login' as
DATABASE_NAME = 'inventario.db'

# Obtener la ruta absoluta del archivo (para evitar errores si ejecutas desde otra carpeta)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)