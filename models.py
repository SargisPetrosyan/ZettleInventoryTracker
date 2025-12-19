from sqlmodel import Field, SQLModel


class InventoryBalanceUpdate(SQLModel, table=True):
    shop_id: int = Field(default=None, primary_key=True)
    timestamp: str
    product_id: str
    variant_id:str
    category: str | None = None
    name: str
    before:int
    after:int
    change:int

    def __repr__(self) -> str:
        return f"""<InventoryBalanceUpdate(name='{self.name}', 
        name='{self.name}, 
        before:{self.before}, 
        after:{self.after}, 
        change:{self.after}')>"""

