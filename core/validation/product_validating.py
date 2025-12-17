from pydantic import BaseModel

class Variants(BaseModel):
    uuid: str
    name: None | str
    description: str
    sku: str

class ProductData(BaseModel):
    uuid: str
    category: str
    categories: list
    name: str
    variants: list[Variants]
    updated: str
    created: str