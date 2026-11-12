"""MAIN: punto de entrada de FastAPI y registro de todos los routers."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.database import crear_tablas

# Importar los modelos antes de crear tablas registra cada clase SQLModel.
from models import usuario, autor, categoria, libro, prestamo  # noqa: F401
# Se importan los routers que contienen las rutas de cada módulo.
from router import auth_router, usuarios_router, catalogo_router, prestamos_router


@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    """Acciones realizadas al iniciar y cerrar el servidor."""
    crear_tablas()  # Crea las tablas faltantes sin borrar datos existentes.
    yield  # FastAPI atiende peticiones mientras el ciclo está suspendido.
    # Las sesiones se cierran individualmente al finalizar cada petición.


# Instancia principal: Uvicorn la busca con main:app.
app = FastAPI(
    title="Sistema Bibliotecario",
    version="1.0.0",
    lifespan=ciclo_vida
)


@app.get("/", tags=["Inicio"])
def inicio():
    # Endpoint público para comprobar que el servidor está levantado.
    return {"mensaje": "API del Sistema Bibliotecario funcionando", "docs": "/docs"}


# Registra las rutas de autenticación, usuarios, catálogo y préstamos.
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(catalogo_router)
app.include_router(prestamos_router)
