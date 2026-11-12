"""Tabla de préstamos y devoluciones."""
from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field


class Prestamo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # ID del préstamo.
    usuario_id: int = Field(foreign_key="usuario.id", index=True)  # Quién recibe el libro.
    libro_id: int = Field(foreign_key="libro.id", index=True)  # Libro prestado.
    fecha_prestamo: date = Field(default_factory=date.today)  # Fecha de registro.
    fecha_limite: date  # Fecha pactada de devolución.
    fecha_real: Optional[date] = None  # Se llena al devolver.
    estado: str = Field(default="activo", index=True)  # activo o devuelto.
