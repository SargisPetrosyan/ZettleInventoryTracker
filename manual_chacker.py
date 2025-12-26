from typing import Sequence
from uuid import UUID

import rich
from core.type_dict import BeforeAfter, Product
from core.utils import EnvVariablesGetter
from core.zettle.services import InventoryManualChangesChecker, InventoryUpdatesDataJoiner, ManualProductData, PurchaseDataJoiner
from core.repositories import InventoryUpdateRepository
from core.zettle.data_fetchers import ProductDataFetcher, PurchasesFetcher
from datetime import datetime

from models import InventoryBalanceUpdateModel

class InventoryManualDataCollector:
    def __init__(self,repo_updater:InventoryUpdateRepository, purchase_fetcher:PurchasesFetcher) -> None:
        self.purchase_fetcher:PurchasesFetcher = purchase_fetcher
        self.repo_updater:InventoryUpdateRepository = repo_updater
        self._purchases_joined_joined:dict[frozenset[UUID], int] = {}
        
    def get_manual_changed_products(self,shop_name:str) -> list[Product] | None:
        env_variables_getter = EnvVariablesGetter()
        organization_id: str = env_variables_getter.get_env_variable(variable_name=f"ZETTLE_{shop_name.upper()}_ORGANIZATION_UUID")

        # end_date:datetime = datetime.now()
        # start_date:datetime = datetime.now() - timedelta(hours=hour_interval)

        start_date:datetime = datetime(hour=11, day=26, month=12,year=2025)
        end_date:datetime = datetime(hour=17, day=26, month=12,year=2025)

        inventory_updates: Sequence[InventoryBalanceUpdateModel] = self.repo_updater.fetch_data_by_date_interval(
            start_date=start_date,
            end_date=end_date)
        
        if not inventory_updates:
            return None
        
        # inventory update data joining
        inventory_data_joiner = InventoryUpdatesDataJoiner(
            inventory_changes=inventory_updates,
            start_date=start_date,
            end_date=end_date)
        
        inventory_data_joined: dict[tuple[UUID,UUID], BeforeAfter] = inventory_data_joiner.join_inventory_update_data()

        # purchases data joining
        purchases_joiner = PurchaseDataJoiner(
            purchases_fetcher=self.purchase_fetcher,
            start_date=start_date,
            end_date=end_date)
        
        purchases_data_merged: dict[tuple[UUID,UUID], int] = purchases_joiner.join_purchase_update_data()

        # minus purchases changes to get manual ones
        inventory_manual_checker = InventoryManualChangesChecker(
            inventory_update_merged=inventory_data_joined,
            purchases_merged=purchases_data_merged,
        )

        manual_changes: dict[tuple[UUID,UUID], BeforeAfter] = inventory_manual_checker.get_manual_changes()

        # get product data for manual changes
        product_data_fetcher:ProductDataFetcher = ProductDataFetcher(shop_name=shop_name) 
        product_data_manual = ManualProductData(
            manual_changes=manual_changes,
            organization_id=organization_id,
            product_data_fetcher=product_data_fetcher)
        
        product_data_with_manual_changes:list[Product] =  product_data_manual.get_manual_changes_product_data()
        return product_data_with_manual_changes

                
 

