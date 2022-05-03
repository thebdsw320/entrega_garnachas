from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(
    'postgresql://andres:password@localhost:5432/bd_entregas',
    echo=True
    )

Base = declarative_base()

Session = sessionmaker()