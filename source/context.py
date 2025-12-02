from const import (
    ART_CRAFT_FOLDER_ID,
    DALA_CAFFE_FOLDER_ID,
    DALASHOP_FOLDER_ID,
)
from source.services import StockInOrOut
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

        self.shop_unique_id_mapping: dict[str, str] = {
            "dala_id": DALASHOP_FOLDER_ID,
            "art_id": ART_CRAFT_FOLDER_ID,
            "caffe_id": DALA_CAFFE_FOLDER_ID,
        }

        self.name = FileName(date=date)
        self.product_update: InventoryBalanceChanged = inventory_balance_update
        self.product_data: ProductData = product_data

        self.stock_in_out = StockInOrOut(product_update=self.product_update)
