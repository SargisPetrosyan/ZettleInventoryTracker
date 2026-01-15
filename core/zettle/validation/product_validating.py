from uuid import UUID
from pydantic import BaseModel


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

