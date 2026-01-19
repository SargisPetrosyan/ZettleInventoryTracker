from core.zettle.services import InventoryBalanceUpdater
from core.zettle.validation.inventory_update_validation import InventoryBalanceUpdateValidation
from setup_db import Database

class SubscriptionHandler:
    def process_subscription(self,inventory_update:InventoryBalanceUpdateValidation,database:Database) -> None:
        inventory_balance_updater =  InventoryBalanceUpdater(inventory_balance_update=inventory_update, engine=database.engine)
        inventory_balance_updater.store_inventory_update()


