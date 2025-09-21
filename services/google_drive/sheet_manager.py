from gspread import utils
from services.google_drive.client import SpreadSheetClient  # type:ignore
from gspread.exceptions import WorksheetNotFound
from gspread.worksheet import Worksheet
from gspread.spreadsheet import Spreadsheet

from typing import Any, Iterable


class SpreadSheetFileManager:
    def __init__(self, client: SpreadSheetClient) -> None:
        self.client = client

    def copy_spreadsheet(self, spreadsheet_id: str, title: str, folder_id: str) -> str:
        return self.client.copy(
            field_id=spreadsheet_id, title=title, folder_id=folder_id
        ).id

    def rename_worksheet(self, spreadsheet_id: str, title: str, rename: str) -> Any:
        return self.client.get_worksheet(
            spreadsheet_id, worksheet_title=title
        ).update_title(rename)

    def copy_sheet_to_spreadsheet(
        self, spreadsheet_id: str, sheet_id: int, destination_spreadsheet_id: str
    ) -> None:
        self.client.spreadsheets_sheets_copy_to(
            id=spreadsheet_id,
            sheet_id=sheet_id,
            destination_spreadsheet_id=destination_spreadsheet_id,
        )

    def worksheet_exist(self, spreadsheet_id: str, sheet_name: str) -> bool | int:
        try:
            worksheet = self.client.get_worksheet(
                spreadsheet_id=spreadsheet_id, worksheet_title=sheet_name
            )
        except WorksheetNotFound:
            return False
        return worksheet.id

    def get_spreadsheet(self, spreadsheet_id) -> Spreadsheet:
        return self.client.open_by_key(spreadsheet_id=spreadsheet_id)

    def get_worksheets_with_ids(self, spreadsheet_id: str) -> dict:
        worksheet_list = self.client.open_by_key(
            spreadsheet_id=spreadsheet_id
        ).worksheets()

        worksheets_info: dict[str, int] = {wl.title: wl.index for wl in worksheet_list}
        return worksheets_info


class SpreadSheetManager:
    def __init__(
        self,
        client: SpreadSheetClient,
        worksheet: Worksheet,
    ) -> None:
        self.client = client

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
        category: str,
        opening_stock: int,
        stock_in: int,
        stock_out: int,
        closing_stock: int,
        last_row: int,
    ) -> None:
        last_element: int = last_row + 1
        new_row: Iterable[Iterable[Any]] = [
            [product_name, category, opening_stock, stock_in, stock_out, closing_stock]
        ]
        self.worksheet.update(
            range_name=f"A{last_element}:F{last_element}", values=new_row
        )

    def update_stock_in(self, value: int | float | str, row: int) -> None:
        self.worksheet.update_cell(row=row + 2, col=self.stock_in_col, value=value)

    def update_stock_out(self, value: int | float | str, row: int) -> None:
        self.worksheet.update_cell(row=row + 2, col=self.stock_out_col, value=value)

    def get_row_data(self) -> list[list[str]]:
        return self.worksheet.get(return_type=utils.GridRangeType.ListOfLists)
