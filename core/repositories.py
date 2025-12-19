from abc import ABC, abstractmethod

from sqlalchemy import Engine
from sqlmodel.sql._expression_select_cls import SelectOfScalar
from setup_db import create_engine_connection
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models import InventoryBalanceUpdate
class InventoryUpdateAbstract(ABC):

    @abstractmethod
    def store_product_data(self,product_data:InventoryBalanceUpdate):
        raise NotImplementedError
    
    @abstractmethod
    def fetch_product_data_by_date(self,variant_id:str):
        raise NotImplementedError
    

class  InventoryUpdateRepository(InventoryUpdateAbstract):
    def __init__(self) -> None:
        self.engine: Engine  = create_engine_connection()
        
    def store_product_data(self, product_data:InventoryBalanceUpdate) -> None:
        with Session(bind=self.engine) as session:
            session.add(instance=product_data)
            session.commit()
    
    def fetch_product_data_by_date(self,variant_id:str):
        with Session(bind=self.engine) as session:
            statement: SelectOfScalar[InventoryBalanceUpdate] = select(InventoryBalanceUpdate).where(InventoryBalanceUpdate.variant_id == variant_id)
            hero: InventoryBalanceUpdate | None = session.exec(statement=statement).first()
            print(hero)