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
    description: str | None
    barcode: str |None
    price: Price
    costPrice: Price | None
    options: list[Options | None] |None

class Properties(BaseModel):
    value:str

class Definitions(BaseModel):
    name: str
    properties:list[Properties]

class VariantOptionDefinitions(BaseModel):
    definitions: list[Definitions]

class Category(BaseModel):
    uuid:UUID
    name:str

class ProductData(BaseModel):
    uuid: UUID
    categories: list[ None | str]
    name: str
    description: str | None
    variants: list[Variants]
    etag:str
    updated:datetime
    updatedBy: UUID
    created: datetime
    variantOptionDefinitions:VariantOptionDefinitions | None
    category: Category | None

