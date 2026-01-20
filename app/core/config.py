import logging
from sqlalchemy import Engine
from sqlmodel import  SQLModel, create_engine
from dotenv import load_dotenv
import os

from app.constants import SHOP_SUBSCRIPTION_EVENTS, WEBHOOK_ENDPOINT_NAME

load_dotenv()

class Database:
    def __init__(self) -> None:
        self.engine: Engine = create_engine(url="sqlite:///database.db")
        SQLModel.metadata.create_all(bind=self.engine)

class Settings:
    def __init__(self, shop_name:str) -> None:
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
        self.name: str = shop_name
        self._subscription_uuid: str | None = os.getenv(key=f"ZETTLE_{shop_name.upper()}_SUBSCRIPTION_UUID")
        self._destination_url: str | None = os.getenv(key="DESTINATION_URL")
        self._mail: str | None = os.getenv(key="MAIL")
        self.events: list[str] = SHOP_SUBSCRIPTION_EVENTS

    @property
    def destination_url(self)-> str:
        if self._destination_url is None:
            raise TypeError(f"{self.name} destination_url cant be None")
        return self._destination_url + WEBHOOK_ENDPOINT_NAME
    