"""Tabla de libros y cantidades de ejemplares."""
from typing import Optional
from sqlmodel import SQLModel, Field


class Libro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # ID interno.
    titulo: str = Field(index=True, min_length=1, max_length=180)  # Título del libro.
    isbn: str = Field(index=True, unique=True, min_length=10, max_length=20)  # ISBN único.
    autor_id: int = Field(foreign_key="autor.id")  # Referencia a autor.
    categoria_id: int = Field(foreign_key="categoria.id")  # Referencia a categoría.
    anio: Optional[int] = Field(default=None, ge=1400, le=2100)  # Año validado.
    total: int = Field(default=1, ge=1)  # Ejemplares que posee la biblioteca.
    disponibles: int = Field(default=1, ge=0)  # Ejemplares que se pueden prestar.
    descripcion: Optional[str] = None  # Resumen opcional.
