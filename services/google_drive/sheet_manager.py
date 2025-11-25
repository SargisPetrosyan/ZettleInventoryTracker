from gspread import utils
import data
from services.google_drive.client import SpreadSheetClient  # type:ignore
from gspread.exceptions import WorksheetNotFound
from gspread.worksheet import Worksheet
from gspread.spreadsheet import Spreadsheet
import logging
from services.utils import FileName
from const import (
    WORKSHEET_SAMPLE_NAME,
    WORKSHEET_SAMPLE_COPY_NAME
)

logger: logging.Logger = logging.getLogger(name=__name__)

from typing import Any, Iterable


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
            tamplates_spreadsheet_id:str,
            spreadsheet:Spreadsheet
            ) -> Worksheet:
        # copy sheet sample to spreadsheet
        self.copy_sheet_to_spreadsheet(
            tamplate_id=tamplates_spreadsheet_id,
            sheet_id=0,
            destination_spreadsheet_id=spreadsheet.id
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
            file_name:str,
            spreadsheet_tamplate_id:str,
            worksheet_name:str,
            year_folder_id: str
            ) -> Spreadsheet:
        
        spreadsheet_copy: Spreadsheet = (
            self.copy_spreadsheet(
                spreadsheet_id=spreadsheet_tamplate_id,
                title=file_name,
                folder_id=year_folder_id
            )
        )
        logger.info(f"file 'file_name: {file_name}' was not found")
        logger.info(f"creating new file 'file_name: {file_name}'")
        spreadsheet_id = spreadsheet_copy.id

        spreadsheet: Spreadsheet = self.get_spreadsheet(
            spreadsheet_id=spreadsheet_id
        )

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
        self.name_col: int = 1
        self.category_col: int = 2
        self.opening_stock_col: int = 3
        self.stock_in_col: int = 4
        self.stock_out_col: int = 5
        self.closing_stock_col: int = 6

    def add_product(
        self,
        product_name: str,
        category: str | None,
        opening_stock: int,
        stock_in: int,
        stock_out: int,
        last_row: int,
    ) -> Any:
        last_element: int = last_row + 1
        new_row: Iterable[Iterable[Any]] = [
            [product_name, category, opening_stock, stock_in, stock_out]
        ]
        self.worksheet.update(
            range_name=f"A{last_element}:F{last_element}", values=new_row
        )

    def update_stock_in(self, value: int | float | str, row: int) -> Any:
        self.worksheet.update_cell(row=row + 2, col=self.stock_in_col, value=value)

    def update_stock_out(self, value: int | float | str, row: int) -> Any:
        self.worksheet.update_cell(row=row + 2, col=self.stock_out_col, value=value)

    def get_raw_data(self) -> list[list[str]]:
        return self.worksheet.get(return_type=utils.GridRangeType.ListOfLists)


class MounthlyWorksheetManager:
    def __init__(
        self,
        worksheet: Worksheet,
        day:int
    ) -> None:
        self.worksheet: Worksheet = worksheet
        self.day: int = day
        self.stock_in_col: int = day
        self.stock_out_col: int = day+2

    def add_product(
        self,
        product_name: str,
        category: str | None,
        opening_stock: int,
        stock_in: int,
        stock_out: int,
        last_row: int,
    ) -> Any:
        last_element: int = last_row + 1
        new_row: Iterable[Iterable[Any]] = [
            [product_name, category, opening_stock, str(self.stock_in_col), str(self.stock_out_col)]
        ]
        self.worksheet.update(
            range_name=f"A{last_element}:AI{last_element}", values=new_row
        )

    def update_stock_in(self, value: int , row: int) -> Any:
        self.worksheet.update_cell(row=row + 2, col=self.stock_in_col, value=value)

    def update_stock_out(self, value: int , row: int) -> Any:
        self.worksheet.update_cell(row=row + 3, col=self.stock_out_col, value=value)

    def get_raw_data(self) -> list[list[str]]:
        return self.worksheet.get(return_type=utils.GridRangeType.ListOfLists)
