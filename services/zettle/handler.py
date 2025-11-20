import logging
from services.google_drive.client import SpreadSheetClient, GoogleDriveClient
from services.google_drive.drive_manager import DriveFileManager
from services.google_drive.sheet_manager import SpreadSheetFileManager, WorksheetManager
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from services.zettle.validaton import InventoryBalanceChanged, ProductData
from services.utils import FileName
from services.utils import check_stock_in_or_out
from services.google_drive.product_dataframe import ProductDataFrame
import json
import config

import logging

logger: logging.Logger = logging.getLogger(name=__name__)

ROOT_FOLDER: str = config.ROOT_FOLDER_ID
DAY_TEMPLATE: str = config.DAY_TEMPLATE
WORKSHEET_SAMPLE_NAME: str = config.WORKSHEET_SAMPLE_NAME
WORKSHEET_SAMPLE_COPY_NAME: str = config.WORKSHEET_SAMPLE_COPY_NAME

with open("data/Product.json", "r") as fp:
    PRODUCT_UPDATE = json.load(fp)

class ZettleWebhookHandler:
    def __init__(self) -> None:
        self.drive_client: GoogleDriveClient = GoogleDriveClient()
        self.spreadsheet_client: SpreadSheetClient = SpreadSheetClient()
        self.drive_file_manager = DriveFileManager(client=self.drive_client)
        self.spreadsheet_file_manager = SpreadSheetFileManager(client=self.spreadsheet_client)

    def process_webhook(self, request:dict) -> None:
        # validating webhook data
        logger.info("")
        inventory_update = InventoryBalanceChanged(**request)
        
        product_data = ProductData(**PRODUCT_UPDATE)
        
        # crete file name by date
        name = FileName(date=inventory_update.timestamp)

        # check if year folder exist if not create it
        year_folder_id: str | None = self.drive_file_manager.folder_exist_by_name(
            folder_name=name.year,
            parent_folder_id=ROOT_FOLDER,
            page_size=100,
        )

        if not year_folder_id:
            year_folder_id = self.drive_file_manager.create_year_folder(
                year=name.year,
                parent_folder_id=ROOT_FOLDER,
            )
            
        # Check if file exist, if not create it
        spreadsheet_id: str | None = self.drive_file_manager.spreadsheet_exist_by_name(
            spreadsheet_name=name.file_name,
            parent_folder_id=year_folder_id,
            page_size=100,
        )

        if not spreadsheet_id:
            spreadsheet_copy: Spreadsheet = self.spreadsheet_file_manager.copy_spreadsheet(
                spreadsheet_id=DAY_TEMPLATE,
                title=name.file_name,
                folder_id=year_folder_id,
            )

            spreadsheet_id = spreadsheet_copy.id

        # create spreadsheet_object
        spreadsheet: Spreadsheet = self.spreadsheet_file_manager.get_spreadsheet(
            spreadsheet_id=spreadsheet_id
        )

        # check if worksheet not exist create it
        worksheet: Worksheet | None = self.spreadsheet_file_manager.get_worksheet_by_title(
            spreadsheet=spreadsheet, title=name.day
        )

        if not worksheet:
            # copy sheet sample to spreadsheet
            self.spreadsheet_file_manager.copy_sheet_to_spreadsheet(
                spreadsheet_id=DAY_TEMPLATE,
                sheet_id=0,
                destination_spreadsheet_id=spreadsheet.id,
            )

            worksheet = spreadsheet.worksheet(title=WORKSHEET_SAMPLE_NAME)

            worksheet.update_title(title=name.day)

        # Check if SHEET worksheet sample exist, if exist delete
        if self.spreadsheet_file_manager.get_worksheet_by_title(
            spreadsheet=spreadsheet, title=WORKSHEET_SAMPLE_COPY_NAME
        ):
            self.spreadsheet_file_manager.delete_worksheet(
                spreadsheet=spreadsheet, title=WORKSHEET_SAMPLE_COPY_NAME
            )

        # create worksheet manager
        worksheet_manager = WorksheetManager(worksheet=worksheet)

        # get raw data of worksheet for pandas
        worksheet_raw_data: list = worksheet_manager.get_raw_data()

        # convert sheet to pandas DataFrame
        dataframe: ProductDataFrame = ProductDataFrame(sheet=worksheet_raw_data)

        product_exist: bool = dataframe.product_exist(
            product_name=product_data.name
        )
        
        stock_in_or_out: dict[str, int] = check_stock_in_or_out(
            before=inventory_update.inventory.before,
            after=inventory_update.inventory.after,
            change=inventory_update.inventory.change,
        )

        if not product_exist:
            last_row: int = dataframe.last_row_index()

            worksheet_manager.add_product(
                product_name=product_data.name,
                category=product_data.category,
                stock_in=stock_in_or_out["stock_in"],
                stock_out=stock_in_or_out["stock_out"],
                opening_stock=stock_in_or_out["before"],
                last_row=last_row,
            )
        else:
            if stock_in_or_out["stock_out"] == 0:
                # increment it in dataframe
                increment_in: dict = dataframe.increment_stock_in(
                    product_name=product_data.name, amount=stock_in_or_out["stock_in"]
                )
                
                # update_worksheet
                worksheet_manager.update_stock_in(
                    value=increment_in["value"], row=increment_in["row"]
                )
            if stock_in_or_out["stock_in"] == 0:
                # increment it in dataframe
                increment_out: dict = dataframe.increment_stock_out(
                    product_name=product_data.name, amount=stock_in_or_out["stock_out"]
                )
                
                # update_worksheet
                worksheet_manager.update_stock_out(
                    value=increment_out["value"], row=increment_out["row"]
                )
        
        