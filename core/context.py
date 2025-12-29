from datetime import datetime
import logging

from core.type_dict import Product
from core.utils import FileName
from core.zettle.validation.inventory_update_validation import InventoryBalanceUpdateValidation

logger: logging.Logger = logging.getLogger(name=__name__)


class Context:
    def __init__(
        self,
        inventory_manual_update: Product,
    ) -> None:
        
        self._parent_folder_id: str | None = None
        self._year_folder_id: str | None = None
        self._day_spreadsheet_id: str | None = None
        self._month_spreadsheet_id: str | None = None
        self.name:FileName = FileName(date=self.product_inventory_update.timestamp)
        self.product_inventory_update: Product = inventory_manual_update

    @property
    def parent_folder_id(self) -> str:
        if not self._parent_folder_id:
            raise TypeError("parent_folder_id cant be NONE")
        return self._parent_folder_id

    @property
    def year_folder_id(self) -> str:
        if not self._year_folder_id:
            raise TypeError("year_folder_id cant be NONE")
        return self._year_folder_id

    @property
    def day_spreadsheet_id(self) -> str:
        if not self._day_spreadsheet_id:
            raise TypeError("day_spreadsheet_id cant be NONE")
        return self._day_spreadsheet_id

    @property
    def month_spreadsheet_id(self) -> str:
        if not self._month_spreadsheet_id:
            raise TypeError("month_spreadsheet_id cant be NONE")
        return self._month_spreadsheet_id
    
    @property
    def category(self) -> str:
        if not self.product_inventory_update.category:
            logger.info("category is NONE")
            return "None"
        return self.product_inventory_update.category

    
    @property
    def variant(self) -> str:
        if not self.product_inventory_update.variant_name:
            logger.info("variant is NONE")
            return "None"
        return self.product_inventory_update.variant_name
    
    @property
    def stock_in_or_out(self) -> int:
        if self.product_inventory_update.manual_change > 0:
            logger.info("product inventory change is stock in")
            return self.product_inventory_update.manual_change
        logger.info("product inventory change is stock out")
        return self.product_inventory_update.manual_change
    
    @property
    def price(self) -> int:
        if not self.product_inventory_update.price:
            raise TypeError("price timestamp cant be NONE")
        return self.product_inventory_update.price // 100 #in zettle value has 2 extra 00 digits


    @parent_folder_id.setter
    def parent_folder_id(self, id: str) -> None:
        self._parent_folder_id = id

    @year_folder_id.setter
    def year_folder_id(self, id: str) -> None:
        self._year_folder_id = id

    @day_spreadsheet_id.setter
    def day_spreadsheet_id(self, id: str) -> None:
        self._day_spreadsheet_id = id

    @month_spreadsheet_id.setter
    def month_spreadsheet_id(self, id: str) -> None:
        self._month_spreadsheet_id = id


class StockInOrOut:
    def __init__(self, product_update: InventoryBalanceUpdateValidation) -> None:
        self.stock_in: int = 0
        self.stock_out: int = 0
        self.change: int = 0
        self.before: int = 0

        logger.info("check if product update stock_in or stock out")
        before: int = product_update.payload.balanceBefore[0].balance
        after: int = product_update.payload.balanceAfter[0].balance
        change: int = abs(before) 
        if product_update.payload.inventory.before > product_update.payload.inventory.after: #type:ignore
            logger.info(f" product is 'stock_out' 'before: {before} > after: {after}'")
            self.stock_out: int = change
            self.before: int = before
        else:
            logger.info(f" product is 'stock_in' 'before: {before} < after: {after}'")
            self.stock_in: int = change
            self.before: int = before
