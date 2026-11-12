"""Configuración central: variables de entorno, seguridad y base de datos."""
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env durante el desarrollo local.
load_dotenv()

# Clave usada para firmar JWT. Debe cambiarse antes de desplegar el proyecto.
SECRET_KEY = os.getenv("SECRET_KEY", "CAMBIAR_POR_UN_SECRETO_LARGO_Y_ALEATORIO")
# Algoritmo simétrico para firmar y verificar los tokens.
ALGORITHM = "HS256"
# Minutos durante los que un token será válido.
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "30"))
# SQLite crea el archivo biblioteca.db en el directorio de ejecución.
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@127.0.0.1:3306/biblioteca")
# Únicos roles aceptados por el sistema.
ROLES = ("admin", "bibliotecario", "usuario")
