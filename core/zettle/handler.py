import logging
from os import name

from core.context import Context
from core.google_drive.drive_manager import GoogleDriveFileManager
from core.google_drive.sheet_manager import (
    SpreadSheetFileManager,
)
from const import DAY_TEMPLATE_ID, MONTHLY_TEMPLATE_ID
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from core.services import (
    DayProductExistenceEnsurer,
    DaySpreadsheetExistenceEnsurer,
    MonthProductExistenceEnsurer,
    MonthSpreadsheetExistenceEnsurer,
    MonthWorksheetValueUpdater,
    WorksheetExistenceEnsurer,
    YearFolderExistenceEnsurer,
    DayWorksheetValueUpdater,
)
from core.validation.inventory_update_validation import InventoryBalanceChanged
from core.validation.product_validating import ProductData
import json
import logging

logger: logging.Logger = logging.getLogger(name=__name__)


with open("data/Product.json", "r") as fp:
    PRODUCT_UPDATE = json.load(fp)


class ZettleWebhookHandler:
    def __init__(
        self,
        google_drive_file_manager: GoogleDriveFileManager,
        spreadsheet_file_manager: SpreadSheetFileManager,
    ) -> None:
        self.google_drive_file_manager: GoogleDriveFileManager = (
            google_drive_file_manager
        )
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manager
        self.year_folder_manager = YearFolderExistenceEnsurer(
            drive_file_manager=self.google_drive_file_manager,
            spreadsheet_file_manege=self.spreadsheet_file_manager,
        )
        self.day_spreadsheet_existence_ensurer = DaySpreadsheetExistenceEnsurer(
            drive_file_manager=self.google_drive_file_manager,
            spreadsheet_file_manager=self.spreadsheet_file_manager,
        )
        self.monthly_spreadsheet_existence_ensurer = MonthSpreadsheetExistenceEnsurer(
            drive_file_manager=self.google_drive_file_manager,
            spreadsheet_file_manager=self.spreadsheet_file_manager,
        )
        self.worksheet_existence_ensurer = WorksheetExistenceEnsurer(
            spreadsheet_file_manager=self.spreadsheet_file_manager
        )

    def process_webhook(self, request: InventoryBalanceChanged) -> None:
        product_data = ProductData(**PRODUCT_UPDATE)

        context = Context(
            date=request.payload.updated.timestamp,
            inventory_balance_update=request,
            product_data=product_data,
        )

        # step 1 ensure year folder:
        self.year_folder_manager.ensure_year_folder(context=context)

        # step 2.1 ensure month spreadsheet
        month_spreadsheet: Spreadsheet = (
            self.monthly_spreadsheet_existence_ensurer.ensure_month_spreadsheet(
                context=context
            )
        )

        # step 2.2 ensure day spreadsheet
        day_spreadsheet: Spreadsheet = (
            self.day_spreadsheet_existence_ensurer.ensure_day_spreadsheet(
                context=context,
            )
        )

        # step 3.1 ensure day and month worksheets:
        day_worksheet: Worksheet = self.worksheet_existence_ensurer.ensure_worksheet(
            spreadsheet=day_spreadsheet,
            name=context.name.day_worksheet_name,
            template_spreadsheet_id=DAY_TEMPLATE_ID,
        )

        # step 3.2 ensure day worksheet:
        month_worksheet: Worksheet = self.worksheet_existence_ensurer.ensure_worksheet(
            spreadsheet=month_spreadsheet,
            name=context.name.month_worksheet_name,
            template_spreadsheet_id=MONTHLY_TEMPLATE_ID,
        )

        # step 4.1 ensure day worksheet product:
        day_product = DayProductExistenceEnsurer(day_worksheet=day_worksheet)
        day_product.ensure_day_product(context=context)

        # step 4.2 ensure day worksheet product:
        month_product = MonthProductExistenceEnsurer(month_worksheet=month_worksheet)
        month_product.ensure_month_product(context=context)

        # step 5.1 update day remote worksheet
        DayWorksheetValueUpdater.update_day_worksheet(
            day_worksheet_reader=day_product.day_worksheet_reader,
            day_worksheet_writer=day_product.day_worksheet_writer,
            context=context,
        )

        # step 5.2 update month remote worksheet
        MonthWorksheetValueUpdater.update_month_worksheet(
            month_worksheet_reader=month_product.month_worksheet_reader,
            month_worksheet_writer=month_product.month_worksheet_writer,
            context=context,
        )
