from fastapi import APIRouter, Body, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from database.db import Session, engine
from database.schemas import (
    UsuarioRegistro, 
    UsuarioBase, 
    UsuarioLogin, 
    UsuarioLoginOut
    )
from database.models import Usuario
from werkzeug.security import (
    generate_password_hash, 
    check_password_hash
    )

ruteador_auth = APIRouter(
    prefix='/auth',
    tags=['Autenticación']
)

session = Session(bind=engine)

@ruteador_auth.post(
    path='/registro',
    summary='Registrar un nuevo usuario',
    response_model=UsuarioBase,
    status_code=status.HTTP_201_CREATED
    )
def registro(usuario: UsuarioRegistro = Body(...)) -> UsuarioBase:
    """
    # Registro
    
    ## Registra a un usuario en la aplicación
    
    Parámetros 
    - **username**: nombre de usuario
    - **email**: email del usuario
    - **password**: contraseña del usuario
    - **es_activo**: el usuario es un usuario activo (si, no)
    - **es_admin**: el usuario tiene permisos de administración (si, no)    
    
    Retorna un JSON con la información básica del usuario creado 
    - **id**: id del usuario creado
    - **username**: username del usuario creado
    
    """
    email_db = session.query(Usuario).filter(Usuario.email == usuario.email).first()
    
    if email_db is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='El email ya está registrado, intenta con uno nuevo'
            )

    username_db = session.query(Usuario).filter(Usuario.username == usuario.username).first()
    
    if username_db is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='El nombre de usuario ya está registrado, intenta con uno nuevo'
            )
    
    nuevo_usuario = Usuario(
        username=usuario.username,
        email=usuario.email,
        password=generate_password_hash(usuario.password),
        es_activo=usuario.es_activo,
        es_admin=usuario.es_admin
    )
    
    session.add(nuevo_usuario)
    
    result = session.execute(
        select(Usuario.id).where(Usuario.username == usuario.username)
    )
    
    session.commit()
    
    return UsuarioBase(username=nuevo_usuario.username, id=result.all()[0][0], mensaje='Registro correcto')
        
@ruteador_auth.post(
    path='/acceso',
    status_code=status.HTTP_200_OK
    )
def entrar(usuario: UsuarioLogin = Body(...), Authorize: AuthJWT = Depends()):
    """
    # Acceso
    
    ## Acceso de un usuario a la API
    
    Parámetros
    - **username**: nombre de usuario
    - **password**: contraseña del usuario
    
    Retorna un JSON con un mensaje de acceso correcto (o incorrecto) y un access/refresh token
    - **Access**: token
    - **Refresh**: refresh token
    - **Mensaje**: mensaje 
    """
    usuario_db = session.query(Usuario).filter(Usuario.username == usuario.username).first()
    
    if usuario_db and check_password_hash(usuario_db.password, usuario.password):
        access_token = Authorize.create_access_token(subject=usuario_db.username)
        refresh_token = Authorize.create_refresh_token(subject=usuario_db.username)
        
        response_token = {
            "access": access_token,
            "refresh": refresh_token
        }
        
        response_usuario = dict(UsuarioLoginOut(username=usuario.username))
        
        response = {**response_usuario, **response_token}
        
        return jsonable_encoder(response)
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Nombre de usuario o contraseña inválidos"
    )

@ruteador_auth.post(
    path='/refresh',
    status_code=status.HTTP_200_OK
)
def refresh_token(Authorize: AuthJWT = Depends()):
    """
    # Refresh Token
    
    ## Crea un fresh token, requiere de un refresh token previo
    """
    try: 
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Por favor asegurate de contar con un refresh token {e}'
        )
    
    usuario_actual = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=usuario_actual)
    refresh_token = Authorize.create_refresh_token(subject=usuario_actual)
    
    return jsonable_encoder(
        {
            "access": access_token,
            "refresh": refresh_token
        }
    )
    
@ruteador_auth.get(
    path='/usuarios',
    status_code=status.HTTP_200_OK,
    summary='Muestra todos los usuarios de la aplicación',
    tags=['Solo Administración']
)
def mostrar_usuarios(Authorize: AuthJWT = Depends()):
    """
    # Mostrar Usuarios
    
    ## Muestra a todos los usuarios de la aplicación, requiere permisos de administración y token
    """
    try: 
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Por favor asegurate de contar con un refresh token {e}'
        )
    
    usuario_actual = Authorize.get_jwt_subject()
    usuario = session.query(Usuario).filter(Usuario.username == usuario_actual).first()
    
    if usuario.es_admin:
        usuarios = session.query(Usuario).all()
        
        return jsonable_encoder(usuarios)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='No eres administrador'
    )        