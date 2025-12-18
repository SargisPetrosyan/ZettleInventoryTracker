from datetime import datetime
from pydantic import BaseModel
from pydantic import UUID1

class Products(BaseModel):
    quantity: int
    productUuid: UUID1
    variantUuid: UUID1
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