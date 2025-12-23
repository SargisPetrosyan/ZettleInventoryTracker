from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class Price(BaseModel):
    amount:int
    currencyId:str

class Options(BaseModel):
    name:int
    value:str

class Variants(BaseModel):
    uuid: UUID
    name: None | str
    description: str | None
    barcode: str
    price: Price
    costPrice: Price
    options: list[Options | None]

class Properties(BaseModel):
    value:str

class Definitions(BaseModel):
    name: int
    properties:list[Properties]

class VariantOptionDefinitions(BaseModel):
    definitions: list[Definitions]

class ProductData(BaseModel):
    uuid: UUID
    categories: list[None | str]
    description: str | None
    variants: list[None | Variants]
    etag:str
    updated:datetime
    updatedBy: UUID
    created: datetime
    variantOptionDefinitions:VariantOptionDefinitions

