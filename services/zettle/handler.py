from services.google_drive.client import SpreadSheetClient,GoogleDriveClient
from services.google_drive.drive_manager import DriveFileManager
from services.google_drive.sheet_manager import SheetFileManager, SheetManager
from services.zettle.validaton import InventoryBalanceChanged, ProductData  # type:ignore
from dotenv import load_dotenv
from pydantic import BaseModel
from services.google_drive.utils import FileName
import json

import os 
from dotenv import load_dotenv

load_dotenv()

ROOT_FOLDER = os.getenv("ROOT_FOLDER_ID")
DAY_SAMPLE = os.getenv("DAY_TEMPLATE_SAMPLE_ID")


with open("data/InventoryBalanceChanged.json", "r") as fp:
    INVENTORY_UPDATE = json.load(fp)
with open("data/Product.json", "r") as fp:
    PRODUCT_UPDATE = json.load(fp)

load_dotenv()


class ZettleWebhookHandler:
    def __init__(self) -> None:
        self.drive_client:GoogleDriveClient = GoogleDriveClient()
        self.sheet_client:SpreadSheetClient = SpreadSheetClient()

        

    def process_webhook(self):
        inventory_update:BaseModel = InventoryBalanceChanged(**INVENTORY_UPDATE)
        product_update:BaseModel = ProductData(**PRODUCT_UPDATE)
        
        
        drive_file_manege:DriveFileManager = DriveFileManager(self.drive_client)
        
        name = FileName(date=inventory_update.timestamp)
        
        
        if not self.drive_client.file_exist(file_name=name.year, folder_id=ROOT_FOLDER, folder=True):
            drive_file = drive_file_manege.create_year_folder(
                year=name.year, 
                parent_folder_id=ROOT_FOLDER,
                sample_file_id=DAY_SAMPLE,
                nested_file_name=name.name)
            drive_file_id = drive_file.get("id")
        sheet_file_manege = SheetFileManager(client=self.sheet_client), 
        sheet_manager = SheetManager(client=self.sheet_client, spreadsheet_id=drive_file_id, worksheet_name=name.month)

        
        
        
        

        

test = ZettleWebhookHandler()

test.process_webhook()

