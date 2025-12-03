from const import (
    ART_CRAFT_FOLDER_ID,
    DALA_CAFFE_FOLDER_ID,
    DALASHOP_FOLDER_ID,
)
import logging

logger: logging.Logger = logging.getLogger(name=__name__)

from source.utils import FileName
from datetime import datetime

from source.zettle.validaton import InventoryBalanceChanged, ProductData


class Context:
    def __init__(
        self,
        date: datetime,
        inventory_balance_update: InventoryBalanceChanged,
        product_data: ProductData,
    ) -> None:
        self.parent_folder_id: str = ""
        self.year_folder_id: str = ""
        self.day_spreadsheet_id: str = ""
        self.month_spreadsheet_id: str = ""
        self.name = FileName(date=date)
        self.product_update: InventoryBalanceChanged = inventory_balance_update
        self.product_data: ProductData = product_data
        self.stock_in_out = StockInOrOut(product_update=self.product_update)


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
