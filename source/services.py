from sqlite3 import Row
from gspread import Cell, Spreadsheet, Worksheet
from source import context
from source.context import Context
from source.google_drive.drive_manager import DriveFileManager
from source.google_drive.client import SpreadSheetClient, GoogleDriveClient
from const import (
    DAY_TEMPLATE_ID,
    WORKSHEET_SAMPLE_NAME,
    MONTHLY_TEMPLATE_ID,
    DALASHOP_FOLDER_ID,
)
import logging

from source.google_drive.sheet_manager import (
    DayWorksheetManager,
    MonthlyWorksheetProductManager,
    SpreadSheetFileManager,
)
from source.zettle.validaton import InventoryBalanceChanged

logger: logging.Logger = logging.getLogger(name=__name__)


class YearFolderManger:
    def __init__(
        self,
        drive_file_manager: DriveFileManager,
        spreadsheet_file_manege: SpreadSheetFileManager,
    ) -> None:
        self.drive_file_manager: DriveFileManager = drive_file_manager
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manege

    def ensure_year_folder(self, parent_folder_id: str, context: Context) -> None:
        year_folder_id: str | None = self.drive_file_manager.folder_exist_by_name(
            folder_name=context.name.year,
            parent_folder_id=parent_folder_id,
            page_size=100,
        )

        if not year_folder_id:
            logger.info(f"'year: {context.name.year}' was not found")

            year_folder_id = self.drive_file_manager.create_year_folder(
                year=context.name.year,
                parent_folder_id=parent_folder_id,
            )
            logger.info(f"new 'year: {context.name.year}' folder was created!!")

            # create mouthy report spreadsheet
            monthly_report_spreadsheet: Spreadsheet = (
                self.spreadsheet_file_manager.copy_spreadsheet(
                    spreadsheet_id=MONTHLY_TEMPLATE_ID,
                    title=context.name.monthly_report_name,
                    folder_id=year_folder_id,
                )
            )

            logger.info(
                f"monthly_report_spreadsheet, rename template names from 'WORKSHEET_SAMPLE_NAME to {context.name.monthly_report_name}'"
            )

            worksheet = monthly_report_spreadsheet.worksheet(
                title=WORKSHEET_SAMPLE_NAME
            )

            worksheet.update_title(title=context.name.day_file_name)

            day_spreadsheet: Spreadsheet = (
                self.spreadsheet_file_manager.copy_spreadsheet(
                    spreadsheet_id=DAY_TEMPLATE_ID,
                    title=context.name.day_file_name,
                    folder_id=year_folder_id,
                )
            )

            logger.info(
                f"day spreadsheet was created, renaming template names from 'WORKSHEET_SAMPLE_NAME to {context.name.day_worksheet_name}' was successfully done!!!"
            )

            # rename copied worksheet tamale name
            worksheet: Worksheet = day_spreadsheet.worksheet(
                title=WORKSHEET_SAMPLE_NAME
            )
            worksheet.update_title(title=context.name.day)
        context.year_folder_id = year_folder_id


class DaySpreadsheetFileManager:
    def __init__(
        self,
        drive_file_manager: DriveFileManager,
        spreadsheet_file_manager: SpreadSheetFileManager,
    ) -> None:
        self.drive_file_manager: DriveFileManager = drive_file_manager
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manager

    def ensure_day_spreadsheet(self, context: Context) -> Spreadsheet:
        if not context.year_folder_id:
            raise ValueError("year folder id not exist check it")

        spreadsheet_id: str | None = self.drive_file_manager.get_spreadsheet_by_name(
            spreadsheet_name=context.name.day_file_name,
            parent_folder_id=context.year_folder_id,
            page_size=100,
        )

        if not spreadsheet_id:
            logger.info(
                f"day spreadsheet wasn't found create new'file_name: {context.name.day_file_name}' exist "
            )
            spreadsheet: Spreadsheet = self.spreadsheet_file_manager.create_spreadsheet(
                spreadsheet_template_id=DAY_TEMPLATE_ID,
                worksheet_name=context.name.day_worksheet_name,
                file_name=context.name.day_file_name,
                year_folder_id=context.year_folder_id,
            )

            self.spreadsheet_file_manager.create_worksheet(
                worksheet_name=context.name.day_worksheet_name,
                templates_spreadsheet_id=DALASHOP_FOLDER_ID,
                spreadsheet=spreadsheet,
            )
            context.day_spreadsheet_id = spreadsheet.id
            return spreadsheet
        spreadsheet: Spreadsheet = self.spreadsheet_file_manager.get_spreadsheet(
            spreadsheet_id=spreadsheet_id
        )
        context.day_spreadsheet_id = spreadsheet_id
        return spreadsheet


class MonthSpreadsheetFileManager:
    def __init__(
        self,
        drive_file_manager: DriveFileManager,
        spreadsheet_file_manager: SpreadSheetFileManager,
    ) -> None:
        self.drive_file_manager: DriveFileManager = drive_file_manager
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manager

    def ensure_month_spreadsheet(
        self,
        context: Context,
    ) -> Spreadsheet:
        if not context.year_folder_id:
            raise ValueError("year folder id not exist check it")

        spreadsheet_id: str | None = self.drive_file_manager.get_spreadsheet_by_name(
            spreadsheet_name=context.name.monthly_report_name,
            parent_folder_id=context.year_folder_id,
            page_size=100,
        )

        if not spreadsheet_id:
            logger.info(
                f"month spreadsheet wasn't found there is an error in month spreadsheet creation logic "
            )
            raise TypeError(
                "cant find month spreadsheet, creating logic could be wrong"
            )

        spreadsheet: Spreadsheet = self.spreadsheet_file_manager.get_spreadsheet(
            spreadsheet_id=spreadsheet_id
        )

        context.month_spreadsheet_id = spreadsheet_id
        return spreadsheet


class WorksheetManager:
    def __init__(self, spreadsheet_file_manager: SpreadSheetFileManager) -> None:
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manager

    def ensure_worksheet(
        self, name: str, spreadsheet: Spreadsheet, template_spreadsheet_id: str
    ) -> Worksheet:
        logger.info(f"check worksheet by name 'worksheet: {name}' exist")
        # check worksheet
        worksheet: Worksheet | None = (
            self.spreadsheet_file_manager.get_worksheet_by_title(
                spreadsheet=spreadsheet, title=name
            )
        )
        if not worksheet:
            logger.info(f"worksheet by name 'worksheet: {name}' not exist!!!")
            # copy sheet sample to spreadsheet
            worksheet = self.spreadsheet_file_manager.create_worksheet(
                worksheet_name=name,
                spreadsheet=spreadsheet,
                templates_spreadsheet_id=template_spreadsheet_id,
            )
            return worksheet
        return worksheet


class ProductManager:
    def __init__(
        self, day_worksheet: Worksheet, context: Context, month_worksheet: Worksheet
    ) -> None:
        self.day_worksheet_manager = DayWorksheetManager(worksheet=day_worksheet)
        self.month_worksheet_manager = MonthlyWorksheetProductManager(
            worksheet=month_worksheet, day=context.name.day
        )

    def ensure_product(self, context: Context) -> None:
        product_exist: bool = self.day_worksheet_manager.product_exist(
            product_name=context.product_data.name
        )

        if not product_exist:
            logger.info(
                f"product by name '{context.product_data.name}' doesn't exist creating new"
            )
            self.day_worksheet_manager.add_new_product(
                product_name=context.product_data.name,
                category=context.product_data.category,
                opening_stock=context.product_update.inventory.before,
                stock_in=context.stock_in_out.stock_in,
                stock_out=context.stock_in_out.stock_out,
            )

            self.month_worksheet_manager.add_new_product(
                product_name=context.product_data.name,
                category=context.product_data.category,
                stock_in=context.stock_in_out.stock_in,
                stock_out=context.stock_in_out.stock_out,
            )


class ProductDataUpdater:
    def update_product_data(
        self,
        day_worksheet_manager: DayWorksheetManager,
        month_worksheet_manager: MonthlyWorksheetProductManager,
        context: Context,
    ):
        logger.info("product by name '{product.name}' was found ")

        day_worksheet_product_position: Cell = day_worksheet_manager.product_position(
            name=context.product_data.name
        )
        day_worksheet_product_row: list[str] = (
            day_worksheet_manager.get_product_row_data(
                row=day_worksheet_product_position.row
            )
        )

        month_worksheet_product_position: Cell = (
            month_worksheet_manager.product_position(name=context.product_data.name)
        )
        monthly_worksheet_product_row: int = month_worksheet_product_position.row

        if context.stock_in_out.stock_in:
            logger.info("update stock in in worksheets")

            day_worksheet_manager.update_stock_in(
                product_data=day_worksheet_product_row,
                amount=context.stock_in_out.stock_out,
                row=day_worksheet_product_position.row,
            )

            month_worksheet_manager.update_stock_in(
                amount=context.stock_in_out.stock_in, row=monthly_worksheet_product_row
            )
        elif context.stock_in_out.stock_out:
            logger.info("update stock out in worksheets")

            day_worksheet_manager.update_stock_out(
                product_data=day_worksheet_product_row,
                amount=context.stock_in_out.stock_out,
                row=day_worksheet_product_position.row,
            )

            month_worksheet_manager.update_stock_out(
                amount=context.stock_in_out.stock_out, row=monthly_worksheet_product_row
            )


class StockInOrOut:
    def __init__(self, product_update: InventoryBalanceChanged) -> None:
        self.stock_in: int = 0
        self.stock_out: int = 0
        self.change: int = 0
        self.before: int = 0

        logger.info("check if product update stock_in or stock out")
        before: int = product_update.inventory.before
        after: int = product_update.inventory.before
        change: int = product_update.inventory.change
        if product_update.inventory.before > product_update.inventory.after:
            logger.info(f" product is 'stock_out' 'before: {before} > after: {after}'")
            self.stock_out: int = change
            self.before: int = before
        else:
            logger.info(f" product is 'stock_in' 'before: {before} < after: {after}'")
            self.stock_in: int = change
            self.before: int = before


class ManagerCreator:
    def __init__(self) -> None:
        _spreadsheet_client = SpreadSheetClient()
        _drive_file_client = GoogleDriveClient()
        self.spreadsheet_manager = SpreadSheetFileManager(client=_spreadsheet_client)
        self.google_drive_manager = DriveFileManager(client=_drive_file_client)
