from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import  TypedDict
from dataclasses import dataclass
from app.constants import (
    month_empty_data_sample_titles,
    month_empty_data_sample_stock_out,
    month_empty_data_sample_stock_in
    )


class Price(BaseModel,str_strip_whitespace=True):
    amount:int
    currencyId:str

class Variants(BaseModel,str_strip_whitespace=True):
    uuid: UUID
    name: str | None
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
class PaypalProductData():
    organization_id: str
    product_variant_uuid: str
    before: int 
    after: int
    timestamp: datetime
    name: str 
    variant_name: str 
    category_name: str 
    price: str | int

class ListOfProductData(TypedDict):
    list_of_products: dict[tuple[UUID,UUID], list[PaypalProductData]]

class MonthlyStockDataBuilder:
    def __init__(self,product_data:PaypalProductData) -> None:
        self.data: PaypalProductData = product_data
        self.data_stock_in:list[str] = [
            product_data.name,
            product_data.category_name,
            product_data.variant_name,
            str(product_data.price)]
        self.normalized_data:list[list[str]] = []

    def normalize_data(self):
        self.data_stock_in.extend(month_empty_data_sample_stock_in)
        self.normalized_data =[
            month_empty_data_sample_titles, 
            self.data_stock_in,
            month_empty_data_sample_stock_out,
        ]

        
