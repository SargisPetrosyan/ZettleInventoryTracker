from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class Products(BaseModel):
    quantity: int
    productUuid: UUID
    variantUuid: UUID
    unitPrice: int
    name:str 
    variantName:str


class Purchases(BaseModel):
    amount:int
    timestamp:datetime
    products:list[Products]
    refunded: bool
    refund: bool


class ListOfPurchases(BaseModel):
    purchases: list[Purchases]