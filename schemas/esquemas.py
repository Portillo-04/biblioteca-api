"""Esquemas Pydantic: validan entradas y filtran los datos de salida."""
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UsuarioAdminCrear(UsuarioCrear):
    rol: str = "usuario"  # Solo la ruta protegida de admin acepta asignar rol.

class UsuarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    correo: str
    rol: str
    activo: bool  # No exponer password_hash.

class LoginEntrada(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=1, max_length=128)

class TokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioSalida

class AutorCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    biografia: Optional[str] = None

class CategoriaCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    descripcion: Optional[str] = None

class LibroCrear(BaseModel):
    titulo: str = Field(min_length=1, max_length=180)
    isbn: str = Field(min_length=10, max_length=20)
    autor_id: int = Field(gt=0)
    categoria_id: int = Field(gt=0)
    anio: Optional[int] = Field(default=None, ge=1400, le=2100)
    total: int = Field(default=1, ge=1)
    descripcion: Optional[str] = None

class LibroActualizar(BaseModel):
    titulo: Optional[str] = Field(default=None, min_length=1, max_length=180)
    isbn: Optional[str] = Field(default=None, min_length=10, max_length=20)
    autor_id: Optional[int] = Field(default=None, gt=0)
    categoria_id: Optional[int] = Field(default=None, gt=0)
    anio: Optional[int] = Field(default=None, ge=1400, le=2100)
    total: Optional[int] = Field(default=None, ge=1)
    descripcion: Optional[str] = None

class LibroSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    isbn: str
    autor_id: int
    categoria_id: int
    anio: Optional[int]
    total: int
    disponibles: int
    descripcion: Optional[str]

class PrestamoCrear(BaseModel):
    libro_id: int = Field(gt=0)
    usuario_id: Optional[int] = Field(default=None, gt=0)
    fecha_limite: date

class PrestamoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_limite: date
    fecha_real: Optional[date]
    estado: str
