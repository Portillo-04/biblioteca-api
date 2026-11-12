"""Agrupa los routers para registrarlos desde main.py."""
from router.auth import router as auth_router
from router.usuarios import router as usuarios_router
from router.catalogo import router as catalogo_router
from router.prestamos import router as prestamos_router
