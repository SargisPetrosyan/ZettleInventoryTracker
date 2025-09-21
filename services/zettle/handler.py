from services.google_drive.client import SpreadSheetClient, GoogleDriveClient
from services.google_drive.drive_manager import DriveFileManager
from services.google_drive.sheet_manager import (
    SpreadSheetFileManager,
    SpreadSheetManager,
)
from gspread.spreadsheet import Spreadsheet
from services.google_drive.product_dataframe import ProductDataFrame
from services.zettle.validaton import InventoryBalanceChanged, ProductData  # type:ignore
from dotenv import load_dotenv
from pydantic import BaseModel
from services.utils import FileName
import json
from services.utils import check_stock_in_or_out, sheet_exist
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
        self.spreadsheet_client: SpreadSheetClient = SpreadSheetClient()

    def process_webhook(self):
        # validating webhook data
        inventory_update = InventoryBalanceChanged(**INVENTORY_UPDATE)

        # defining managers
        drive_file_manager = DriveFileManager(self.drive_client)
        spreadsheet_file_manager = SpreadSheetFileManager(self.spreadsheet_client)
        name = FileName(date=inventory_update.timestamp)

        # check if year folder exist
        year_folder_id = drive_file_manager.file_exist(
            file_name=name.year,
            parent_folder_id=ROOT_FOLDER,
            folder=True,
            page_size=100,
        )

        if not year_folder_id:
            year_folder_id = drive_file_manager.create_year_folder(
                year=name.year,
                parent_folder_id=ROOT_FOLDER,
            )

        if not drive_file_manager.file_exist(
            file_name=name.month_name,
            parent_folder_id=year_folder_id,
            folder=False,
            page_size=20,
        ):
            spreadsheet_id: str = spreadsheet_file_manager.copy_spreadsheet(
                spreadsheet_id=DAY_TEMPLATE,
                title=name.month_name,
                folder_id=ROOT_FOLDER,
            )

        list_of_sheets = spreadsheet_file_manager.get_worksheets_with_ids(
            spreadsheet_id=spreadsheet_id
        )

        if not sheet_exist(sheet_name=name.month_name, items=list_of_sheets):
            spreadsheet_file_manager.copy_sheet_to_spreadsheet(
                spreadsheet_id=DAY_TEMPLATE,
                destination_spreadsheet_id=spreadsheet_id,
                sheet_id=0,
            )

        # if not sheet:
        #     spreadsheet_file_manager.copy_sheet_to_spreadsheet(
        #         spreadsheet_id=DAY_TEMPLATE,
        #         destination_spreadsheet_id=spreadsheet_id
        #         sheet_id=
        #     )
        # # defining spreadsheet manager
        # spreadsheet = SpreadSheetManager(
        #     spreadsheet_id=spreadsheet_id,
        #     worksheet_name=name.month,
        #     client=self.spreadsheet_client,
