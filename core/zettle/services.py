import rich
from sqlalchemy import Engine
from core.repositories import InventoryUpdateRepository
from core.zettle.validation.inventory_update_validation import InventoryBalanceUpdateValidation,Payload
import logging

from models import InventoryBalanceUpdateModel 

logger: logging.Logger = logging.getLogger(name=__name__)

class InventoryBalanceUpdater:
    def __init__(self, inventory_balance_update:InventoryBalanceUpdateValidation, engine:Engine) -> None:
        self.inventory_balance_update: InventoryBalanceUpdateValidation = inventory_balance_update
        self.database:InventoryUpdateRepository = InventoryUpdateRepository(engine=engine)
        
    def store_inventory_update(self) -> None:
        list_of_updates:list[InventoryBalanceUpdateModel] = []
        for i in range(len(self.inventory_balance_update.payload.balanceBefore)):
            payload: Payload = self.inventory_balance_update.payload
            object = InventoryBalanceUpdateModel(
                timestamp=payload.updated.timestamp,
                shop_id=payload.organizationUuid,
                product_id=payload.balanceBefore[i].productUuid,
                variant_id=payload.balanceBefore[i].variantUuid,
                before=payload.balanceBefore[i].balance,
                after=payload.balanceAfter[i].balance,
            )
            list_of_updates.append(object) 

        inventory_update: InventoryUpdateRepository = InventoryUpdateRepository(engine=self.database.engine)
        inventory_update.store_updated_inventory_data(inventory_update=list_of_updates)