from os import name
from typing import Any, Sequence
from uuid import UUID
import rich
from sqlalchemy import Engine
from app.db.schemes import InventoryUpdateRepository
from app.models.inventory import InventoryUpdateData,InventoryBalanceUpdateValidation, Payload
from app.models.product import SpreadsheetProductData,ProductData,ListOfPurchases
from app.utils import EnvVariablesGetter, utc_to_local
from app.zettle.data_fetchers import ProductDataFetcher, PurchasesFetcher
from datetime import datetime, timedelta
from app.db.models import InventoryBalanceUpdateModel 

import logging

logger: logging.Logger = logging.getLogger(name=__name__)

class InventoryBalanceUpdater:
    def __init__(self, inventory_balance_update:InventoryBalanceUpdateValidation, engine:Engine) -> None:
        self.inventory_balance_update: InventoryBalanceUpdateValidation = inventory_balance_update
        self.database:InventoryUpdateRepository = InventoryUpdateRepository(engine=engine)
        
    def store_inventory_update(self) -> None:
        list_of_updates:list[InventoryBalanceUpdateModel] = []
        for i in range(len(self.inventory_balance_update.payload.balanceBefore)):
            payload: Payload = self.inventory_balance_update.payload
            local_timezone: datetime = utc_to_local(utc_dt=payload.updated.timestamp)
            object = InventoryBalanceUpdateModel(
                timestamp=local_timezone,
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
    def __init__(
            self,
            inventory_changes:Sequence[InventoryBalanceUpdateModel],
            start_date:datetime,end_date:datetime) -> None:
        
        self.inventory_changes:Sequence[InventoryBalanceUpdateModel] = inventory_changes
        self.start_date: datetime =start_date
        self.end_date:datetime = end_date
        self._inventory_update_joined:dict[tuple[UUID,UUID], InventoryUpdateData] = {}
    
    def join_inventory_update_data(self) -> dict[tuple[UUID,UUID], InventoryUpdateData]:
        # fetch stored inventory updates
        logger.info(msg="start inventor data joining")
        for update in self.inventory_changes:
            key:tuple[UUID,UUID] = (update.product_id, update.variant_id)
            change:int = update.after - update.before
            if key in self._inventory_update_joined:
                self._inventory_update_joined[key].updated_value += change
            else:
                self._inventory_update_joined[key] = InventoryUpdateData(
                    stock=update.before,
                    updated_value=update.after,
                    timestamp=update.timestamp,
                )
        logger.info(msg=f"Inventory data was joined products count: '{self._inventory_update_joined}")
        return self._inventory_update_joined
    
class PurchaseDataJoiner:
    def __init__(self,start_date:datetime,end_date:datetime):
        self.start_date: datetime =start_date
        self.end_date:datetime = end_date
        self._purchases_joined:dict[tuple[UUID,UUID], int ] = {}

    
    def join_purchase_update_data(self,purchases:ListOfPurchases) -> dict[tuple[UUID,UUID], int]:
        # fetch stored inventory updates

        validated_purchases:ListOfPurchases = ListOfPurchases.model_validate(obj=purchases)

        for purchases_iter in validated_purchases.purchases:
            for product_iter in purchases_iter.products:
                if purchases_iter.refund:
                    continue 
                key:tuple[UUID,UUID] = (product_iter.productUuid, product_iter.variantUuid)
                quantity:int = product_iter.quantity
                if key not in self._purchases_joined:
                    self._purchases_joined[key] = quantity
                else:
                    self._purchases_joined[key] += quantity
        return self._purchases_joined
                    

class InventoryManualChangesChecker:
    def __init__(
            self,
            purchases_merged:dict[tuple[UUID,UUID],int],
            inventory_update_merged:dict[tuple[UUID,UUID],InventoryUpdateData],
            ) -> None:
        
        self.marge_inventory_update: dict[tuple[UUID,UUID],InventoryUpdateData] = inventory_update_merged
        self.marge_purchases_update: dict[tuple[UUID,UUID],int] = purchases_merged

    def get_manual_changes(self) -> dict[tuple[UUID, UUID], InventoryUpdateData]:
        for purchase, value in self.marge_purchases_update.items():
            self.marge_inventory_update[purchase].updated_value = self.marge_inventory_update[purchase].updated_value + value
            if self.marge_inventory_update[purchase].stock == self.marge_inventory_update[purchase].updated_value:
                del self.marge_inventory_update[purchase]
        return self.marge_inventory_update
            

class ManualProductData:
    def __init__(
            self,
            manual_changes: dict[tuple[UUID,UUID],InventoryUpdateData],
            organization_id:str,
            product_data_fetcher:ProductDataFetcher) -> None:
        
        self.manual_changes: dict[tuple[UUID,UUID],InventoryUpdateData] = manual_changes
        self.organization_id: str = organization_id
        self.data_fetcher:ProductDataFetcher = product_data_fetcher
        self.list_of_products:list[SpreadsheetProductData] = []
    
    def get_manual_changes_product_data(self) -> list[SpreadsheetProductData]:
        for key,value in self.manual_changes.items():
            product_data:dict = self.data_fetcher.get_product_data(
                product_uuid=str(object=key[0]), 
                organization_id=self.organization_id)
        
            validated_product_data:ProductData = ProductData.model_validate(obj=product_data)
            
            for variant in validated_product_data.variants:
                if variant.uuid == key[1]:
                    product:SpreadsheetProductData = SpreadsheetProductData(
                        name=validated_product_data.name,
                        variant_name=str(object=variant.name),
                        product_variant_uuid=f"{str(key[0])},{str(key[1])}",
                        category_name=(
                            validated_product_data.category.name
                            if validated_product_data.category is not None
                            else "None"
                        ),
                        price=(
                            variant.price.amount // 100
                            if variant.price is not None
                            else "None"
                        ),
                        after=value.updated_value,
                        before=value.stock,
                        timestamp= value.timestamp,
                        organization_id=self.organization_id
                    )
                    self.list_of_products.append(product)
                    
        return self.list_of_products


class InventoryManualDataCollector:
    def __init__(
            self,repo_updater:InventoryUpdateRepository, 
            shop_name:str, 
            start_date:datetime, 
            end_date:datetime) -> None:
        
        self.purchase_fetcher:PurchasesFetcher = PurchasesFetcher(shop_name=shop_name)
        self.repo_updater:InventoryUpdateRepository = repo_updater
        self._purchases_joined_joined:dict[frozenset[UUID], int] = {}
        self.variable_getter:EnvVariablesGetter = EnvVariablesGetter()
        self.end_date:datetime = datetime.now()
        self.shop_name: str = shop_name
        self.start_date: datetime = start_date
        self.end_date:datetime = end_date

    def get_manual_changed_products(self) -> list[SpreadsheetProductData] | None:
        self.variable_getter = EnvVariablesGetter()
        organization_id: str = str(object=UUID(hex=self.variable_getter.\
            get_env_variable(variable_name=f"ZETTLE_{self.shop_name.upper()}_ORGANIZATION_UUID")))

        #fetch inventory data from database
        inventory_updates: Sequence[InventoryBalanceUpdateModel] = self.repo_updater.fetch_data_by_date_interval(
            start_date=self.start_date,
            end_date=self.end_date)
        
        if not inventory_updates:
            return None
        
        # inventory update data joining
        inventory_data_joiner = InventoryUpdatesDataJoiner(
            inventory_changes=inventory_updates,
            start_date=self.start_date,
            end_date=self.end_date)
        
        inventory_data_joined: dict[tuple[UUID,UUID], InventoryUpdateData] = inventory_data_joiner.join_inventory_update_data()

        # purchases data joining
        purchases_joiner = PurchaseDataJoiner(
            start_date=self.start_date,
            end_date=self.end_date)
        
        # get purchases by time interval
        purchases: dict[Any,Any] = self.purchase_fetcher.get_purchases(
            start_date=self.start_date - timedelta(hours=1),
            end_date=self.end_date - timedelta(hours=1),
        )

        validate_purchases:ListOfPurchases = ListOfPurchases.model_validate(obj=purchases)
        purchases_data_merged: dict[tuple[UUID,UUID], int] = purchases_joiner.join_purchase_update_data(purchases=validate_purchases)

        # minus purchases changes to get manual ones
        inventory_manual_checker = InventoryManualChangesChecker(
            inventory_update_merged=inventory_data_joined,
            purchases_merged=purchases_data_merged,
        )

        manual_changes: dict[tuple[UUID,UUID], InventoryUpdateData] = inventory_manual_checker.get_manual_changes()

        # get product data for manual changes
        product_data_fetcher:ProductDataFetcher = ProductDataFetcher(shop_name=self.shop_name) 
        product_data_manual = ManualProductData(
            manual_changes=manual_changes,
            organization_id=organization_id,
            product_data_fetcher=product_data_fetcher)
        
        product_data_with_manual_changes:list[SpreadsheetProductData] =  product_data_manual.get_manual_changes_product_data()
        return product_data_with_manual_changes



