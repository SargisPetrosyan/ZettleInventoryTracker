from datetime import datetime
from typing import TypedDict
from uuid import UUID

class Product(TypedDict):
    name: str
    variant_name: str | None
    category: str | None
    manual_change: int | None
    price: int
    stock:int
    timestamp:datetime


class ListOfProductData(TypedDict):
    list_of_products: dict[tuple[UUID,UUID], list[Product]]


class BeforeAfter(TypedDict):
    stock:int
    updated_value:int
    timestamp:datetime
