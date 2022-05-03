from .db import engine, Base
from .models import Usuario, Orden

def activate():
    Base.metadata.create_all(bind=engine)