from pydantic import BaseModel
from datetime import datetime

   
class InventoryUpdatedBy(BaseModel):
    userUuid: str
    userType: str
    clientUuid: str
    updatedAt: str
    
class InventoryBalanceChanged(BaseModel):
    organizationUuid: str
    updatedBy: InventoryUpdatedBy
    timestamp: datetime

class Product(BaseModel):
    productUuid: str
    variantUuid: str
    locationUuid: str
    
class inventory(BaseModel):
    before: int
    after: int
    change: int
    updatedAt: datetime

class Variants:
    uuid: str
    name: None | str
    description: str
    sku: str
    
class ProductData:
    uuid: str
    category:str
    categories: list
    name: str
    variants: list[Variants]
    updated: str
    created: str
    


    
    

