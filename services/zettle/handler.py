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
from constants import (
    ROOT_FOLDER_ID,
    DAY_TEMPLATE,
    WORKSHEET_SAMPLE_NAME,
    WORKSHEET_SAMPLE_COPY_NAME,
    MONTHLY_REPORT_TEMPLATE_ID,
    MONTHLY_REPORT_TEMPLATE,
)

import logging

logger: logging.Logger = logging.getLogger(name=__name__)


with open("data/Product.json", "r") as fp:
    PRODUCT_UPDATE = json.load(fp)


class ZettleWebhookHandler:
    def __init__(self) -> None:
        self.drive_client: GoogleDriveClient = GoogleDriveClient()
        self.spreadsheet_client: SpreadSheetClient = SpreadSheetClient()
        self.drive_file_manager = DriveFileManager(client=self.drive_client)
        self.spreadsheet_file_manager = SpreadSheetFileManager(
            client=self.spreadsheet_client
        )

    def process_webhook(self, request: InventoryBalanceChanged) -> None:
        # validating webhook data

        product_data = ProductData(**PRODUCT_UPDATE)

        # crete file name by date
        name = FileName(date=request.timestamp)

        logger.info(f"check if 'year: {name.year}' folder exist")
        # check if year folder exist if not create it
        year_folder_id: str | None = self.drive_file_manager.folder_exist_by_name(
            folder_name=name.year,
            parent_folder_id=ROOT_FOLDER_ID,
            page_size=100,
        )

        if not year_folder_id:
            logger.info(f"'year: {name.year}' was not found")
            logger.info(f"creating 'year: {name.year}' folder")
            year_folder_id = self.drive_file_manager.create_year_folder(
                year=name.year,
                parent_folder_id=ROOT_FOLDER_ID,
            )
            logger.info(f"'year: {name.year}' folder was created!!")

            # create mouthy report spreadsheet
            monthly_report_spreadsheet: Spreadsheet = (
                self.spreadsheet_file_manager.copy_spreadsheet(
                    spreadsheet_id=MONTHLY_REPORT_TEMPLATE_ID,
                    title=f"{name.monthly_report_name}",
                    folder_id=year_folder_id,
                )
            )

            monthly_report_spreadsheet: Spreadsheet = monthly_report_spreadsheet
            
            logger.info(
                f"rename template names from 'WORKSHEET_SAMPLE_NAME to {name.day}'"
            )
            # rename copied worksheet tamale name
            worksheet = monthly_report_spreadsheet.worksheet(title=WORKSHEET_SAMPLE_NAME)

            worksheet.update_title(title=name.month)
            logger.info(
                f"renaming template names from 'WORKSHEET_SAMPLE_NAME to {name.day}' was successfully done!!!"
            )
            

        # Check if file exist, if not create it
        logger.info(f"check if file 'file_name: {name.file_name}' exist ")
        spreadsheet_id: str | None = self.drive_file_manager.spreadsheet_exist_by_name(
            spreadsheet_name=name.file_name,
            parent_folder_id=year_folder_id,
            page_size=100,
        )

        if not spreadsheet_id:
            spreadsheet_copy: Spreadsheet = (
                self.spreadsheet_file_manager.copy_spreadsheet(
                    spreadsheet_id=DAY_TEMPLATE,
                    title=name.file_name,
                    folder_id=year_folder_id,
                )
            )
            logger.info(f"file 'file_name: {name.file_name}' was not found")
            logger.info(f"creating new file 'file_name: {name.file_name}'")
            spreadsheet_id = spreadsheet_copy.id

            spreadsheet: Spreadsheet = self.spreadsheet_file_manager.get_spreadsheet(
                spreadsheet_id=spreadsheet_id
            )

            logger.info(
                f"rename template names from 'WORKSHEET_SAMPLE_NAME to {name.day}'"
            )
            # rename copied worksheet tamale name
            worksheet = spreadsheet.worksheet(title=WORKSHEET_SAMPLE_NAME)

            worksheet.update_title(title=name.day)
            logger.info(
                f"renaming template names from 'WORKSHEET_SAMPLE_NAME to {name.day}' was successfully done!!!"
            )

        # create spreadsheet_object
        else:
            logger.info(f"file 'file_name: {name.file_name}' was found!!!")
            spreadsheet: Spreadsheet = self.spreadsheet_file_manager.get_spreadsheet(
                spreadsheet_id=spreadsheet_id
            )

            logger.info(f"check worksheet by name 'worksheet: {name.day}' exist")
            # check if worksheet not exist create it
            worksheet: Worksheet | None = (
                self.spreadsheet_file_manager.get_worksheet_by_title(
                    spreadsheet=spreadsheet, title=name.day
                )
            )
            if not worksheet:
                logger.info(f"worksheet by name 'worksheet: {name.day}' not exist!!!")
                # copy sheet sample to spreadsheet
                self.spreadsheet_file_manager.copy_sheet_to_spreadsheet(
                    spreadsheet_id=DAY_TEMPLATE,
                    sheet_id=0,
                    destination_spreadsheet_id=spreadsheet.id,
                )
                logger.info(f"copying worksheet from template")
                # rename copied worksheet tamale name
                worksheet = spreadsheet.worksheet(title=WORKSHEET_SAMPLE_COPY_NAME)
                logger.info(
                    f"renaming worksheet form '{WORKSHEET_SAMPLE_COPY_NAME} to {name.day}'"
                )

                worksheet.update_title(title=name.day)

        monthly_report_spreadsheet_id: str | None = (
            self.drive_file_manager.spreadsheet_exist_by_name(
                spreadsheet_name=name.monthly_report_name,
                parent_folder_id=year_folder_id,
                page_size=100,
            )
        )

        # create monthly report spreadsheet
        monthly_report_spreadsheet = self.spreadsheet_file_manager.get_spreadsheet(
            spreadsheet_id=monthly_report_spreadsheet_id
        )

        # get worksheet of monthly report spreadsheet my month
        monthly_report_worksheet: Worksheet | None = (
            self.spreadsheet_file_manager.get_worksheet_by_title(
                spreadsheet=monthly_report_spreadsheet, title=name.monthly_report_name
            )
        )

        if not monthly_report_worksheet:
            logger.info(f"monthly report worksheet by name 'worksheet: {name.day}' not exist!!!")
            # copy sheet sample to spreadsheet
            self.spreadsheet_file_manager.copy_sheet_to_spreadsheet(
                spreadsheet_id=MONTHLY_REPORT_TEMPLATE_ID,
                sheet_id=0,
                destination_spreadsheet_id=monthly_report_spreadsheet.id,
            )
            logger.info(f"copying monthly report worksheet from template")
            # rename copied worksheet tamale name
            monthly_report_worksheet = spreadsheet.worksheet(title=WORKSHEET_SAMPLE_COPY_NAME)
            logger.info(
                f"renaming monthly report worksheet form '{MONTHLY_REPORT_TEMPLATE} to {name.day}'"
            )

            worksheet.update_title(title=name.month)

        # create worksheet manager
        worksheet_manager = WorksheetManager(worksheet=worksheet)
        monthly_worksheet_manager = WorksheetManager(worksheet=monthly_report_worksheet)

        # get raw data of worksheet for pandas
        logger.info(f"get worksheet raw data nested lists")
        worksheet_raw_data: list = worksheet_manager.get_raw_data()

        # get raw data of worksheet for pandas
        logger.info(f"get monthly report worksheet raw data nested lists")
        worksheet_raw_data: list = monthly_worksheet_manager.get_raw_data()
        
        # convert sheet to pandas DataFrame
        dataframe: ProductDataFrame = ProductDataFrame(sheet=worksheet_raw_data)
        monthly_report_dataframe: ProductDataFrame = ProductDataFrame(
            sheet=worksheet_raw_data
        )

        product_exist: bool = dataframe.product_exist(product_name=product_data.name)

        stock_in_or_out: dict[str, int] = check_stock_in_or_out(
            before=request.inventory.before,
            after=request.inventory.after,
            change=request.inventory.change,
        )

        if not product_exist:
            last_row: int = dataframe.last_row_index()
            logger.info("product doesn't exist creating product in dataframe ")
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
                logger.info("increment stock in in dataframe")
                increment_in: dict = dataframe.increment_stock_in(
                    product_name=product_data.name, amount=stock_in_or_out["stock_in"]
                )

                logger.info("update stock in in worksheet")
                # update_worksheet
                worksheet_manager.update_stock_in(
                    value=increment_in["value"], row=increment_in["row"]
                )
            if stock_in_or_out["stock_in"] == 0:
                # increment it in dataframe
                logger.info("increment stock out in dataframe")
                increment_out: dict = dataframe.increment_stock_out(
                    product_name=product_data.name, amount=stock_in_or_out["stock_out"]
                )

                # update_worksheet
                logger.info("update stock out in worksheet")
                worksheet_manager.update_stock_out(
                    value=increment_out["value"], row=increment_out["row"]
                )
