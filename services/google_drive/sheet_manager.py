from tkinter import NO
from gspread import Cell, utils
from services.google_drive.client import SpreadSheetClient  # type:ignore
from gspread.exceptions import WorksheetNotFound
from gspread.worksheet import Worksheet
from gspread.spreadsheet import Spreadsheet
import logging
from const import (
    WORKSHEET_SAMPLE_COPY_NAME,
    WORKSHEET_SAMPLE_NAME,
    PRODUCT_NAME_INDEX,
    PRODUCT_CATEGORY_INDEX,
    PRODUCT_OPENING_STOCK_INDEX,
    PRODUCT_STOCK_IN_INDEX,
    PRODUCT_STOCK_OUT_INDEX,
    PRODUCT_CLOSING_STOCK_INDEX,
)

from typing import Any, Iterable
import logging

logger: logging.Logger = logging.getLogger(name=__name__)


class SpreadSheetFileManager:
    def __init__(self, client: SpreadSheetClient) -> None:
        self.client: SpreadSheetClient = client
        logger.info("'SpreadSheetFileManager' was created ")

    def copy_spreadsheet(
        self, spreadsheet_id: str, title: str, folder_id: str
    ) -> Spreadsheet:
        return self.client.copy(
            field_id=spreadsheet_id, title=title, folder_id=folder_id
        )

    def copy_sheet_to_spreadsheet(
        self, tamplate_id: str, sheet_id: int, destination_spreadsheet_id: str
    ) -> Any:
        self.client.spreadsheets_sheets_copy_to(
            id=tamplate_id,
            sheet_id=sheet_id,
            destination_spreadsheet_id=destination_spreadsheet_id,
        )

    def worksheet_exist(self, spreadsheet_id: str, sheet_name: str) -> bool | Worksheet:
        try:
            worksheet: Worksheet = self.client.get_worksheet(
                spreadsheet_id=spreadsheet_id, worksheet_title=sheet_name
            )
        except WorksheetNotFound:
            return False
        return worksheet

    def get_spreadsheet(self, spreadsheet_id) -> Spreadsheet:
        return self.client.open_by_key(spreadsheet_id=spreadsheet_id)

    def get_worksheet_by_title(
        self, title: str, spreadsheet: Spreadsheet
    ) -> Worksheet | None:
        name: str = str(object=title)
        try:
            worksheet: Worksheet = spreadsheet.worksheet(title=name)
            return worksheet
        except WorksheetNotFound:
            return None

    def delete_worksheet(self, spreadsheet: Spreadsheet, title: str) -> None:
        worksheet: Worksheet = spreadsheet.worksheet(title=f"{title}")
        spreadsheet.del_worksheet(worksheet)

    def create_worksheet(
        self,
        worksheet_name: str,
        templates_spreadsheet_id: str,
        spreadsheet: Spreadsheet,
    ) -> Worksheet:
        # copy sheet sample to spreadsheet
        self.copy_sheet_to_spreadsheet(
            tamplate_id=templates_spreadsheet_id,
            sheet_id=0,
            destination_spreadsheet_id=spreadsheet.id,
        )
        logger.info(f"copying worksheet from template")
        # rename copied worksheet tamale name
        worksheet: Worksheet = spreadsheet.worksheet(title=WORKSHEET_SAMPLE_COPY_NAME)
        logger.info(
            f"renaming worksheet form '{WORKSHEET_SAMPLE_COPY_NAME} to {worksheet_name}'"
        )

        worksheet.update_title(title=worksheet_name)

        return worksheet

    def create_spreadsheet(
        self,
        file_name: str,
        spreadsheet_template_id: str,
        worksheet_name: str,
        year_folder_id: str,
    ) -> Spreadsheet:
        spreadsheet_copy: Spreadsheet = self.copy_spreadsheet(
            spreadsheet_id=spreadsheet_template_id,
            title=file_name,
            folder_id=year_folder_id,
        )
        logger.info(f"file 'file_name: {file_name}' was not found")
        logger.info(f"creating new file 'file_name: {file_name}'")
        spreadsheet_id = spreadsheet_copy.id

        spreadsheet: Spreadsheet = self.get_spreadsheet(spreadsheet_id=spreadsheet_id)

        logger.info(
            f"rename template names from 'WORKSHEET_SAMPLE_NAME to {worksheet_name}'"
        )
        # rename copied worksheet tamale name
        worksheet = spreadsheet.worksheet(title=WORKSHEET_SAMPLE_NAME)

        worksheet.update_title(title=worksheet_name)
        logger.info(
            f"renaming template names from 'WORKSHEET_SAMPLE_NAME to {worksheet_name}' was successfully done!!!"
        )
        return spreadsheet


class DayWorksheetManager:
    def __init__(
        self,
        worksheet: Worksheet,
    ) -> None:
        self.worksheet: Worksheet = worksheet

    def add_new_product(
        self,
        product_name: str,
        category: str,
        opening_stock: int,
        stock_in: int,
        stock_out: int,
    ) -> Any:
        new_row: list[str | int] = [
            product_name,
            category,
            opening_stock,
            stock_in,
            -abs(stock_out),
        ]

        self.worksheet.append_row(values=new_row)

    def update_stock_in(
        self, product_data: list[str], amount: int, product_positional_data: Cell
    ) -> None:
        old_value: int = int(product_data[PRODUCT_STOCK_IN_INDEX])
        increment_values: int = old_value + amount
        self.worksheet.update_cell(
            row=product_positional_data.row,
            # python list index starting from 0, drive sheet index from 1
            col= PRODUCT_STOCK_IN_INDEX + 1,
            value=increment_values,
        )  # type:ignore

    def update_stock_out(
        self, product_data: list[str], amount: int, product_positional_data: Cell
    ) -> None:
        old_value: int = int(product_data[PRODUCT_STOCK_OUT_INDEX])
        increment_values: int = old_value + amount
        self.worksheet.update_cell(
            row=product_positional_data.row,
            # python list index starting from 0, drive sheet index from 1
            col=PRODUCT_STOCK_OUT_INDEX + 1,
            value=-abs(increment_values),
        )  # type:ignore

    def product_position(self, name) -> Cell | None:
        product: Cell | None = self.worksheet.find(name, in_column=1)

        if not product:
            logger.info(f"product by name 'product_name: {name}' doesn't exist adding new")
            return None

        return product

    def get_product_row_data(self, row: int) -> list[str]:
        return self.worksheet.row_values(row=row)


class MounthlyWorksheetManager:
    def __init__(self, worksheet: Worksheet, day: int) -> None:
        self.worksheet: Worksheet = worksheet
        self.day: int = day

        # first 3 row product name, category etc.
        self.stock_in_col: int = day + 4
        self.stock_out_col: int = day + 4

    def add_new_product(
        self,
        product_name: str,
        category: str | None,
        last_mounth_stock: int,
        stock_in: int,
        stock_out: int,
        last_row: int,
    ) -> Any:
        last_element_row: int = last_row
        new_row: Iterable[Iterable[Any]] = [
            [
                product_name,
                category,
                last_mounth_stock,
            ]
        ]

        # bunch update last element row + 1
        self.worksheet.update(
            range_name=f"A{last_element_row + 1}:C{last_element_row + 1}",
            values=new_row,
        )

        if stock_in:
            self.update_stock_in(row=last_element_row, value=stock_in)
        elif stock_out:
            self.update_stock_out(row=last_element_row, value=-abs(stock_out))

    def update_stock_in(self, value: int, row: int) -> Any:
        # in dataframe object col and row different to get correct row need to + 2
        self.worksheet.update_cell(row=row + 1, col=self.stock_in_col, value=value)

    def update_stock_out(self, value: int, row: int) -> Any:
        # in dataframe object col and row different to get correct row need to + 2
        self.worksheet.update_cell(row=row + 2, col=self.stock_out_col, value=value)

    def get_raw_data(self) -> list[list[str]]:
        return self.worksheet.get(return_type=utils.GridRangeType.ListOfLists)
