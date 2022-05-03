from typing import Optional
from pydantic import BaseModel, Field, validator, EmailStr
import re
import os


class UsuarioBase(BaseModel):
    id: Optional[int] = Field(
        title='ID de usuario'
    )
    username: str = Field(
        title='Nombre de usuario',
        min_length=1,
        max_length=25
    )
    mensaje: str = Field(
        default='Registro correcto',
        description='Mensaje descriptivo'
    )
   
class UsuarioRegistro(UsuarioBase):
    email: EmailStr = Field(
        title='Email del usuario'
    )
    password: str = Field(
        title='Contraseña',
        min_length=8
    )
    es_activo: Optional[bool] = Field(
        title='Es un usuario activo?',
        default=True
    )
    es_admin: Optional[bool] = Field(
        title='Es administrador?',
        default=False
    )
    
    @validator('password')
    def password_val(cls, v):
        flag = 0
        while True:  
            if (len(v) < 8):
                flag = -1
                break
            elif not re.search("[a-z]", v):
                flag = -1
                break
            elif not re.search("[A-Z]", v):
                flag = -1
                break
            elif not re.search("[0-9]", v):
                flag = -1
                break
            elif not re.search("[_@$]", v):
                flag = -1
                break
            elif re.search("\s", v):
                flag = -1
                break
            else:
                flag = 0
                break
        if flag ==-1:
            raise ValueError('La contraseña debe contener mayúsculas, minúsculas, números y alguno de estos caracteres [_@$]')
        
        return v
    
    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "username": "andres",
                "email": "andres@mail.com",
                "password": "andr3S@2",
                "es_activo": True,
                "es_admin": False
            }
        }
 
class UsuarioLoginOut(BaseModel):
    username: str = Field(
        title='Nombre de usuario'
    )
    mensaje: str = Field(
        default='Ingreso aprobado',
        description='Mensaje descriptivo'
    )   
    
class UsuarioLogin(BaseModel):
    username: str = Field(
        title='Nombre de usuario'
    )    
    password: str = Field(
        title='Contraseña del usuario'
    )

class Settings(BaseModel):
    authjwt_secret_key: str = os.environ['JWT_KEY']
    
class OrdenBase(BaseModel):
    id: Optional[int]
    cantidad: int = Field(
        title='Cantidad',
        description='Cantidad de productos'
    )
    estado: Optional[str] = Field(
        title='Estado de la orden',
        description='Estado de la orden (PROCESANDO, EN RUTA, ENTREGADO)',
        default='PROCESANDO'
    )
    guisados: str = Field(
        title='Guisado',
        description='Guisado de tu tipo de comida (TINGA, CARNE, POLLO, CHAMPIÑONES, COMBINADO)',
    )
    tipo: str = Field(
        title='Tipo de comida',
        description='Tipo de comida (QUESADILLA, HUARACHE, SOPE)'
    )
    id_usuario: Optional[int] = Field(
        title='ID del usuario'
    )
    
    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'cantidad': 2,
                'guisados': 'TINGA',
                'tipo': 'QUESADILLA',
            }
        }
    
class EstadoOrden(BaseModel):
    estado: Optional[str] = 'PENDIENTE'

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "estado": 'PENDIENTE'
            }
        }