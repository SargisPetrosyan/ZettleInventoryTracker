from services.google_drive.client import SpreadSheetClient, GoogleDriveClient
from services.google_drive.drive_manager import DriveFileManager
from services.google_drive.sheet_manager import SheetFileManager, SheetManager
from services.google_drive.product_dataframe import ProductDataFrame
from services.zettle.validaton import InventoryBalanceChanged, ProductData  # type:ignore
from dotenv import load_dotenv
from pydantic import BaseModel
from services.utils import FileName
import json
from services.utils import check_stock_in_or_out
import config

import config

from dotenv import load_dotenv

ROOT_FOLDER: str = config.ROOT_FOLDER_ID
DAY_TEMPLATE: str = config.DAY_TEMPLATE


with open("data/InventoryBalanceChanged.json", "r") as fp:
    INVENTORY_UPDATE = json.load(fp)
with open("data/Product.json", "r") as fp:
    PRODUCT_UPDATE = json.load(fp)

load_dotenv()


class ZettleWebhookHandler:
    def __init__(self) -> None:
        self.drive_client: GoogleDriveClient = GoogleDriveClient()
        self.sheet_client: SpreadSheetClient = SpreadSheetClient()

    def process_webhook(self):
        # validating webhook data
        inventory_update = InventoryBalanceChanged(**INVENTORY_UPDATE)

        drive_file_manager = DriveFileManager(self.drive_client)
        name = FileName(date=inventory_update.timestamp)

        # check if year folder exist
        folder_id: None | str = drive_file_manager.file_exist(
            file_name=name.year,
            parent_folder_id=ROOT_FOLDER,
            folder=True,
            page_size=100,
        )

        drive_file_manager.if_miss_create_folder(
            folder=folder_id,
            name=name,
            parent_folder_id=folder_id,
            sample_file_id=DAY_SAMPLE,
        )
