from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel
from pydantic import UUID1,UUID3,UUID4,UUID5

class Price(BaseModel):
    amount:int
    currencyId:str

class Options(BaseModel):
    name:int
    value:str

class Variants(BaseModel):
    uuid: UUID1
    name: None | str
    description: str | None
    barcode: int
    price: Price
    costPrice: Price
    vatPercentage:int
    options: list[Options | None]
    sku: str

class Properties(BaseModel):
    value:str

class Definitions(BaseModel):
    name: int
    properties:list[Properties]

class VariantOptionDefinitions(BaseModel):
    definitions: list[Definitions]

class ProductData(BaseModel):
    uuid: UUID1
    categories: list[None | str]
    description: str | None
    variants: list[None | Variants]
    etag:str
    updated:datetime
    updatedBy: UUID4
    created: datetime
    variantOptionDefinitions:VariantOptionDefinitions

