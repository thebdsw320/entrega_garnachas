from fastapi import APIRouter, Body, Depends, Path, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from database.models import Usuario, Orden
from database.schemas import OrdenBase, EstadoOrden
from database.db import Session, engine

session = Session(bind=engine)

ruteador_ordenes = APIRouter(
    prefix='/ordenes',
    tags=['Órdenes']
)

@ruteador_ordenes.post(
    path='/',
    summary='Ordena algo',
    status_code=status.HTTP_201_CREATED,
    response_model=OrdenBase,
    response_model_exclude={'id_usuario'}
    )
def ordenar(orden: OrdenBase, Authorize: AuthJWT =  Depends()):
    """
    # Ordenar
    
    ## Ordenar un producto, requiere de un token de acceso 
    
    Parámetros
    - **cantidad**: número de piezas que quieres
    - **guisados**: guisados que puedes elegir; opciones -> [TINGA, CARNE, POLLO, CHAMPIÑONES, COMBINADO]
    - **tipo**: tipo de comida que puedes elegir; opciones -> [QUESADILLA, HUARACHE, SOPE]

    Retorna un JSON con la orden que acabas de pedir:
    - **id**: ID de la orden
    - **estado**: estado de la orden; -> puede ser [PROCESANDO, EN RUTA, ENTREGADO]
    - **cantidad**: número de piezas que quieres
    - **guisados**: guisados que puedes elegir; opciones -> [TINGA, CARNE, POLLO, CHAMPIÑONES, COMBINADO]
    - **tipo**: tipo de comida que puedes elegir; opciones -> [QUESADILLA, HUARACHE, SOPE]
    """
    try:
        Authorize.jwt_required()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token Invalido'
        )
    
    usuario_actual = Authorize.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()
    
    nueva_orden = Orden(
        cantidad = orden.cantidad,
        guisados = orden.guisados,
        tipo = orden.tipo
    )
    
    nueva_orden.usuario = usuario
    session.add(nueva_orden)
    
    result = session.execute(
        select(Orden.id).where(Usuario.username == usuario.username)
    )
    
    session.commit()
    
    return OrdenBase(cantidad=orden.cantidad, guisados=orden.guisados, tipo=orden.tipo, estado=orden.estado, id=result.all()[-1][0])
    
    
@ruteador_ordenes.get(
    path='/',
    summary='Muestra todas las órdenes',
    status_code=status.HTTP_200_OK,
    tags=['Solo Administración']
    )
def ordenar(Authorize: AuthJWT =  Depends()):
    """
    # Órdenes
    
    ## Lista todas las órdenes, requiere de un token de acceso y que el usuario sea administrador
    """
    try:
        Authorize.jwt_required()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token Invalido'
        )

    usuario_actual = Authorize.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()
    
    if usuario.es_admin:
        ordenes = session.query(Orden).all()
        return jsonable_encoder(ordenes)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='No eres administrador'
    )

@ruteador_ordenes.delete(
    path='/{id_orden}',
    status_code=status.HTTP_200_OK,
    summary='Borrar una orden'
    )
def borrar_orden(id_orden: int = Path(..., gt=0), Authorize: AuthJWT = Depends()):
    """
    # Borrar orden
    
    ## Borra una orden
    
    Parámetros
    -**id_orden**: ID de la orden = Path Parameter
    """
    try: 
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token inválido o token no proporcionado'
        )
    
    usuario_actual = Authorize.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()
    orden = session.query(Orden).filter(Orden.id == id_orden).first()
    
    if orden:
        if orden.id_usuario == usuario.id or usuario.es_admin:
            session.delete(orden)
            session.commit()
            
            return {
                'Mensaje': f'La orden {id_orden} fue eliminada exitosamente'
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'No puedes borrar la orden {id_orden} porque no te pertenece y/o no eres administrador'
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'La orden con ID {id_orden} no existe'
    )
    
@ruteador_ordenes.get(
    path='/usuario',
    status_code=status.HTTP_200_OK,
    summary='Muestra todas las órdenes del usuario actual'
)
def mostrar_ordenes_usuario(Authorize: AuthJWT = Depends()):
    """
    # Mostrar órdenes
    
    ## Muestra todas las órdenes del usuario actual, requiere de un token de acceso
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token inválido o token no proporcionado'
        )
    
    usuario_actual = Authorize.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()
    ordenes = session.query(Orden).filter(Orden.id_usuario == usuario.id).all()
    
    return jsonable_encoder(ordenes)

@ruteador_ordenes.get(
    path='/usuarios/{id_usuario}',
    status_code=status.HTTP_200_OK,
    summary='Muestra todas las órdenes de un usuario',
    tags=['Solo Administración']
)
def ordenes_usuario(id_usuario: int = Path(...), Authorize: AuthJWT = Depends()):
    """
    # Mostrar órdenes
    
    ## Muestra todas las órdenes de un usuario con su ID, requiere de un token de acceso y que el usuario sea administrador
    
    Parámetros
    - **id_usuario**: ID del usuario = Path Parameter
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token inválido o token no proporcionado'
        )
    
    usuario_actual = Authorize.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()
    
    if usuario.es_admin:
        ordenes = session.query(Orden).filter(Orden.id_usuario == id_usuario).all()
    
        return jsonable_encoder(ordenes)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='No eres administrador'
    )

@ruteador_ordenes.get(
    path='/{id_orden}',
    status_code=status.HTTP_200_OK,
    summary='Muestra una orden en específico',
    tags=['Solo Administración']
)
def mostar_orden(id_orden: int = Path(...), Authorization: AuthJWT = Depends()):
    """
    # Órdenes
    
    ## Muestra una orden con un ID específico, requiere ser administrador
    
    Parámetros
    - **id_orden**: ID de la orden a buscar = Path Parameter
    """
    try:
        Authorization.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token inválido o token no proporcionado'
        )
    
    usuario_actual = Authorization.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()
    
    if usuario.es_admin:
        orden = session.query(Orden).filter(Orden.id == id_orden).first()
        
        return jsonable_encoder(orden)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='No eres administrador'
    )

@ruteador_ordenes.get(
    path='/usuario/{id_orden}',
    status_code=status.HTTP_200_OK,
    summary='Muestra una orden del usuario'
)
def mostrar_orden_usuario(id_orden: int = Path(...), Authorization: AuthJWT = Depends()):
    """
    # Mostrar orden
    
    ## Muestra una orden del usuario actual
    
    Parámetros
    - **id_orden**: ID de la orden ```Path Parameter: int```
    """
    try:
        Authorization.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token inválido o token no proporcionado'
        )
    
    usuario_actual = Authorization.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()
    orden = session.query(Orden).filter(Orden.id == id_orden)
    
    if orden:
        if orden.id_usuario == usuario.id:
            return jsonable_encoder(orden)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'La orden con ID {id_orden} no te pertenece'
        )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'La orden con ID {id_orden} no existe'
    )

@ruteador_ordenes.put(
    path='/{id_orden}',
    status_code=status.HTTP_200_OK,
    response_model=OrdenBase,
    summary='Actualiza una orden'
)
def actualizar_orden(id_orden: int = Path(...), orden: OrdenBase = Body(...), Authorization: AuthJWT = Depends()):
    """
    # Actualizar Orden
    
    ## Actualiza una orden en específico
    
    Parámetros
    - **id_orden**: ID de la orden ```Path Parameter: int```
    - **orden**: Orden con los datos para actualizar
    """
    try:
        Authorization.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token inválido o token no proporcionado'
        )
        
    usuario_actual = Authorization.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()
    orden_actualizada = session.query(Orden).filter(Orden.id == id_orden)    
    
    if orden_actualizada.id_usuario == usuario.id:        
        orden_actualizada.cantidad = orden.cantidad
        orden_actualizada.guisados = orden.guisados
        orden_actualizada.tipo = orden.tipo
        
        session.commit()
        return jsonable_encoder(OrdenBase(
            id=orden_actualizada.id,
            cantidad=orden_actualizada.cantidad,
            guisados=str(orden_actualizada.guisados.code),
            estado=str(orden_actualizada.estado.code),
            tipo=str(orden_actualizada.tipo.code),
            id_usuario=orden_actualizada.id_usuario
        ))

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f'No puedes actualizar la orden con ID {id_orden} porque no te pertenece'
    )
    
    
@ruteador_ordenes.patch(
    path='/{id_orden}', 
    status_code=status.HTTP_200_OK,
    response_model=OrdenBase,
    summary='Actualiza el estado de una orden',
    tags=['Solo Administración']
)
def actualizar_estado_orden(estado_orden: EstadoOrden = Body(...), id_orden: int = Path(...), Authorize: AuthJWT = Depends()):
    """
    # Actualiza orden
    
    ## Actualiza el estado de una orden, requiere ser administrador
    
    Parámetros 
    - **estado_orden**: Estado de la orden para actualizar [PROCESANDO, EN RUTA, ENTREGADO]
    - **id_orden**: ID de la orden ```Path Parameter: int```
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token inválido o token no proporcionado'
        )

    usuario_actual = Authorize.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()

    if usuario.es_admin:
        orden_actualizada = session.query(Orden).filter(Orden.id == id_orden).first()
        orden_actualizada.estado = estado_orden.estado

        session.commit()
        return jsonable_encoder(OrdenBase(
            id=orden_actualizada.id,
            cantidad=orden_actualizada.cantidad,
            guisados=str(orden_actualizada.guisados.code),
            estado=str(orden_actualizada.estado.code),
            tipo=str(orden_actualizada.tipo.code),
            id_usuario=orden_actualizada.id_usuario
        ))
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='No eres administrador'
    )    
      