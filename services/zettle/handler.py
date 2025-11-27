import logging

from gspread import Cell
from services.google_drive.client import SpreadSheetClient, GoogleDriveClient
from services.google_drive.drive_manager import DriveFileManager
from services.google_drive.sheet_manager import (
    SpreadSheetFileManager,
    DayWorksheetManager,
    MounthlyWorksheetManager,
)
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from services.zettle.validaton import InventoryBalanceChanged, ProductData
from services.utils import FileName
from services.utils import check_stock_in_or_out
import json
from const import (
    DAY_TEMPLATE_ID,
    WORKSHEET_SAMPLE_NAME,
    MONTHLY_REPORT_TEMPLATE_ID,
    ART_CRAFT_FOLDER_ID,
    DALA_CRAFFE_FOLDER_ID,
    DALASHOP_FOLDER_ID,
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
        self.shop_unique_id_mapping: dict[str, str] = {
            "dala_id": DALASHOP_FOLDER_ID,
            "art_id": ART_CRAFT_FOLDER_ID,
            "cafee_id": DALA_CRAFFE_FOLDER_ID,
        }

    def process_webhook(self, request: InventoryBalanceChanged) -> None:
        product_data = ProductData(**PRODUCT_UPDATE)

        name = FileName(date=request.timestamp)

        if not request.organizationUuid in self.shop_unique_id_mapping:
            raise ValueError("organization uuid doesn't match")

        parent_folder_id: str = self.shop_unique_id_mapping[request.organizationUuid]

        logger.info(f"check if 'year: {name.year}' folder exist")

        year_folder_id: str | None = self.drive_file_manager.folder_exist_by_name(
            folder_name=name.year,
            parent_folder_id=parent_folder_id,
            page_size=100,
        )

        if not year_folder_id:
            logger.info(f"'year: {name.year}' was not found")

            year_folder_id = self.drive_file_manager.create_year_folder(
                year=name.year,
                parent_folder_id=parent_folder_id,
            )
            logger.info(f"new 'year: {name.year}' folder was created!!")

            # create mouthy report spreadsheet
            monthly_report_spreadsheet: Spreadsheet = (
                self.spreadsheet_file_manager.copy_spreadsheet(
                    spreadsheet_id=MONTHLY_REPORT_TEMPLATE_ID,
                    title=name.monthly_report_name,
                    folder_id=year_folder_id,
                )
            )

            logger.info(
                f"monthly_report_spreadsheet, rename template names from 'WORKSHEET_SAMPLE_NAME to {name.file_name}'"
            )

            worksheet = monthly_report_spreadsheet.worksheet(
                title=WORKSHEET_SAMPLE_NAME
            )

            worksheet.update_title(title=name.file_name)

            day_spreadsheet: Spreadsheet = (
                self.spreadsheet_file_manager.copy_spreadsheet(
                    spreadsheet_id=DAY_TEMPLATE_ID,
                    title=name.file_name,
                    folder_id=year_folder_id,
                )
            )

            logger.info(
                f"day spreadsheet was created, renaming template names from 'WORKSHEET_SAMPLE_NAME to {name.day}' was successfully done!!!"
            )

            # rename copied worksheet tamale name
            worksheet = day_spreadsheet.worksheet(title=WORKSHEET_SAMPLE_NAME)
            worksheet.update_title(title=name.day)


        # Check if file exist, if not create it
        logger.info(f"check if file 'file_name: {name.file_name}' exist ")
        day_spreadsheet_id: str | None = (
            self.drive_file_manager.get_spreadsheet_by_name(
                spreadsheet_name=name.file_name,
                parent_folder_id=year_folder_id,
                page_size=100,
            )
        )

        if not day_spreadsheet_id:
            logger.info(f"day spreadsheet wasn't found create new'file_name: {name.file_name}' exist ")
            spreadsheet: Spreadsheet = self.spreadsheet_file_manager.create_spreadsheet(
                spreadsheet_template_id=DAY_TEMPLATE_ID,
                worksheet_name=name.day,
                file_name=name.file_name,
                year_folder_id=year_folder_id,
            )

            worksheet: Worksheet | None = spreadsheet.worksheet(
                title=name.day,
            )

        # create spreadsheet_object
        else:
            logger.info(f"file 'file_name: {name.file_name}' was found!!!")
            spreadsheet: Spreadsheet = self.spreadsheet_file_manager.get_spreadsheet(
                spreadsheet_id=day_spreadsheet_id
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
                worksheet = self.spreadsheet_file_manager.create_worksheet(
                    worksheet_name=name.day,
                    spreadsheet=spreadsheet,
                    templates_spreadsheet_id=DAY_TEMPLATE_ID,
                )
            logger.info(f"check worksheet by name 'worksheet: {name.day}' exist")

        logger.info(
            f"get monthly report spreadsheet_id 'name:{name.monthly_report_name}'"
        )
        monthly_report_spreadsheet_id: str | None = (
            self.drive_file_manager.get_spreadsheet_by_name(
                spreadsheet_name=name.monthly_report_name,
                parent_folder_id=year_folder_id,
                page_size=100,
            )
        )
        logger.info(
            f"create monthly spreadsheet object 'name:{name.monthly_report_name}'"
        )
        monthly_report_spreadsheet = self.spreadsheet_file_manager.get_spreadsheet(
            spreadsheet_id=monthly_report_spreadsheet_id
        )

        # get worksheet of monthly report spreadsheet my month
        logger.info(f"cget monthly worksheet 'name:{name.file_name}'")
        monthly_report_worksheet: Worksheet | None = (
            self.spreadsheet_file_manager.get_worksheet_by_title(
                spreadsheet=monthly_report_spreadsheet, title=name.file_name
            )
        )

        if not monthly_report_worksheet:
            logger.info(
                f"monthly report worksheet by name 'worksheet: {name.file_name}' not exist!!!"
            )
            # copy sheet sample to spreadsheet
            monthly_report_worksheet = self.spreadsheet_file_manager.create_worksheet(
                worksheet_name=name.file_name,
                spreadsheet=spreadsheet,
                templates_spreadsheet_id=MONTHLY_REPORT_TEMPLATE_ID,
            )

        day_worksheet_manager = DayWorksheetManager(worksheet=worksheet)

        # check if product exist
        product_position: Cell | None = day_worksheet_manager.product_position(
            product_data.name
        )

        stock_in_and_out: dict[str, int] = check_stock_in_or_out(
            before=request.inventory.before,
            after=request.inventory.after,
            change=request.inventory.change,
        )

        if not product_position:
            logger.info(f"product by name '{product_data.name}' doesn't exist creating new")
            day_worksheet_manager.add_new_product(
                product_name=product_data.name,
                category=product_data.category,
                opening_stock=request.inventory.before,
                stock_in=stock_in_and_out["stock_in"],
                stock_out=stock_in_and_out["stock_out"],
            )

        else:
            logger.info("product by name '{product.name}' was found ")
            product_row_data: list[str] = day_worksheet_manager.get_product_row_data(
                row=product_position.row
            )

            if stock_in_and_out["stock_in"]:
                logger.info("update stock in in worksheet")
                print(product_row_data)
                day_worksheet_manager.update_stock_in(
                    product_data=product_row_data,
                    product_positional_data=product_position,
                    amount=stock_in_and_out["stock_in"],
                )
            elif stock_in_and_out["stock_out"]:
                logger.info("update stock out in worksheet")

                day_worksheet_manager.update_stock_out(
                    product_data=product_row_data,
                    product_positional_data=product_position,
                    amount=stock_in_and_out["stock_out"],
                )
