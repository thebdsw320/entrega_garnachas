from .db import Base
from sqlalchemy import Column, Integer, Boolean, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType

class Usuario(Base):
    __tablename__ = 'usuario'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    password = Column(Text, nullable=True)
    es_admin = Column(Boolean, default=False)
    es_activo = Column(Boolean, default=True)
    ordenes = relationship('Orden', back_populates='usuario')
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Orden(Base):
    __tablename__ = 'ordenes'
    
    ESTADOS = (
        ('PROCESANDO', 'procesando'),
        ('EN RUTA', 'en ruta de entrega'),
        ('ENTREGADO', 'entregado')    
    )
    
    GUISADOS = (
        ('TINGA', 'tinga de pollo'),
        ('CARNE', 'carne'),
        ('POLLO', 'pollo'),
        ('CHAMPIÑONES', 'champiñones'),
        ('COMBINADO', 'combinado')
    )
    
    TIPOS = (
        ('QUESADILLA', 'quesadilla'),
        ('HUARACHE', 'huarache'),
        ('SOPE', 'sope')
    )
    
    id = Column(Integer, primary_key = True)
    cantidad = Column(Integer, nullable = False)
    estado = Column(ChoiceType(choices=ESTADOS), default='PROCESANDO')
    guisados = Column(ChoiceType(choices=GUISADOS))
    tipo = Column(ChoiceType(choices=TIPOS))
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship('Usuario', back_populates='ordenes')
    
    def __repr__(self):
        return f'<Orden {self.id}>'