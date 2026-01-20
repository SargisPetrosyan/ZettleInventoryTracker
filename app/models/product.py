from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import TypedDict
from dataclasses import dataclass

class Price(BaseModel):
    amount:int
    currencyId:str

class Variants(BaseModel):
    uuid: UUID
    name: None | str
    price: Price | None 

class Category(BaseModel):
    uuid:UUID
    name:str

class ProductData(BaseModel):
    uuid: UUID
    categories: list[ None | str]
    name: str
    variants: list[Variants]
    category: Category | None


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

@dataclass
class Product():
    name: str
    variant_name: str | None 
    _category_name: Category | None
    organization_id: str
    stock:int
    manual_change: int
    _price: int | None
    timestamp:datetime

    @property
    def category(self) -> str | None:
        if not self._category_name:
            return None
        return self._category_name.name
    
    @property
    def price(self) -> int | None:
        if not self._category_name:
            return None
        return self.price
    

class ListOfProductData(TypedDict):
    list_of_products: dict[tuple[UUID,UUID], list[Product]]
