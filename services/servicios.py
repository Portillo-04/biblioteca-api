"""Servicios: reglas de negocio separadas de los endpoints HTTP."""
from datetime import date
from fastapi import HTTPException
from sqlmodel import Session, select
from models.usuario import Usuario
from models.autor import Autor
from models.categoria import Categoria
from models.libro import Libro
from models.prestamo import Prestamo
from services.seguridad import hash_password
from config.settings import ROLES


def registrar_usuario(datos, session: Session, rol="usuario"):
    # Comprueba que el correo no esté ocupado antes de insertar.
    correo = str(datos.correo).lower()
    if session.exec(select(Usuario).where(Usuario.correo == correo)).first():
        raise HTTPException(409, "El correo ya está registrado.")
    if rol not in ROLES:
        raise HTTPException(422, "Rol no válido.")
    # Almacena únicamente el hash, nunca la contraseña original.
    usuario = Usuario(nombre=datos.nombre.strip(), correo=correo,
                      password_hash=hash_password(datos.password), rol=rol)
    session.add(usuario); session.commit(); session.refresh(usuario)
    return usuario


def alta_autor(datos, session: Session):
    autor = Autor(nombre=datos.nombre.strip(), biografia=datos.biografia)
    session.add(autor); session.commit(); session.refresh(autor)
    return autor


def alta_categoria(datos, session: Session):
    nombre = datos.nombre.strip()
    if session.exec(select(Categoria).where(Categoria.nombre == nombre)).first():
        raise HTTPException(409, "La categoría ya existe.")
    categoria = Categoria(nombre=nombre, descripcion=datos.descripcion)
    session.add(categoria); session.commit(); session.refresh(categoria)
    return categoria


def alta_libro(datos, session: Session):
    # Las referencias deben existir para evitar libros huérfanos.
    if not session.get(Autor, datos.autor_id):
        raise HTTPException(404, "Autor no encontrado.")
    if not session.get(Categoria, datos.categoria_id):
        raise HTTPException(404, "Categoría no encontrada.")
    if session.exec(select(Libro).where(Libro.isbn == datos.isbn)).first():
        raise HTTPException(409, "El ISBN ya está registrado.")
    # Inicialmente todos los ejemplares están disponibles.
    libro = Libro(**datos.model_dump(), disponibles=datos.total)
    session.add(libro); session.commit(); session.refresh(libro)
    return libro


def editar_libro(libro: Libro, cambios: dict, session: Session):
    # Comprueba referencias y unicidad del ISBN cuando se modifican.
    if "autor_id" in cambios and not session.get(Autor, cambios["autor_id"]):
        raise HTTPException(404, "Autor no encontrado.")
    if "categoria_id" in cambios and not session.get(Categoria, cambios["categoria_id"]):
        raise HTTPException(404, "Categoría no encontrada.")
    if "isbn" in cambios:
        repetido = session.exec(select(Libro).where(Libro.isbn == cambios["isbn"], Libro.id != libro.id)).first()
        if repetido: raise HTTPException(409, "ISBN ya utilizado por otro libro.")
    # Calcula cuántos ejemplares están prestados para proteger el inventario.
    if "total" in cambios:
        prestados = libro.total - libro.disponibles
        if cambios["total"] < prestados:
            raise HTTPException(409, "No se puede fijar un total menor que los ejemplares prestados.")
        libro.disponibles = cambios["total"] - prestados
    for campo, valor in cambios.items():
        if campo != "total": setattr(libro, campo, valor)
    session.add(libro); session.commit(); session.refresh(libro)
    return libro


def borrar_libro(libro: Libro, session: Session):
    # Conserva trazabilidad: impide borrar libros con préstamos históricos.
    historial = session.exec(select(Prestamo).where(Prestamo.libro_id == libro.id)).first()
    if historial: raise HTTPException(409, "No se puede borrar: existe historial de préstamos.")
    session.delete(libro); session.commit()


def crear_prestamo(libro_id: int, usuario_id: int, fecha_limite: date, session: Session):
    # El usuario debe existir y estar activo.
    usuario = session.get(Usuario, usuario_id)
    if not usuario or not usuario.activo: raise HTTPException(404, "Usuario no encontrado o inactivo.")
    # El libro debe existir y tener unidades libres.
    libro = session.get(Libro, libro_id)
    if not libro: raise HTTPException(404, "Libro no encontrado.")
    if libro.disponibles < 1: raise HTTPException(409, "No hay ejemplares disponibles.")
    if fecha_limite <= date.today(): raise HTTPException(422, "La fecha límite debe ser futura.")
    # Actualiza inventario y préstamo dentro de la misma sesión.
    libro.disponibles -= 1
    prestamo = Prestamo(usuario_id=usuario_id, libro_id=libro_id, fecha_limite=fecha_limite)
    session.add(libro); session.add(prestamo); session.commit(); session.refresh(prestamo)
    return prestamo


def devolver_prestamo(prestamo: Prestamo, session: Session):
    # Evita registrar dos devoluciones para el mismo préstamo.
    if prestamo.estado != "activo": raise HTTPException(409, "El préstamo ya fue devuelto.")
    libro = session.get(Libro, prestamo.libro_id)
    if not libro: raise HTTPException(404, "Libro asociado no encontrado.")
    prestamo.estado = "devuelto"
    prestamo.fecha_real = date.today()
    # Nunca permite que disponibles supere el total de ejemplares.
    libro.disponibles = min(libro.total, libro.disponibles + 1)
    session.add(prestamo); session.add(libro); session.commit(); session.refresh(prestamo)
    return prestamo
