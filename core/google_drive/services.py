from os import name
from gspread import Spreadsheet, Worksheet
from core.context import Context
from core.google_drive.drive_manager import GoogleDriveFileManager
from const import (
    DAY_TEMPLATE_ID,
    WORKSHEET_SAMPLE_NAME,
    MONTHLY_TEMPLATE_ID,
    DALASHOP_FOLDER_ID,
    SHOP_ID,
)
import logging

from core.google_drive.product_managers import (
    DayWorksheetProductReader,
    DayWorksheetProductWriter,
    MonthWorksheetProductReader,
    MonthWorksheetProductWriter,
)

from core.google_drive.sheet_manager import SpreadSheetFileManager

logger: logging.Logger = logging.getLogger(name=__name__)


class YearFolderExistenceEnsurer:
    def __init__(
        self,
        drive_file_manager: GoogleDriveFileManager,
        spreadsheet_file_manege: SpreadSheetFileManager,
    ) -> None:
        self.drive_file_manager: GoogleDriveFileManager = drive_file_manager
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manege

    def ensure_year_folder(self, context: Context) -> None:
        logger.info(msg=f"check if 'year: {context.name.year}' folder exist")
        parent_folder_id: str | None = SHOP_ID[str(context.product_update.organizationUuid)]

        year_folder_id: str | None = self.drive_file_manager.folder_exist_by_name(
            folder_name=context.name.year_folder_name,
            parent_folder_id=parent_folder_id,
            page_size=100,
        )

        if not year_folder_id:
            logger.info(msg=f"'year: {context.name.year}' was not found")

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


class DaySpreadsheetExistenceEnsurer:
    def __init__(
        self,
        drive_file_manager: GoogleDriveFileManager,
        spreadsheet_file_manager: SpreadSheetFileManager,
    ) -> None:
        self.drive_file_manager: GoogleDriveFileManager = drive_file_manager
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manager

    def ensure_day_spreadsheet(self, context: Context) -> Spreadsheet:
        if not context.year_folder_id:
            raise ValueError("year folder id not exist")

        spreadsheet_id: str | None = self.drive_file_manager.get_spreadsheet_id_by_name(
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


class MonthSpreadsheetExistenceEnsurer:
    def __init__(
        self,
        drive_file_manager: GoogleDriveFileManager,
        spreadsheet_file_manager: SpreadSheetFileManager,
    ) -> None:
        self.drive_file_manager: GoogleDriveFileManager = drive_file_manager
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manager

    def ensure_month_spreadsheet(
        self,
        context: Context,
    ) -> Spreadsheet:
        if not context.year_folder_id:
            raise ValueError("year folder id not exist check YearFolderEnsurer")

        spreadsheet_id: str | None = self.drive_file_manager.get_spreadsheet_id_by_name(
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


class WorksheetExistenceEnsurer:
    def __init__(self, spreadsheet_file_manager: SpreadSheetFileManager) -> None:
        self.spreadsheet_file_manager: SpreadSheetFileManager = spreadsheet_file_manager

    def ensure_worksheet(
        self, name: str, spreadsheet: Spreadsheet, template_spreadsheet_id: str
    ) -> Worksheet:
        logger.info(msg=f"check worksheet by name 'worksheet: {name}' exist")

        worksheet: Worksheet | None = (
            self.spreadsheet_file_manager.get_worksheet_by_title(
                spreadsheet=spreadsheet, title=name
            )
        )
        if not worksheet:
            logger.info(msg=f"worksheet by name 'worksheet: {name}' not exist!!!")
            # copy sheet sample to spreadsheet
            worksheet = self.spreadsheet_file_manager.create_worksheet(
                worksheet_name=name,
                spreadsheet=spreadsheet,
                templates_spreadsheet_id=template_spreadsheet_id,
            )
            return worksheet
        return worksheet


class DayProductExistenceEnsurer:
    def __init__(
        self,
        day_worksheet: Worksheet,
    ) -> None:
        self.day_worksheet_reader = DayWorksheetProductReader(worksheet=day_worksheet)
        self.day_worksheet_writer = DayWorksheetProductWriter(worksheet=day_worksheet)

    def ensure_day_product(self, context: Context) -> None:
        product_exist: int | None = self.day_worksheet_reader.product_exist(
            product_name=context.product_data.name
        )
        if not product_exist:
            logger.info(
                msg=f"product by name '{context.product_data.name}' doesn't exist creating new"
            )
            self.day_worksheet_writer.add_new_product(context=context)
            return None


class MonthProductExistenceEnsurer:
    def __init__(self, month_worksheet: Worksheet) -> None:
        self.month_worksheet_reader: MonthWorksheetProductReader = (
            MonthWorksheetProductReader(worksheet=month_worksheet)
        )
        self.month_worksheet_writer = MonthWorksheetProductWriter(
            worksheet=month_worksheet
        )

    def ensure_month_product(self, context: Context) -> int | None:
        product_exist: int | None = self.month_worksheet_reader.product_exist(
            product_name=context.product_data.name
        )
        if not product_exist:
            logger.info(
                f"product by name '{context.product_data.name}' doesn't exist creating new"
            )
            self.month_worksheet_writer.add_new_product(context=context)
            return


class DayWorksheetValueUpdater:
    @staticmethod
    def update_day_worksheet(
        context: Context,
        day_worksheet_writer: DayWorksheetProductWriter,
        day_worksheet_reader: DayWorksheetProductReader,
    ) -> None:
        logger.info(msg=f"product by name '{context.product_data.name}' was found ")

        if context.stock_in_out.stock_in:
            logger.info(msg="update stock in in worksheets")
            product_row: int = day_worksheet_reader.get_product_row_by_name(
                product_name=context.product_data.name
            )
            old_stock_in: int = day_worksheet_reader.get_product_stock_in(
                product_row=product_row
            )
            day_worksheet_writer.update_stock_in(
                old_stock_in=old_stock_in,
                amount=context.stock_in_out.stock_in,
                row=product_row,
            )

        elif context.stock_in_out.stock_out:
            logger.info(msg="update stock in in worksheets")
            product_row: int = day_worksheet_reader.get_product_row_by_name(
                product_name=context.product_data.name
            )
            old_stock_out: int = day_worksheet_reader.get_product_stock_out(
                product_row=product_row
            )
            day_worksheet_writer.update_stock_out(
                old_stock_out=old_stock_out,
                amount=context.stock_in_out.stock_out,
                row=product_row,
            )


class MonthWorksheetValueUpdater:
    @staticmethod
    def update_month_worksheet(
        context: Context,
        month_worksheet_writer: MonthWorksheetProductWriter,
        month_worksheet_reader: MonthWorksheetProductReader,
    ) -> None:
        logger.info(msg=f"product by name '{context.product_data.name}' was found ")

        if context.stock_in_out.stock_in:
            logger.info(msg="update stock in in worksheets")

            product_row: int = month_worksheet_reader.get_product_row_by_name(
                product_name=context.product_data.name
            )
            old_stock_in: int = month_worksheet_reader.get_product_stock_in(
                product_row=product_row,
                stock_in_col=context.name.month_stock_in_and_out_col_index,
            )

            month_worksheet_writer.update_stock_in(
                old_stock_in=old_stock_in,
                amount=context.stock_in_out.stock_in,
                row=product_row,
                col=context.name.month_stock_in_and_out_col_index,
            )

        elif context.stock_in_out.stock_out:
            logger.info(msg="update stock in in worksheets")
            stock_out_row: int = month_worksheet_reader.get_product_stock_out_row(
                product_name=context.product_data.name
            )
            old_stock_out: int = month_worksheet_reader.get_product_stock_out(
                product_row=stock_out_row,
                stock_out_col=context.name.month_stock_in_and_out_col_index,
            )
            month_worksheet_writer.update_stock_out(
                old_stock_out=old_stock_out,
                amount=context.stock_in_out.stock_out,
                row=stock_out_row,
                col=context.name.month_stock_in_and_out_col_index,
            )
