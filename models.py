import datetime
from sqlmodel import Field, SQLModel, DateTime
import uuid



class InventoryBalanceUpdate(SQLModel, table=True):
    shop_id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp:datetime.datetime = Field(default_factory=DateTime)
    product_id:uuid.UUID  = Field(default_factory=uuid.uuid1)
    variant_id:uuid.UUID = Field(default_factory=uuid.uuid1)
    category: str | None = None
    name: str
    before:int
    after:int
    change:int

    def __repr__(self) -> str:
        return f"""<InventoryBalanceUpdate(name='{self.name}', 
        timestamp='{self.timestamp}
        name='{self.name}, 
        before:{self.before}, 
        after:{self.after}, 
        change:{self.after}')>"""

