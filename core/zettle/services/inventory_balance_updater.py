from sqlalchemy import Engine
from core.repositories import InventoryUpdateRepository
from core.zettle.validation.inventory_update_validation import InventoryBalanceChanged,Payload
import logging 

logger: logging.Logger = logging.getLogger(name=__name__)

class InventoryBalanceUpdater:
    def __init__(self, inventory_balance_update:InventoryBalanceChanged, engine:Engine) -> None:
        self.inventory_balance_update: InventoryBalanceChanged = inventory_balance_update
        self.database_repositories:InventoryUpdateRepository = InventoryUpdateRepository(engine=engine)
        
    def update_inventory_update_database(self) -> None:
        for i in range(len(self.inventory_balance_update.payload.balanceBefore)):
            payload: Payload = self.inventory_balance_update.payload
            self.database_repositories.store_product_data(
                timestamp=payload.updated.timestamp,
                shop_id=payload.organizationUuid,
                product_id=payload.balanceBefore[i].productUuid,
                variant_id=payload.balanceBefore[i].variantUuid,
                before=payload.balanceBefore[i].balance,
                after=payload.balanceBefore[i].balance,
            )