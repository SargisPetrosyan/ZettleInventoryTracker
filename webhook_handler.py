from core.zettle.services.inventory_balance_updater import InventoryBalanceUpdater
from core.zettle.validation.inventory_update_validation import InventoryBalanceChanged
from setup_db import Database

class SubscriptionHandler:
    def process_subscription(self,inventory_update:InventoryBalanceChanged,database:Database) -> None:
        inventory_balance_updater =  InventoryBalanceUpdater(inventory_balance_update=inventory_update, engine=database.engine)
        inventory_balance_updater.update_inventory_update_database()
