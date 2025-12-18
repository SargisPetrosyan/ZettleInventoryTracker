from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime
from setup_db import Base

class InventoryBalanceUpdate(Base):
    __tablename__: str = 'inventory_balance_change'
    shop_id = Column(String(100), nullable=False)
    timestamp = Column(String(100), nullable=False)
    product_id = Column(String(100), nullable=False)
    category=Column(String(100), nullable=False)
    name=Column(String(100), nullable=False)
    before=Column(Integer)
    after = Column(Integer)
    change = Column(Integer)

    def __repr__(self) -> str:
        return f"<InventoryBalanceUpdate(name='{self.name}', category='{self.category}, before:{self.before}, after:{self.after}, change:{self.after}')>"