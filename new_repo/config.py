import logging
from sqlalchemy import Engine
from sqlmodel import  SQLModel, create_engine
from dotenv import load_dotenv
import os

load_dotenv()

from setup_db import Database

class Config:
    def __init__(self,db_url:str):
        self._setup_logging()
        self.db: Engine = self._setup_db(db_url=db_url)

    def _setup_logging(self):
        logging.basicConfig(
        # filename="app/langgraph/logs/langgraph_logs.log",
        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        filemode="w",
        force=True,
    )
        # Creating an object
        logger: logging.Logger = logging.getLogger()

        # Setting the threshold of logger to DEBUG
        logger.setLevel(level=logging.INFO)
    
    def _setup_db(self,db_url:str):
        engine: Engine = create_engine(url=db_url)
        SQLModel.metadata.create_all(bind=engine)
        return engine

class Settings:
    def __init__(self) -> None:
        self.DATABASE_URL: str | None = os.getenv("DB_URL")
        self.MAIL: str | None = os.getenv("MAIL")
        self.DESTINATION_URL: str | None = os.getenv("DESTINATION_URL")
        #ART&CRAFT
        self.ZETTLE_ART_ORGANIZATION_UUID: str | None = os.getenv("ZETTLE_ART_ORGANIZATION_UUID")
        self.ZETTLE_ART_PRODUCT_READ_CLIENT_ID: str | None = os.getenv("ZETTLE_ART_PRODUCT_READ_CLIENT_ID")
        self.ZETTLE_ART_PRODUCT_READ_KEY: str | None = os.getenv("ZETTLE_ART_PRODUCT_READ_KEY")
        #DALA
        self.ZETTLE_DALA_ORGANIZATION_UUID: str | None = os.getenv("ZETTLE_DALA_ORGANIZATION_UUID")
        self.ZETTLE_DALA_PRODUCT_READ_CLIENT_ID: str | None = os.getenv("ZETTLE_DALA_PRODUCT_READ_CLIENT_ID")
        self.ZETTLE_DALA_PRODUCT_READ_KEY: str | None = os.getenv("ZETTLE_DALA_PRODUCT_READ_KEY")
        
        

