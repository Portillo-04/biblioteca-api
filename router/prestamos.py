"""Endpoints para crear, consultar y devolver préstamos."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from config.database import obtener_sesion
from models.usuario import Usuario
from models.libro import Libro
from models.prestamo import Prestamo
from schemas.esquemas import PrestamoCrear, PrestamoSalida
from services.seguridad import usuario_actual
from services.servicios import crear_prestamo, devolver_prestamo

router = APIRouter(prefix="/loans", tags=["Préstamos"])

@router.post("", response_model=PrestamoSalida, status_code=201)
def prestar(datos: PrestamoCrear, session: Session = Depends(obtener_sesion),
            usuario: Usuario = Depends(usuario_actual)):
    # Usuario normal solo puede pedir para sí mismo; staff puede indicar usuario_id.
    if usuario.rol == "usuario":
        if datos.usuario_id is not None and datos.usuario_id != usuario.id:
            raise HTTPException(403, "Solo puedes solicitar préstamos para ti.")
        destino = usuario.id
    else:
        if datos.usuario_id is None:
            raise HTTPException(422, "Admin/bibliotecario deben enviar usuario_id.")
        destino = datos.usuario_id
    return crear_prestamo(datos.libro_id, destino, datos.fecha_limite, session)

@router.get("", response_model=list[PrestamoSalida])
def listar(activos: bool | None = None, session: Session = Depends(obtener_sesion),
           usuario: Usuario = Depends(usuario_actual)):
    # Admin y bibliotecario ven todo; usuario ve solo sus propios registros.
    consulta = select(Prestamo)
    if usuario.rol == "usuario": consulta = consulta.where(Prestamo.usuario_id == usuario.id)
    if activos is True: consulta = consulta.where(Prestamo.estado == "activo")
    elif activos is False: consulta = consulta.where(Prestamo.estado == "devuelto")
    return session.exec(consulta).all()

@router.post("/{prestamo_id}/return", response_model=PrestamoSalida)
def devolver(prestamo_id: int, session: Session = Depends(obtener_sesion),
             usuario: Usuario = Depends(usuario_actual)):
    prestamo = session.get(Prestamo, prestamo_id)
    if not prestamo: raise HTTPException(404, "Préstamo no encontrado.")
    # Un usuario no puede alterar el préstamo de otra persona.
    if usuario.rol == "usuario" and prestamo.usuario_id != usuario.id:
        raise HTTPException(403, "No puedes devolver préstamos de otra persona.")
    return devolver_prestamo(prestamo, session)
