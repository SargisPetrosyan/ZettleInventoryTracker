from sqlalchemy import Engine
from sqlmodel.sql._expression_select_cls import SelectOfScalar
from sqlmodel import Field, Session, select
from models import InventoryBalanceUpdate

class  InventoryUpdateRepository():
    def __init__(self,engine) -> None:
        self.engine: Engine  = engine
        
    def store_product_data(self,    
            shop_id,
            name,
            category,
            product_id,
            variant_id,
            timestamp,
            before,
            after,
        ) -> None:
        with Session(bind=self.engine) as session:
            InventoryBalanceUpdate(
                shop_id=shop_id ,
                name=name ,
                category=category ,
                product_id=product_id,
                variant_id=variant_id,
                timestamp=timestamp,
                before=before,
                after=after,
            )
            session.add(instance=InventoryBalanceUpdate)
            session.commit()
    
    def fetch_product_data_by_date(self,variant_id:str):
        with Session(bind=self.engine) as session:
            statement: SelectOfScalar[InventoryBalanceUpdate] = select(InventoryBalanceUpdate).where(InventoryBalanceUpdate.variant_id == variant_id)
            hero: InventoryBalanceUpdate | None = session.exec(statement=statement).first()
            print(hero)