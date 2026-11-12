"""Conexión a la base de datos usando únicamente la interfaz de SQLModel."""
from sqlmodel import SQLModel, Session, create_engine
from config.settings import DATABASE_URL

# SQLite requiere esta opción para trabajar correctamente con FastAPI.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
# Crea el motor que SQLModel utilizará para abrir sesiones.
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def crear_tablas():
    """Crea las tablas declaradas en los modelos SQLModel importados."""
    SQLModel.metadata.create_all(engine)


def obtener_sesion():
    """Dependencia de FastAPI: abre una sesión y la cierra al terminar."""
    with Session(engine) as session:
        yield session
