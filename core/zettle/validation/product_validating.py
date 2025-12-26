from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import Uuid

class Price(BaseModel):
    amount:int
    currencyId:str

class Options(BaseModel):
    name:str
    value:str

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

