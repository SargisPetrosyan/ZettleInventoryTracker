from calendar import month
from os import name
from typing import Any, List
from gspread import Spreadsheet, ValueRange, Worksheet
from h11 import Data
from pandas import DataFrame
from app.google_drive.context import Context
from app.google_drive.dataframe_manager import DayProductDataFrameManager, MonthProductDataFrameManager
from app.google_drive.drive_manager import GoogleDriveFileManager
from app.constants import (
    DAY_TEMPLATE_ID,
    WORKSHEET_SAMPLE_NAME,
    MONTHLY_TEMPLATE_ID,
    DALASHOP_FOLDER_ID,
)
import logging


from app.google_drive.sheet_manager import SpreadSheetFileManager
from app.models.product import PaypalProductData
from app.utils import dataframe_formatter, get_folder_id_by_shop_id

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
        parent_folder_id: str | None = get_folder_id_by_shop_id(context.product.organization_id)
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
                    title=context.name.monthly_report_file_name,
                    folder_id=year_folder_id,
                )
            )

            logger.info(
                f"monthly_report_spreadsheet, rename template names from 'WORKSHEET_SAMPLE_NAME to {context.name.monthly_report_file_name}'"
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
            spreadsheet_name=context.name.monthly_report_file_name,
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


class DayProductDataEnsurer:
    def __init__(
            self,
            day_worksheet:Worksheet,
            product_data:PaypalProductData
            )  -> None:
        
        self.worksheet: Worksheet = day_worksheet
        self.product_data: PaypalProductData = product_data

    def ensure_day_product(self) -> DayProductDataFrameManager:
        worksheet_row_data:List[List[Any]] = self.worksheet.get_all_values()
        day_worksheet_formatted: DataFrame = dataframe_formatter(row_data=worksheet_row_data)
        day_product_dataframe = DayProductDataFrameManager(day_dataframe=day_worksheet_formatted)
        product_exist: bool = day_product_dataframe.product_exist(product_variant_id=self.product_data.product_variant_uuid)

        if not product_exist:
            day_product_dataframe.add_new_product(product=self.product_data)
            return day_product_dataframe
        
        return day_product_dataframe
    

class MonthProductDataEnsurer:
    def __init__(
            self,
            month_worksheet:Worksheet,
            product_data:PaypalProductData
            )  -> None:
        
        self.worksheet: Worksheet = month_worksheet
        self.product_data: PaypalProductData = product_data

    def ensure_month_product(self) -> MonthProductDataFrameManager:
        worksheet_row_data:List[List[Any]] = self.worksheet.get_all_values()
        month_worksheet_formatted = dataframe_formatter(row_data=worksheet_row_data)
        month_product_dataframe = MonthProductDataFrameManager(month_dataframe=month_worksheet_formatted)
        product_exist: bool = month_product_dataframe.product_exist(product_variant_id=self.product_data.product_variant_uuid)

        if not product_exist:
            month_product_dataframe.add_new_product(product=self.product_data)
            return month_product_dataframe
        
        return month_product_dataframe
    
class DayDataframeUpdater:
    def __init__(
            self,
            product_data:PaypalProductData,
            day_product_dataframe: DayProductDataFrameManager
            ) -> None:
        self.product_data: PaypalProductData = product_data
        self.day_product_dataframe: DayProductDataFrameManager =day_product_dataframe
    
    def update_dataframe(self):
        if self.product_data.after - self.product_data.before > 0:
            self.day_product_dataframe.increment_stock_in(
                product_variant_id=self.product_data.product_variant_uuid,
                amount=self.product_data.after - self.product_data.before)
        
        elif self.product_data.after - self.product_data.after < 0:
            self.day_product_dataframe.increment_stock_out(
                product_variant_id=self.product_data.product_variant_uuid,
                amount=self.product_data.after - self.product_data.before)


class MonthDataFrameUpdater:
    def __init__(
            self,
            product_data:PaypalProductData,
            month_product_dataframe: MonthProductDataFrameManager,
            ) -> None:
        self.product_data: PaypalProductData = product_data
        self.month_product_dataframe: MonthProductDataFrameManager =month_product_dataframe
    
    def update_dataframe(self,context:Context):
        if self.product_data.after - self.product_data.before > 0:
            self.month_product_dataframe.increment_stock_in(
                day=int(context.name.day),
                product_variant_id=self.product_data.product_variant_uuid,
                amount=self.product_data.after - self.product_data.before)
        
        elif self.product_data.after - self.product_data.after < 0:
            self.month_product_dataframe.increment_stock_out(
                day=int(context.name.day),
                product_variant_id=self.product_data.product_variant_uuid,
                amount=self.product_data.after - self.product_data.before)


        






    