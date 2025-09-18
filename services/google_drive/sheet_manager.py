from gspread import utils
from client import SpreadSheetClient

from typing import Any, Iterable


class SheetFileManager:
    def __init__(self, client: SpreadSheetClient) -> None:
        self.client = client

    def copy_spreadsheet(self, spreadsheet_id: str, title: str, folder_id: str):
        return self.client.copy(
            field_id=spreadsheet_id, title=title, folder_id=folder_id
        )

    def rename_worksheet(self, spreadsheet_id: str, title: str, rename: str):
        return self.client.open_by_key(spreadsheet_id, title=title).update_title(rename)

    def copy_sheet_to_spreadsheet(
        self, spreadsheet_id: str, sheet_id: int, destination_spreadsheet_id: str
    ):
        self.client.spreadsheets_sheets_copy_to(
            id=spreadsheet_id,
            sheet_id=sheet_id,
            destination_spreadsheet_id=destination_spreadsheet_id,
        )


class SheetManager:
    def __init__(
        self, spreadsheet_id, worksheet_name: str, client: SpreadSheetClient
    ) -> None:
        self.client = client

        self.spreadsheet = self.client.open_by_key(spreadsheet_id, title=worksheet_name)
        self.raw_data = self.spreadsheet.get(
            return_type=utils.GridRangeType.ListOfLists
        )
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
        self.spreadsheet.update(
            range_name=f"A{last_element}:F{last_element}", values=new_row
        )

    def update_stock_in(self, value: int | float | str, row: int) -> None:
        self.spreadsheet.update_cell(row=row + 2, col=self.stock_in_col, value=value)

    def update_stock_out(self, value: int | float | str, row: int) -> None:
        self.spreadsheet.update_cell(row=row + 2, col=self.stock_out_col, value=value)
