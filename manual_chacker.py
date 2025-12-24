from datetime import datetime, timedelta
from typing import Sequence
from uuid import UUID

from numpy import fromregex
from core.utils import InventoryUpdatesDataJoiner
import f

from sqlalchemy import Engine

from core.repositories import InventoryUpdateRepository
from core.zettle.data_fetchers import PurchasesFetcher
from core.zettle.validation.purchase_validation import ListOfPurchases
from models import InventoryBalanceUpdateModel


class InventoryChangeSourceChecker:
    def __init__(self,repo_updater:InventoryUpdateRepository, purchase_fetcher:PurchasesFetcher) -> None:
        
        self.purchase_fetcher:PurchasesFetcher = purchase_fetcher
        self.repo_updater:InventoryUpdateRepository = repo_updater
        self._purchases_joined_joined:dict[frozenset[UUID], int] = {}
        
    def check_manuel_changes(self,hour_interval:int):
        end_date:datetime = datetime.now()
        start_date:datetime = datetime.now() - timedelta(hours=hour_interval)

        inventory_data_joiner = InventoryUpdatesDataJoiner(
            repo_updater=self.repo_updater,
            start_date=start_date,
            end_date=end_date)
        
        inventory_data_joined: dict[frozenset[UUID], int] = inventory_data_joiner.join_inventory_update_data()

        # fetch purchases by date interval
        purchase_by_interval = self.purchase_fetcher.get_purchases(
            start_date=start_date,
            end_date=end_date
        )

        validated_purchase = ListOfPurchases(**purchase_by_interval)

        for update in inventory_updates:
            key:frozenset[UUID] = frozenset((update.product_id, update.variant_id))
            item_value: int | None = self._inventory_update_joined.get(key,None)
            change:int = update.after - update.before
            if item_value:
                new_value: int = item_value + change
                self._inventory_update_joined[key] = new_value
            else:
                self._inventory_update_joined[key] = change
            

                
 

