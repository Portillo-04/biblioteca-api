"""Endpoints públicos de registro/login y endpoint de perfil protegido."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from config.database import obtener_sesion
from models.usuario import Usuario
from schemas.esquemas import UsuarioCrear, UsuarioSalida, LoginEntrada, TokenSalida
from services.seguridad import hash_password, verificar_password, crear_token, usuario_actual
from services.servicios import registrar_usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def autenticar(correo: str, password: str, session: Session) -> dict:
    """Valida las credenciales y devuelve el token con los datos del usuario."""
    # Normaliza el correo para evitar diferencias por mayúsculas.
    correo = correo.lower()
    usuario = session.exec(select(Usuario).where(
        Usuario.correo == correo)).first()
    # Mensaje genérico: no informa si el correo está registrado.
    if not usuario or not verificar_password(password, usuario.password_hash) or not usuario.activo:
        raise HTTPException(401, "Correo o contraseña incorrectos.")
    return {"access_token": crear_token(usuario), "token_type": "bearer", "usuario": usuario}


@router.post("/register", response_model=UsuarioSalida, status_code=201)
def registro(datos: UsuarioCrear, session: Session = Depends(obtener_sesion)):
    # El servicio asigna siempre rol usuario al registro abierto.
    return registrar_usuario(datos, session, "usuario")


@router.post("/login", response_model=TokenSalida)
def login(datos: LoginEntrada, session: Session = Depends(obtener_sesion)):
    # Login normal en JSON: {"correo": "...", "password": "..."}.
    return autenticar(str(datos.correo), datos.password, session)


@router.post("/token", response_model=TokenSalida, include_in_schema=False)
def token(datos: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(obtener_sesion)):
    # Ruta para el botón Authorize de Swagger (formulario OAuth2).
    # En OAuth2 el campo "username" lleva el correo.
    return autenticar(datos.username, datos.password, session)


@router.get("/me", response_model=UsuarioSalida)
def perfil(usuario: Usuario = Depends(usuario_actual)):
    # Devuelve el perfil del usuario autenticado sin exponer el hash.
    return usuario
