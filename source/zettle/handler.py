import logging
from os import name

from source.context import Context
from source.google_drive.drive_manager import DriveFileManager
from source.google_drive.sheet_manager import (
    SpreadSheetFileManager,
)
from const import DAY_TEMPLATE_ID, MONTHLY_TEMPLATE_ID,ROOT_FOLDER_ID
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from source.services import (
    DaySpreadsheetFileManager,
    MonthSpreadsheetFileManager,
    ProductDataUpdater,
    ProductManager,
    WorksheetManager,
    YearFolderManger,
)
from source.zettle.validaton import InventoryBalanceChanged, ProductData
import json
import logging

logger: logging.Logger = logging.getLogger(name=__name__)


with open("data/Product.json", "r") as fp:
    PRODUCT_UPDATE = json.load(fp)


class ZettleWebhookHandler:
    def __init__(
        self,
        google_drive_file_manager: DriveFileManager,
        spreadsheet_file_manager: SpreadSheetFileManager,
    ) -> None:
        self.google_drive_file_manager: DriveFileManager = google_drive_file_manager
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manager
        self.year_folder_manager = YearFolderManger(
            drive_file_manager=self.google_drive_file_manager,
            spreadsheet_file_manege=self.spreadsheet_file_manager,
        )
        self.day_spreadsheet_file_manager = DaySpreadsheetFileManager(
            drive_file_manager=self.google_drive_file_manager,
            spreadsheet_file_manager=self.spreadsheet_file_manager,
        )
        self.monthly_spreadsheet_file_manager = MonthSpreadsheetFileManager(
            drive_file_manager=self.google_drive_file_manager,
            spreadsheet_file_manager=self.spreadsheet_file_manager,
        )
        self.worksheet_manager = WorksheetManager(
            spreadsheet_file_manager=self.spreadsheet_file_manager
        )
        self.product_data_updater = ProductDataUpdater()

    def process_webhook(self, request: InventoryBalanceChanged) -> None:
        product_data = ProductData(**PRODUCT_UPDATE)

        context = Context(
            date=request.timestamp,
            inventory_balance_update=request,
            product_data=product_data,
        )

        # step 1 ensure year folder:
        self.year_folder_manager.ensure_year_folder(context=context)

        # step 2 ensure day and month spreadsheets
        day_spreadsheet: Spreadsheet = (
            self.day_spreadsheet_file_manager.ensure_day_spreadsheet(context=context,)
        )

        month_spreadsheet: Spreadsheet = (
            self.monthly_spreadsheet_file_manager.ensure_month_spreadsheet(context=context)
        )

        # step 3 ensure day and month worksheets:
        day_worksheet: Worksheet = self.worksheet_manager.ensure_worksheet(
            spreadsheet=day_spreadsheet,
            name=context.name.day_worksheet_name,
            template_spreadsheet_id=DAY_TEMPLATE_ID,
        )

        month_worksheet: Worksheet = self.worksheet_manager.ensure_worksheet(
            spreadsheet=month_spreadsheet,
            name=context.name.month_worksheet_name,
            template_spreadsheet_id=MONTHLY_TEMPLATE_ID,
        )

        # step 4 ensure product:
        product_manager = ProductManager(
            month_worksheet=month_worksheet,
            day_worksheet=day_worksheet,
            context=context,
        )

        # step 5 update product remote
        product_manager.ensure_and_update_product(context=context)

    