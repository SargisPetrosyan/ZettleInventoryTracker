from pydantic import BaseModel, ValidationError
from datetime import datetime


class InventoryUpdatedBy(BaseModel):
    userUuid: str
    userType: str
    clientUuid: str
    updatedAt: str


class Product(BaseModel):
    productUuid: str
    variantUuid: str
    locationUuid: str


class Inventory(BaseModel):
    before: int
    after: int
    change: int
    updatedAt: datetime


class Variants(BaseModel):
    uuid: str
    name: None | str
    description: str
    sku: str


class InventoryBalanceChanged(BaseModel):
    organizationUuid: str
    timestamp: datetime
    updatedBy: InventoryUpdatedBy
    product: Product
    inventory: Inventory


class ProductData(BaseModel):
    uuid: str
    category: str | None
    categories: list
    name: str
    variants: list[Variants]
    updated: str
    created: str
