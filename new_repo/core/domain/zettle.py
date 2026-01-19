from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import TypedDict
from dataclasses import dataclass

#InventoryBalanceUpdate
class Updated(BaseModel):
    uuid: UUID
    timestamp: datetime
    userType: str
    clientUuid: UUID | None 

class BalanceBefore(BaseModel):
    organizationUuid: UUID
    locationUuid: UUID
    productUuid: UUID
    variantUuid: UUID
    balance: int

class BalanceAfter(BaseModel):
    organizationUuid: UUID
    locationUuid: UUID
    productUuid: UUID
    variantUuid: UUID
    balance: int

class Payload(BaseModel):
    organizationUuid: UUID
    updated: Updated
    balanceBefore: list[BalanceBefore]
    balanceAfter: list[BalanceAfter]
    externalUuid: None  | str

class InventoryBalanceUpdate(BaseModel):
    organizationUuid: UUID
    messageUuid: UUID
    eventName: str
    messageId: UUID
    payload: Payload
    timestamp: datetime

#ProductData
class Price(BaseModel):
    amount:int
    currencyId:str

class Variants(BaseModel):
    uuid: UUID
    name: None | str
    price: Price

class Category(BaseModel):
    uuid:UUID
    name:str

class ProductData(BaseModel):
    uuid: UUID
    categories: list[ None | str]
    name: str
    variants: list[Variants]
    category: Category | None

#Purchases
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


#Zettle Auth
class ZettleAccessToken(BaseModel):
    access_token: str
    expiry: datetime

class ZettleCredentials(BaseModel):
    client_id: str
    key: str
    grant_type: str
    auth_url: str
    headers: str

class ZettleNewAccessToken(BaseModel):
    access_token: str

# Manual Changed Data Model
@dataclass
class Product():
    name: str
    variant_name: str | None 
    _category_name: Category | None
    organization_id: str
    stock:int
    manual_change: int
    price: int
    timestamp:datetime

    @property
    def category(self) -> str:
        if not self._category_name:
            return 'None'
        return self._category_name.name
    

class ListOfProductData(TypedDict):
    list_of_products: dict[tuple[UUID,UUID], list[Product]]

@dataclass
class InventoryUpdateData():
    stock:int
    updated_value:int
    timestamp:datetime
