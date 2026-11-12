"""Hash de contraseñas, tokens JWT y control de acceso por roles."""
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from config.settings import SECRET_KEY, ALGORITHM, TOKEN_MINUTES
from config.database import obtener_sesion
from models.usuario import Usuario

# Swagger usará esta ruta para solicitar el token de acceso.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def hash_password(password: str) -> str:
    # bcrypt añade una sal aleatoria; el hash no permite recuperar la contraseña.
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar_password(password: str, hashed: str) -> bool:
    # Compara la contraseña enviada con el hash almacenado.
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False


def crear_token(usuario: Usuario) -> str:
    # 'sub' identifica al usuario; 'exp' limita la vigencia del token.
    ahora = datetime.now(timezone.utc)
    payload = {"sub": str(usuario.id), "iat": ahora,
               "exp": ahora + timedelta(minutes=TOKEN_MINUTES)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def usuario_actual(token: str = Depends(oauth2_scheme), session: Session = Depends(obtener_sesion)):
    # Error uniforme para tokens incorrectos, expirados o cuentas deshabilitadas.
    error = HTTPException(status_code=401, detail="Token inválido, expirado o usuario inactivo.",
                          headers={"WWW-Authenticate": "Bearer"})
    try:
        # jose verifica firma y expiración antes de entregar el contenido.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub", ""))
    except (JWTError, ValueError, TypeError):
        raise error
    # Se vuelve a consultar la cuenta para comprobar que sigue activa.
    usuario = session.get(Usuario, user_id)
    if not usuario or not usuario.activo:
        raise error
    return usuario


def roles_permitidos(*roles):
    # Dependencia que puede colocarse en cualquier endpoint restringido.
    def validar(usuario: Usuario = Depends(usuario_actual)):
        if usuario.rol not in roles:
            raise HTTPException(
                status_code=403, detail="No tienes permiso para esta operación.")
        return usuario
    return validar
