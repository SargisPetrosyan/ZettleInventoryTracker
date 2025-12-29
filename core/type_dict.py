from datetime import datetime
from typing import TypedDict
from uuid import UUID
from dataclasses import dataclass

from core.zettle.validation.product_validating import Category

@dataclass
class Product():
    name: str
    variant_name: str | None 
    _category_name: Category | None
    organization_id: str
    manual_change: int
    price: int
    stock:int
    timestamp:datetime

    @property
    def category(self) -> str:
        if not self._category_name:
            return 'None'
        return self._category_name.name


class ListOfProductData(TypedDict):
    list_of_products: dict[tuple[UUID,UUID], list[Product]]

@dataclass
class BeforeAfter():
    stock:int
    updated_value:int
    timestamp:datetime
