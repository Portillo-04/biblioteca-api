"""Endpoints de autores, categorías y libros."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from config.database import obtener_sesion
from models.usuario import Usuario
from models.autor import Autor
from models.categoria import Categoria
from models.libro import Libro
from schemas.esquemas import AutorCrear, CategoriaCrear, LibroCrear, LibroActualizar, LibroSalida
from services.seguridad import usuario_actual, roles_permitidos
from services.servicios import alta_autor, alta_categoria, alta_libro, editar_libro, borrar_libro

router = APIRouter(tags=["Catálogo"])

@router.post("/authors", response_model=Autor, status_code=201)
def crear_autor(datos: AutorCrear, session: Session = Depends(obtener_sesion),
                usuario: Usuario = Depends(roles_permitidos("admin", "bibliotecario"))):
    # Administrador y bibliotecario pueden ampliar el catálogo de autores.
    autor = Autor(nombre=datos.nombre.strip(), biografia=datos.biografia)
    session.add(autor); session.commit(); session.refresh(autor)
    return autor

@router.get("/authors", response_model=list[Autor])
def autores(session: Session = Depends(obtener_sesion), usuario: Usuario = Depends(usuario_actual)):
    # Cualquier usuario autenticado puede consultar autores.
    return session.exec(select(Autor)).all()

@router.post("/categories", response_model=Categoria, status_code=201)
def crear_categoria(datos: CategoriaCrear, session: Session = Depends(obtener_sesion),
                    usuario: Usuario = Depends(roles_permitidos("admin", "bibliotecario"))):
    # El servicio impide nombres de categoría duplicados.
    return alta_categoria(datos, session)

@router.get("/categories", response_model=list[Categoria])
def categorias(session: Session = Depends(obtener_sesion), usuario: Usuario = Depends(usuario_actual)):
    # El catálogo de categorías es de consulta para los tres roles.
    return session.exec(select(Categoria)).all()

@router.post("/books", response_model=LibroSalida, status_code=201)
def crear_libro(datos: LibroCrear, session: Session = Depends(obtener_sesion),
                usuario: Usuario = Depends(roles_permitidos("admin", "bibliotecario"))):
    # Servicio valida autor, categoría e ISBN antes de guardar.
    return alta_libro(datos, session)

@router.get("/books", response_model=list[LibroSalida])
def libros(q: str | None = None, disponibles: bool | None = None,
           session: Session = Depends(obtener_sesion), usuario: Usuario = Depends(usuario_actual)):
    # Los filtros son opcionales: texto del título y solo libros disponibles.
    consulta = select(Libro)
    if q: consulta = consulta.where(Libro.titulo.contains(q))
    if disponibles is True: consulta = consulta.where(Libro.disponibles > 0)
    return session.exec(consulta).all()

@router.get("/books/{libro_id}", response_model=LibroSalida)
def libro_detalle(libro_id: int, session: Session = Depends(obtener_sesion),
                  usuario: Usuario = Depends(usuario_actual)):
    libro = session.get(Libro, libro_id)
    if not libro: raise HTTPException(404, "Libro no encontrado.")
    return libro

@router.patch("/books/{libro_id}", response_model=LibroSalida)
def actualizar_libro(libro_id: int, datos: LibroActualizar,
                     session: Session = Depends(obtener_sesion),
                     usuario: Usuario = Depends(roles_permitidos("admin", "bibliotecario"))):
    libro = session.get(Libro, libro_id)
    if not libro: raise HTTPException(404, "Libro no encontrado.")
    return editar_libro(libro, datos.model_dump(exclude_unset=True), session)

@router.delete("/books/{libro_id}", status_code=204)
def eliminar_libro(libro_id: int, session: Session = Depends(obtener_sesion),
                   usuario: Usuario = Depends(roles_permitidos("admin"))):
    # Solo admin elimina y el servicio bloquea libros con historial.
    libro = session.get(Libro, libro_id)
    if not libro: raise HTTPException(404, "Libro no encontrado.")
    borrar_libro(libro, session)
    return None
