from pydantic import BaseModel
from datetime import datetime
from pydantic import UUID1,UUID4,UUID5,HttpUrl,EmailStr


class Updated(BaseModel):
    uuid: UUID4
    timestamp: datetime
    userType: str
    clientUuid: UUID4 | None 

class BalanceBefore(BaseModel):
    organizationUuid: UUID4
    locationUuid: UUID1
    productUuid: UUID1
    variantUuid: UUID1
    balance: int

class BalanceAfter(BaseModel):
    organizationUuid: UUID4
    locationUuid: UUID1
    productUuid: UUID1
    variantUuid: UUID1
    balance: int

class Payload(BaseModel):
    organizationUuid: UUID4
    updated: Updated
    balanceBefore: list[BalanceBefore]
    balanceAfter: list[BalanceAfter]
    externalUuid: None  | str

class InventoryBalanceUpdateValidation(BaseModel):
    organizationUuid: UUID4
    messageUuid: UUID1
    eventName: str
    messageId: UUID5
    payload: Payload
    timestamp: datetime
