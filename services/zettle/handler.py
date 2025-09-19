from services.google_drive.client import SpreadSheetClient, GoogleDriveClient
from services.google_drive.drive_manager import DriveFileManager
from services.google_drive.sheet_manager import SheetFileManager, SheetManager
from services.google_drive.product_dataframe import ProductDataFrame
from services.zettle.validaton import InventoryBalanceChanged, ProductData  # type:ignore
from dotenv import load_dotenv
from pydantic import BaseModel
from services.utils import FileName
import json
from services.utils import check_stock_in_or_out

import os
from dotenv import load_dotenv

load_dotenv()

ROOT_FOLDER = os.getenv("ROOT_FOLDER_ID")
DAY_SAMPLE = os.getenv("DAY_TEMPLATE_SAMPLE_ID")


with open("data/InventoryBalanceChanged.json", "r") as fp:
    INVENTORY_UPDATE = json.load(fp)
with open("data/Product.json", "r") as fp:
    PRODUCT_UPDATE = json.load(fp)

load_dotenv()


class ZettleWebhookHandler:
    def __init__(self) -> None:
        self.drive_client: GoogleDriveClient = GoogleDriveClient()
        self.sheet_client: SpreadSheetClient = SpreadSheetClient()

    def process_webhook(self):
        inventory_update: BaseModel = InventoryBalanceChanged(**INVENTORY_UPDATE)
        product_update: BaseModel = ProductData(**PRODUCT_UPDATE)

        drive_file_manege: DriveFileManager = DriveFileManager(self.drive_client)

        name = FileName(date=inventory_update.timestamp)

        folder: None | dict = self.drive_client.file_exist(
            file_name=name.year, folder_id=ROOT_FOLDER, folder=True
        )

        if not folder:
            drive_file = drive_file_manege.create_year_folder(
                year=name.year,
                parent_folder_id=ROOT_FOLDER,
                sample_file_id=DAY_SAMPLE,
                nested_file_name=name.name,
            )
            drive_file_id = drive_file.get("id")
        else:
            sheet_file_manege = SheetFileManager(client=self.sheet_client)
            sheet_manager = SheetManager(
                client=self.sheet_client,
                spreadsheet_id=drive_file_id,
                worksheet_name=name.month,
            )

            # get row spreadsheet data
            row_sheet_data = sheet_manager.get_row_data()

            # converts pandas DataFrame
            product_dataframe = ProductDataFrame(row_sheet_data)

            if not self.drive_client.file_exist(
                file_name=name.month_name, folder_id=folder.get("id"), folder=False
            ):
                sheet_file_manege.copy_spreadsheet(
                    spreadsheet_id=DAY_SAMPLE,
                    title=name.month_name,
                    folder_id=folder.get("id"),
                )

            else:
                product_data = product_dataframe.get_product_data(
                    product_name=product_update.name
                )

                # check if inventory update is stock in or out
                stock_in_or_out = check_stock_in_or_out(
                    before=inventory_update.inventory.before,
                    after=inventory_update.inventory.after,
                    change=inventory_update.inventory.change,
                )

                stock_in: int = stock_in_or_out["stock_in"]
                stock_out: int = stock_in_or_out["stock_out"]

                if not product_data:
                    last_row: int = product_dataframe.last_row_index()
                    sheet_manager.add_product(
                        product_name=product_update.name,
                        category=product_update.category,
                        opening_stock=inventory_update,
                        stock_in=stock_in,
                        stock_out=stock_out,
                        closing_stock=inventory_update.inventory.change,
                        last_row=last_row,
                    )

                else:
                    product_row = product_dataframe.get_product_row_index(
                        product_update.name
                    )
                    sheet_manager.update_stock_in(value=stock_in, row=product_row)
                    sheet_manager.update_stock_out(value=stock_out, row=product_row)
