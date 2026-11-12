"""Tabla de autores asociados a libros."""
from typing import Optional
from sqlmodel import SQLModel, Field


class Autor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Clave primaria.
    nombre: str = Field(index=True, min_length=2, max_length=120)  # Nombre del autor.
    biografia: Optional[str] = None  # Dato opcional.
