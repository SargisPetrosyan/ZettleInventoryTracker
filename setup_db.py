from sqlalchemy import Engine
from sqlmodel import  SQLModel, create_engine

def create_engine_connection() -> Engine:
    engine: Engine = create_engine(url="sqlite:///database.db")

    SQLModel.metadata.create_all(bind=engine)

    return engine

