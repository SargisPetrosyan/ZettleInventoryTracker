from datetime import datetime
import logging
from gspread.worksheet import JSONResponse
from const import MONTH_PRODUCT_STOCK_IN_COL_OFFSET
from core.google_drive.client import GoogleDriveClient, SpreadSheetClient
from core.google_drive.drive_manager import GoogleDriveFileManager
from core.google_drive.sheet_manager import SpreadSheetFileManager

logger: logging.Logger = logging.getLogger(name=__name__)


class FileName:
    def __init__(self, date: datetime) -> None:
        logger.info(f"initializing file name")
        self.year: str = str(object=date.year)
        self.year_folder_name: str = str(object=date.year)
        self.month: str = str(object=date.month).zfill(2)
        self.day: str = str(object=date.day).zfill(2)
        self.day_worksheet_name: str = self.day
        self.month_file_name: str = str(object=date.strftime("%B"))
        self.day_file_name: str = f"{self.year}-{self.month}-{self.month_file_name}"
        self.month_worksheet_name: str = self.day_file_name
        self.monthly_report_name: str = f"{self.year}-monthly report"
        self.month_stock_in_and_out_col_index: int = int(self.day) + MONTH_PRODUCT_STOCK_IN_COL_OFFSET
        self.month_stock_out_row_index:int = int(self.day) + 1
        logger.info(f"file name was created 'file_name: {self.day_file_name}'")


def check_stock_in_or_out(before: int, after: int, change: int) -> dict[str, int]:
    logger.info("check if product update stock_in or stock out")
    if before > after:
        logger.info(f" product is 'stock_out' 'before: {before} > after: {after}'")
        return {"stock_in": 0, "stock_out": change, "before": before}
    else:
        logger.info(f" product is 'stock_in' 'before: {before} < after: {after}'")
        return {"stock_in": change, "stock_out": 0, "before": before}


def sheet_exist(items: dict[str, int], sheet_name: str) -> int | None:
    for sheet, index in items.items():
        if sheet == sheet_name:
            return index
    return None


def get_row_from_response(response: JSONResponse) -> int:
    product_update_data: str = response["updates"]["updatedRange"]
    product_row_position: str = product_update_data.split("!")[-1]
    if ":" in product_row_position:
        product_row_number: str = product_row_position.split(":")[0][1:]
        return int(product_row_number)
    else:
        product_row_number: str = product_row_position[0][1:]
        return int(product_row_number)


class ManagersCreator:
    def __init__(self) -> None:
        self._spreadsheet_client = SpreadSheetClient()
        self._google_drive_client = GoogleDriveClient()
        self._spreadsheet_manager = SpreadSheetFileManager(
            client=self._spreadsheet_client
        )
        self._google_drive_manager = GoogleDriveFileManager(
            client=self._google_drive_client
        )

    @property
    def google_drive_manager(self) -> GoogleDriveFileManager:
        return self._google_drive_manager

    @property
    def spreadsheet_manager(self) -> SpreadSheetFileManager:
        return self._spreadsheet_manager
