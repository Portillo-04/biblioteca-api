"""Tabla de usuarios: almacena datos públicos y hash de contraseña."""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # ID autogenerado.
    nombre: str = Field(min_length=2, max_length=120)  # Nombre para mostrar.
    correo: str = Field(index=True, unique=True, max_length=160)  # Correo único.
    password_hash: str  # Nunca se guarda la contraseña original.
    rol: str = Field(default="usuario", index=True)  # admin, bibliotecario o usuario.
    activo: bool = True  # Una cuenta inactiva no puede autenticarse.
    creado_en: datetime = Field(default_factory=datetime.utcnow)  # Fecha de alta.
