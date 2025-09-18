from pydantic import BaseModel, ValidationError
from datetime import datetime


def validate_inventory_update(payload: dict) -> BaseModel:
    try:
        validation: BaseModel = InventoryBalanceChanged(**payload)
        return validation
    except ValidationError as e:
        raise ValidationError("Inventory update data validation failed", e)


def validating_product_data(payload: dict):
    try:
        validation: BaseModel = ProductData(**payload)
        return validation
    except ValidationError as e:
        raise ValidationError("Product data validation failed", e)


class InventoryUpdatedBy(BaseModel):
    userUuid: str
    userType: str
    clientUuid: str
    updatedAt: str


class InventoryBalanceChanged(BaseModel):
    organizationUuid: str
    updatedBy: InventoryUpdatedBy
    timestamp: datetime


class Product(BaseModel):
    productUuid: str
    variantUuid: str
    locationUuid: str


class inventory(BaseModel):
    before: int
    after: int
    change: int
    updatedAt: datetime


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
