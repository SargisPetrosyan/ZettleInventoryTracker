from sqlalchemy import Engine
from sqlmodel import Field, Session
from models import InventoryBalanceUpdateModel


class  InventoryUpdateRepository():
    def __init__(self,engine) -> None:
        self.engine: Engine  = engine
        
    def store_updated_inventory_data(self,inventory_update: list[InventoryBalanceUpdateModel]) -> None:
        with Session(bind=self.engine) as session:
            for i in inventory_update:
                session.add(instance=i)
            session.commit()