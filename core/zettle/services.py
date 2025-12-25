from typing import Any, Sequence
from uuid import UUID
import rich
from sqlalchemy import Engine
from core.repositories import InventoryUpdateRepository
from core.type_dict import Product
from core.zettle.data_fetchers import ProductDataFetcher, PurchasesFetcher
from core.zettle.validation.inventory_update_validation import InventoryBalanceUpdateValidation,Payload
import logging
from datetime import datetime

from core.zettle.validation.product_validating import ProductData
from core.zettle.validation.purchase_validation import ListOfPurchases
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

class InventoryUpdatesDataJoiner:
    def __init__(self,repo_updater:InventoryUpdateRepository,start_date:datetime,end_date:datetime):
        self.repo_updater:InventoryUpdateRepository = repo_updater
        self.start_date: datetime =start_date
        self.end_date:datetime = end_date
        self._inventory_update_joined:dict[tuple[UUID,UUID], int ] = {}
    
    def join_inventory_update_data(self) -> dict[tuple[UUID,UUID], int]:
        # fetch stored inventory updates
        inventory_updates: Sequence[InventoryBalanceUpdateModel] = self.repo_updater.fetch_data_by_date_interval(
            start_date=self.start_date,
            end_date=self.end_date)
        
        for update in inventory_updates:
            key:tuple[UUID,UUID] = (update.product_id, update.variant_id)
            item_value: int | None = self._inventory_update_joined.get(key,None)
            change:int = update.after - update.before
            if item_value:
                self._inventory_update_joined[key] = item_value + change
            else:
                self._inventory_update_joined[key] = change
        return self._inventory_update_joined
    
class PurchaseDataJoiner:
    def __init__(self,purchases_fetcher:PurchasesFetcher,start_date:datetime,end_date:datetime):
        self.purchases_fetcher: PurchasesFetcher = purchases_fetcher
        self.start_date: datetime =start_date
        self.end_date:datetime = end_date
        self._purchases_joined:dict[tuple[UUID,UUID], int ] = {}

    
    def join_purchase_update_data(self) -> dict[tuple[UUID,UUID], int]:
        # fetch stored inventory updates
        purchases: dict[Any,Any] = self.purchases_fetcher.get_purchases(
            start_date=self.start_date,
            end_date=self.end_date,
        )
        validated_purchases:ListOfPurchases = ListOfPurchases.model_validate(obj=purchases)
        
        for purchases_iter in validated_purchases.purchases:
            for product_iter in purchases_iter.products:
                key:tuple[UUID,UUID] = (product_iter.productUuid, product_iter.variantUuid)
                item_value: int | None = self._purchases_joined.get(key,None)
                quantity:int = product_iter.quantity
                if item_value:
                    self._purchases_joined[key] = item_value + quantity
                else:
                    self._purchases_joined[key] = quantity
        return self._purchases_joined
                    

class InventoryManualChangesChecker:
    def __init__(
            self,
            purchases_merged:dict[tuple[UUID,UUID],int],
            inventory_update_merged:dict[tuple[UUID,UUID],int]) -> None:
        
        self.marge_inventory_update: dict[tuple[UUID,UUID], int] = inventory_update_merged
        self.marge_purchases_update: dict[tuple[UUID,UUID], int] = purchases_merged

    def get_manual_changes(self) -> dict[tuple[UUID,UUID], int]:
        for purchase,value in self.marge_purchases_update.items():
            if purchase in self.marge_inventory_update.keys():
                self.marge_inventory_update[purchase] = self.marge_inventory_update[purchase] + value
                if not self.marge_inventory_update[purchase]:
                    del self.marge_inventory_update[purchase]
        return self.marge_inventory_update
            

class ManualProductData:
    def __init__(self,manual_changes: dict[tuple[UUID,UUID],int],organization_id:str,product_data_fetcher:ProductDataFetcher) -> None:
        self.manual_changes: dict[tuple[UUID,UUID], int] = manual_changes
        self.organization_id: str = organization_id
        self.data_fetcher:ProductDataFetcher = product_data_fetcher
        self.list_of_products:list[Product] = []
    
    def get_manual_changes_product_data(self) -> list[Product]:
        for key,value in self.manual_changes.items():
            product_data:dict = self.data_fetcher.get_product_data(product_uuid=str(object=key[0]), organization_id=self.organization_id)
            validated_product_data:ProductData = ProductData.model_validate(obj=product_data)
            
            for variant in validated_product_data.variants:
                if str(object=variant.uuid) == str(object=key[1]):
                    category: str | None = validated_product_data.category.name if validated_product_data.category else None
                    product:Product = {
                        "name": validated_product_data.name,
                        "variant_name":variant.name,
                        "category":category,
                        "price":variant.price.amount,
                        "manual_change":value,
                    }
                    self.list_of_products.append(product)
                    
        return self.list_of_products



