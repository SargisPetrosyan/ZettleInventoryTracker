from pydantic import BaseModel, ValidationError
from datetime import datetime
from fastapi.responses import JSONResponse
import json


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


def validate_inventory_update(response: JSONResponse) -> InventoryBalanceChanged:
    response_loads: dict = json.loads(response.body)
    try:
        validated = InventoryBalanceChanged(**response_loads)
        return validated
    except ValidationError:
        raise ValidationError("your model doesn't have valid data")


def validate_product_data(response: JSONResponse) -> ProductData:
    response_loads: dict = json.loads(response.body)
    try:
        validated = ProductData(**response_loads)
        return validated
    except ValidationError:
        raise ValidationError("your model doesn't have valid data")
