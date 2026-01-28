
import datetime
import rich
from app.google_drive.context import Context
from app.google_drive.dataframe_manager import DayProductDataFrameManager, ProductDataframeManager
from app.google_drive.drive_manager import GoogleDriveFileManager
from app.google_drive.sheet_manager import SpreadSheetFileManager
from app.constants import (
    DAY_TEMPLATE_ID, 
    MONTHLY_TEMPLATE_ID)
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from app.google_drive.services import (
    DayProductExistenceEnsurer,
    DaySpreadsheetExistenceEnsurer,
    MonthProductExistenceEnsurer,
    MonthSpreadsheetExistenceEnsurer,
    MonthWorksheetValueUpdater,
    WorksheetExistenceEnsurer,
    YearFolderExistenceEnsurer,
    DayWorksheetValueUpdater,
)
from app.models.product import SpreadsheetProductData
import logging

logger: logging.Logger = logging.getLogger(name=__name__)


class DriveManager:
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

    def process_data_to_drive(self, product: SpreadsheetProductData) -> None:

        context = Context(product_manual=product)

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
