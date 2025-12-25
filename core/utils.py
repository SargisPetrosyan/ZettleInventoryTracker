from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
import json
from multiprocessing import managers
from uuid import UUID
import logging
from tracemalloc import start
from typing import Any, Sequence
import uuid
from fastapi import Request
from gspread.worksheet import JSONResponse
import rich
from const import MONTH_PRODUCT_STOCK_IN_COL_OFFSET, SHOP_SUBSCRIPTION_EVENTS, WEBHOOK_ENDPOINT_NAME
from core.google_drive.client import GoogleDriveClient, SpreadSheetClient
from core.google_drive.drive_manager import GoogleDriveFileManager
from core.google_drive.sheet_manager import SpreadSheetFileManager
import os
from const import (
    DALA_SHOP,
    ART_AND_CRAFT,
    CAFE,
)
from core.repositories import InventoryUpdateRepository
from core.type_dict import ListOfProductData, Product
from core.zettle.data_fetchers import ProductDataFetcher, PurchasesFetcher
from core.zettle.validation.product_validating import ProductData
from core.zettle.validation.purchase_validation import ListOfPurchases, Purchases
from models import InventoryBalanceUpdateModel

logger: logging.Logger = logging.getLogger(name=__name__)
import os
from dotenv import load_dotenv

load_dotenv()

class EnvVariablesGetter:
    def get_env_variable(self,variable_name:str) -> str:
        variable: str | None = os.getenv(variable_name)

        if not variable:
            raise TypeError(f"env variable by name '{variable_name}' cant be NONE ")
        
        return variable



class FileName:
    def __init__(self, date: datetime) -> None:
        logger.info(f"initializing file name")
        self.year: str = str(object=date.year)
        self.year_folder_name: str = str(object=date.year)
        self.month: str = str(object=date.month).zfill(2)
        self.day: str = str(object=date.day).zfill(2)
        self.day_worksheet_name: str = self.day
        self.month_file_name: str = str(object=date.strftime("%B"))
        self.day_file_name: str = f"{self.year}-{self.month}-{self.month_file_name}"
        self.month_worksheet_name: str = self.day_file_name
        self.monthly_report_name: str = f"{self.year}-monthly report"
        self.month_stock_in_and_out_col_index: int = int(self.day) + MONTH_PRODUCT_STOCK_IN_COL_OFFSET
        self.month_stock_out_row_index:int = int(self.day) + 1
        logger.info(f"file name was created 'file_name: {self.day_file_name}'")


def check_stock_in_or_out(before: int, after: int, change: int) -> dict[str, int]:
    logger.info("check if product update stock_in or stock out")
    if before > after:
        logger.info(f" product is 'stock_out' 'before: {before} > after: {after}'")
        return {"stock_in": 0, "stock_out": change, "before": before}
    else:
        logger.info(f" product is 'stock_in' 'before: {before} < after: {after}'")
        return {"stock_in": change, "stock_out": 0, "before": before}


def sheet_exist(items: dict[str, int], sheet_name: str) -> int | None:
    for sheet, index in items.items():
        if sheet == sheet_name:
            return index
    return None


def get_row_from_response(response: JSONResponse) -> int:
    product_update_data: str = response["updates"]["updatedRange"]
    product_row_position: str = product_update_data.split("!")[-1]
    if ":" in product_row_position:
        product_row_number: str = product_row_position.split(":")[0][1:]
        return int(product_row_number)
    else:
        product_row_number: str = product_row_position[0][1:]
        return int(product_row_number)


class ManagersCreator:
    def __init__(self) -> None:
        self._spreadsheet_client = SpreadSheetClient()
        self._google_drive_client = GoogleDriveClient()
        self._spreadsheet_manager = SpreadSheetFileManager(
            client=self._spreadsheet_client
        )
        self._google_drive_manager = GoogleDriveFileManager(
            client=self._google_drive_client
        )

    @property
    def google_drive_manager(self) -> GoogleDriveFileManager:
        return self._google_drive_manager

    @property
    def spreadsheet_manager(self) -> SpreadSheetFileManager:
        return self._spreadsheet_manager


class ZettleCredsPathManager:
    def __init__(self,shop_name:str) -> None:      
        BASE_DIR: str = os.path.dirname(p=os.path.abspath(path=__file__))
        self.token_path: str = os.path.abspath(
            path=os.path.join(BASE_DIR, f"../creds/zettle/{shop_name}_access_token.json")
        )

        self.credentials_path: str = os.path.abspath(
            path=os.path.join(BASE_DIR, f"../creds/zettle/{shop_name}_credentials.json")
        )

class CredentialContext():
    def __init__(self,shop_name:str) -> None:
        self.name: str = shop_name
        self._subscription_uuid: str | None = os.getenv(key=f"ZETTLE_{shop_name.upper()}_SUBSCRIPTION_UUID")
        self._destination_url: str | None = os.getenv(key="DESTINATION_URL")
        self._mail: str | None = os.getenv(key="MAIL")
        self.events: list[str] = SHOP_SUBSCRIPTION_EVENTS

    @property
    def subscription_uuid(self)-> str:
        if self._subscription_uuid is None:
            raise TypeError(f"{self.name} subscription_uuid cant be None")
        return self._subscription_uuid 
    
    @property
    def destination_url(self)-> str:
        if self._destination_url is None:
            raise TypeError(f"{self.name} destination_url cant be None")
        return self._destination_url + WEBHOOK_ENDPOINT_NAME
    
    @property
    def mail(self)-> str:
        if self._mail is None:
            raise TypeError(f"{self.name} mail cant be None")
        return self._mail 
    
class DateRangeBuilder:
    def __init__(self,end_date:datetime,interval_by_hours:int) -> None:
        start_date:datetime = end_date - timedelta(hours=interval_by_hours)
        self.start_date:str = start_date.isoformat()
        self.end_date:str = end_date.isoformat()


class OrganizationsNameMappedId:
    def __init__(self) -> None:
        self.organizations: dict[str | None, str] = {
            os.getenv("ZETTLE_ART_ORGANIZATION_UUID"):ART_AND_CRAFT,
            os.getenv("ZETTLE_DALA_ORGANIZATION_UUID"):DALA_SHOP,
            os.getenv("ZETTLE_CAFE_ORGANIZATION_UUID"):CAFE,
        } 

    def get_name_by_id(self,shop_id:str) -> str:
        organization_name: str | None = self.organizations.get(shop_id,None)
        if not organization_name:
            raise TypeError("organization uuid is missing")
        return organization_name

async def json_to_dict(request:Request)-> dict:
    body: bytes = await request.body()
    data = json.loads(body)
    data["payload"] = json.loads(data["payload"])
    return data


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
                self.marge_inventory_update[purchase] = self.marge_inventory_update[purchase] - value
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



