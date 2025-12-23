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
    barcode:str


class Purchases(BaseModel):
    purchaseUUID:str
    amount:int
    currency:str
    timestamp:datetime
    products:list[Products]


class ListOfPurchases(BaseModel):
    purchases: Purchases