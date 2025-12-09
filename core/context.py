from const import (
    ART_CRAFT_FOLDER_ID,
    DALA_CAFFE_FOLDER_ID,
    DALASHOP_FOLDER_ID,
)
import logging

logger: logging.Logger = logging.getLogger(name=__name__)

from core.utils import FileName
from datetime import datetime

from core.zettle.validaton import InventoryBalanceChanged, ProductData


class Context:
    def __init__(
        self,
        date: datetime,
        inventory_balance_update: InventoryBalanceChanged,
        product_data: ProductData,
    ) -> None:
        self._parent_folder_id: str | None = None
        self._year_folder_id: str | None = None
        self._day_spreadsheet_id: str | None = None
        self._month_spreadsheet_id: str | None = None
        self.name = FileName(date=date)
        self.product_update: InventoryBalanceChanged = inventory_balance_update
        self.product_data: ProductData = product_data
        self.stock_in_out = StockInOrOut(product_update=self.product_update)

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
    def __init__(self, product_update: InventoryBalanceChanged) -> None:
        self.stock_in: int = 0
        self.stock_out: int = 0
        self.change: int = 0
        self.before: int = 0

        logger.info("check if product update stock_in or stock out")
        before: int = product_update.inventory.before
        after: int = product_update.inventory.after
        change: int = product_update.inventory.change
        if product_update.inventory.before > product_update.inventory.after:
            logger.info(f" product is 'stock_out' 'before: {before} > after: {after}'")
            self.stock_out: int = change
            self.before: int = before
        else:
            logger.info(f" product is 'stock_in' 'before: {before} < after: {after}'")
            self.stock_in: int = change
            self.before: int = before
