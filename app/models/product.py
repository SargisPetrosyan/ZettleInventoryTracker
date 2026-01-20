from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any, TypedDict
from dataclasses import dataclass


class Price(BaseModel,str_strip_whitespace=True):
    amount:int
    currencyId:str

class Variants(BaseModel,str_strip_whitespace=True):
    uuid: UUID
    name: None | str
    price: Price | None 

class Category(BaseModel,str_strip_whitespace=True):
    uuid:UUID
    name:str

class ProductData(BaseModel, str_strip_whitespace=True):
    uuid: UUID
    categories: list[ None | str]
    name: str
    variants: list[Variants]
    category: Category | None


class Products(BaseModel,str_strip_whitespace=True):
    quantity: int
    productUuid: UUID
    variantUuid: UUID
    unitPrice: int
    name:str 
    variantName:str


class Purchases(BaseModel,str_strip_whitespace=True):
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
    category: Category | None
    organization_id: str
    stock:int
    manual_change: int
    timestamp:datetime
    price: Price | None = None

    def __post_init__(self) -> None:
        self.price = self.correct_price_amount(price=self.price)
    
    def correct_price_amount(self, price:Price | None) -> Price | None:
        if not price:
            return None
        else:
            return Price(amount=price.amount // 100, currencyId=price.currencyId)
    
        
    
    
    
class ListOfProductData(TypedDict):
    list_of_products: dict[tuple[UUID,UUID], list[Product]]
