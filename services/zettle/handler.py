from services.google_drive.client import SpreadSheetClient, GoogleDriveClient
from services.google_drive.drive_manager import DriveFileManager
from services.google_drive.sheet_manager import (
    SpreadSheetFileManager,
)
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from services.zettle.validaton import InventoryBalanceChanged  # type:ignore
from services.utils import FileName
import json
import config

from dotenv import load_dotenv

ROOT_FOLDER: str = config.ROOT_FOLDER_ID
DAY_TEMPLATE: str = config.DAY_TEMPLATE
WORKSHEET_SAMPLE_NAME: str = config.WORKSHEET_SAMPLE_NAME


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

        # crete file name by date
        name = FileName(date=inventory_update.timestamp)

        # check if year folder exist if not create it
        year_folder_id: str | None = drive_file_manager.folder_exist_by_name(
            folder_name=name.year,
            parent_folder_id=ROOT_FOLDER,
            page_size=100,
        )

        if not year_folder_id:
            year_folder_id = drive_file_manager.create_year_folder(
                year=name.year,
                parent_folder_id=ROOT_FOLDER,
            )
        # Check if file exist, if not create it
        spreadsheet_id: str | None = drive_file_manager.spreadsheet_exist_by_name(
            spreadsheet_name=name.name,
            parent_folder_id=year_folder_id,
            page_size=100,
        )

        if not spreadsheet_id:
            spreadsheet_copy: Spreadsheet = spreadsheet_file_manager.copy_spreadsheet(
                spreadsheet_id=DAY_TEMPLATE,
                title=name.name,
                folder_id=year_folder_id,
            )

            spreadsheet_id = spreadsheet_copy.id

        # create spreadsheet_object
        spreadsheet: Spreadsheet = spreadsheet_file_manager.get_spreadsheet(
            spreadsheet_id=spreadsheet_id
        )

        # check if worksheet not exist create it
        worksheet: Worksheet | None = spreadsheet_file_manager.get_worksheet_by_title(
            spreadsheet=spreadsheet, title=name.day
        )

        if not worksheet:
            # copy sheet sample to spreadsheet
            spreadsheet_file_manager.copy_sheet_to_spreadsheet(
                spreadsheet_id=DAY_TEMPLATE,
                sheet_id=0,
                destination_spreadsheet_id=spreadsheet.id,
            )

            worksheet = spreadsheet.worksheet(WORKSHEET_SAMPLE_NAME)

            worksheet.update_title(name.day)

        # Check if SHEET worksheet sample exist, if exist delete
        if spreadsheet_file_manager.get_worksheet_by_title(
            spreadsheet=spreadsheet, title=WORKSHEET_SAMPLE_NAME
        ):
            spreadsheet_file_manager.delete_worksheet(
                spreadsheet=spreadsheet, title=WORKSHEET_SAMPLE_NAME
            )
