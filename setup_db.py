from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

engine: Engine = create_engine('sqlite:///library.db', echo=True)

# Create a base class for our models
Base = declarative_base()

# Create a session factory bound to our engine
SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine)
