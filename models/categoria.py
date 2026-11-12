"""Tabla de categorías bibliográficas."""
from typing import Optional
from sqlmodel import SQLModel, Field


class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Clave primaria.
    nombre: str = Field(index=True, unique=True, min_length=2, max_length=80)  # No duplicar.
    descripcion: Optional[str] = None  # Descripción opcional.
