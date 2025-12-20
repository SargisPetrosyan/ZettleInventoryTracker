import datetime
from sqlmodel import Field, SQLModel, DateTime
import uuid



class InventoryBalanceUpdate(SQLModel, table=True):
    timestamp:datetime.datetime = Field(default_factory=DateTime)
    shop_id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    product_id:uuid.UUID  = Field(default_factory=uuid.uuid1)
    variant_id:uuid.UUID = Field(default_factory=uuid.uuid1)
    before:int
    after:int

    def __repr__(self) -> str:
        return f"""<InventoryBalanceUpdate(, 
        timestamp='{self.timestamp}, 
        before:{self.before}, 
        after:{self.after}, 
        change:{self.after}')>"""

