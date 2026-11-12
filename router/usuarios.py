"""Endpoints de administración de cuentas; todos requieren rol admin."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from config.database import obtener_sesion
from config.settings import ROLES
from models.usuario import Usuario
from schemas.esquemas import UsuarioAdminCrear, UsuarioSalida
from services.seguridad import roles_permitidos
from services.servicios import registrar_usuario

router = APIRouter(prefix="/users", tags=["Usuarios"])

@router.post("", response_model=UsuarioSalida, status_code=201)
def crear(datos: UsuarioAdminCrear, session: Session = Depends(obtener_sesion),
          admin: Usuario = Depends(roles_permitidos("admin"))):
    # Solo un administrador puede crear usuarios con rol elegido.
    return registrar_usuario(datos, session, datos.rol)

@router.get("", response_model=list[UsuarioSalida])
def listar(session: Session = Depends(obtener_sesion),
           admin: Usuario = Depends(roles_permitidos("admin"))):
    # El esquema de salida excluye el password_hash.
    return session.exec(select(Usuario)).all()

@router.patch("/{user_id}/role", response_model=UsuarioSalida)
def cambiar_rol(user_id: int, rol: str, session: Session = Depends(obtener_sesion),
                admin: Usuario = Depends(roles_permitidos("admin"))):
    # Verifica que el rol solicitado sea uno de los tres definidos.
    if rol not in ROLES: raise HTTPException(422, "Rol no válido.")
    usuario = session.get(Usuario, user_id)
    if not usuario: raise HTTPException(404, "Usuario no encontrado.")
    usuario.rol = rol; session.add(usuario); session.commit(); session.refresh(usuario)
    return usuario

@router.patch("/{user_id}/status", response_model=UsuarioSalida)
def cambiar_estado(user_id: int, activo: bool, session: Session = Depends(obtener_sesion),
                   admin: Usuario = Depends(roles_permitidos("admin"))):
    # Deshabilita o reactiva una cuenta sin borrar su historial.
    usuario = session.get(Usuario, user_id)
    if not usuario: raise HTTPException(404, "Usuario no encontrado.")
    usuario.activo = activo; session.add(usuario); session.commit(); session.refresh(usuario)
    return usuario
