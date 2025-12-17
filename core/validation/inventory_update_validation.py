from pydantic import BaseModel
from datetime import datetime
from pydantic import UUID1,UUID3,UUID4,UUID5


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

class Payload(BaseModel):
    organizationUuid: UUID4
    updated: datetime
    updatedBy: InventoryUpdatedBy
    product: Product
    inventory: Inventory

class InventoryBalanceChanged(BaseModel):
    organizationUuid: UUID4
    messageUuid: UUID1
    eventName: str
    messageId: UUID5
    payload: Payload
