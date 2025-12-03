from typing import List
from gspread.worksheet import JSONResponse
from gspread import Cell, ValueRange, Worksheet

from const import (
    PRODUCT_STOCK_IN_COL_INDEX,
    PRODUCT_STOCK_OUT_COL_INDEX,
    MONTH_WORKSHEET_FIRST_CELL,
    MONTH_PRODUCT_DATA_CELL_RANGE,
)
from source.context import Context
from source.context import Context
from source.abstract_classes import WorksheetProductReader, WorksheetProductWriter
import logging

from source.utils import get_row_from_response

logger: logging.Logger = logging.getLogger(name=__name__)


class DayWorksheetProductReader(WorksheetProductReader):
    def __init__(
        self,
        worksheet: Worksheet,
    ) -> None:
        self.worksheet: Worksheet = worksheet
        self.stock_in_col: int = PRODUCT_STOCK_IN_COL_INDEX
        self.stock_out_index: int = PRODUCT_STOCK_OUT_COL_INDEX

    def get_product_row_position(self, product_name: str) -> int | None:
        product: Cell | None = self.worksheet.find(query=product_name, in_column=1)

        if not product:
            return None
        return product.row

    def get_product_stock_in(self, product_row: int) -> int:
        stock_in: Cell = self.worksheet.cell(row=product_row, col=self.stock_in_col)

        if not stock_in.value:
            return 0
        return int(stock_in.value)

    def get_product_stock_out(self, product_row: int) -> int:
        stock_out: Cell = self.worksheet.cell(row=product_row, col=self.stock_in_col)

        if not stock_out.value:
            return 0

        return int(stock_out.value)


class DayWorksheetProductWriter(WorksheetProductWriter):
    def __init__(self, worksheet: Worksheet) -> None:
        self.worksheet: Worksheet = worksheet
        self._row: int | None = None

    def add_new_product(self, context: Context):
        new_row: list[str | int] = [
            context.product_data.name,
            context.product_data.category,
        ]
        response: JSONResponse = self.worksheet.append_row(values=new_row)
        row: int = get_row_from_response(response=response)
        self._row = row
        return

    def update_stock_in(
        self,
        old_stock_in: int,
        amount: int,
    ) -> None:
        increment_values: int = old_stock_in + amount
        logger.info(f"update day report stock_out by value'{increment_values}'")
        self.worksheet.update_cell(
            row=self.row, value=increment_values, col=PRODUCT_STOCK_IN_COL_INDEX
        )

    def update_stock_out(self, old_stock_out: int, amount: int) -> None:
        old_value: int = old_stock_out
        increment_values: int = old_value + amount
        logger.info(f"update day report stock_out by value'{increment_values}'")
        self.worksheet.update_cell(
            row=self.row,
            col=PRODUCT_STOCK_OUT_COL_INDEX,
            value=-abs(increment_values),
        )

    @property
    def row(self) -> int:
        if not self._row:
            raise ValueError("row parameter can't be NONE")
        return self._row


class MonthWorksheetProductReader(WorksheetProductReader):
    def __init__(
        self,
        worksheet: Worksheet,
    ) -> None:
        self.worksheet: Worksheet = worksheet
        self.stock_in_col: int = PRODUCT_STOCK_IN_COL_INDEX
        self.stock_out_col: int = PRODUCT_STOCK_OUT_COL_INDEX

    def get_product_row_position(self, product_name: str) -> int | None:
        product: Cell | None = self.worksheet.find(query=product_name, in_column=1)

        if not product:
            return None
        return product.row

    def get_product_stock_in(self, product_row: int) -> int:
        stock_in: Cell = self.worksheet.cell(row=product_row, col=self.stock_in_col)

        if not stock_in.value:
            return 0
        return int(stock_in.value)

    def get_product_stock_out(self, product_row: int) -> int:
        stock_out: Cell = self.worksheet.cell(row=product_row, col=self.stock_in_col)

        if not stock_out.value:
            return 0

        return int(stock_out.value)


class MonthWorksheetProductWriter(WorksheetProductWriter):
    def __init__(self, worksheet: Worksheet) -> None:
        self.worksheet: Worksheet = worksheet
        self._row: int | None = None
        self._col: int | None = None

    def add_new_product(self, context: Context) -> int:
        first_element: ValueRange | List[List[str]] = self.worksheet.get(
            range_name=MONTH_WORKSHEET_FIRST_CELL
        )
        if not first_element[0]:
            response: JSONResponse = self.worksheet.append_row(
                values=[
                    context.product_data.name,
                    context.product_data.category,
                    context.product_update.inventory.before,
                ],
                table_range=MONTH_PRODUCT_DATA_CELL_RANGE,
            )
        else:
            response: JSONResponse = self.worksheet.append_row(
                values=[
                    context.product_data.name,
                    context.product_data.category,
                    context.product_update.inventory.before,
                ]
            )

        row: int = get_row_from_response(response=response)
        self._row = row
        self._col = int(context.name.day)
        return row

    def update_stock_in(
        self,
        old_stock_in: int,
        amount: int,
    ) -> None:
        increment_values: int = old_stock_in + amount
        logger.info(f"update day report stock_out by value'{increment_values}'")
        self.worksheet.update_cell(row=self.row, value=increment_values, col=self.col)

    def update_stock_out(self, old_stock_out: int, amount: int) -> None:
        old_value: int = old_stock_out
        increment_values: int = old_value + amount
        logger.info(f"update day report stock_out by value'{increment_values}'")
        self.worksheet.update_cell(
            row=self.row,
            col=self.col,
            value=-abs(increment_values),
        )

    @property
    def row(self) -> int:
        if not self._row:
            raise TypeError("row parameter can't be NONE")
        return self._row

    @property
    def col(self) -> int:
        if not self._col:
            raise TypeError("col parameter can't be NONE")
        return self._col


# class MonthlyWorksheetProductReader(WorksheetProductReader):
#     def __init__(self, worksheet: Worksheet, col_index: str) -> None:
#         self.worksheet: Worksheet = worksheet

#         # first 4 col are 'product_name', 'category', 'variant' etc.
#         self.col_index_by_day: int = int(col_index) + 4

#     def add_new_product(
#         self,
#         product_name: str,
#         category: str ,
#         stock_in: int,
#         stock_out: int,
#         before: int
#     ) -> Any:
#         # check if its first element that would be appended
#         first_element: ValueRange | List[List[str]] = self.worksheet.get("A2:A3")
#         if not first_element[0]:
#             self.worksheet.append_row(
#                 values=[
#                     product_name,
#                     category,
#                     before,
#                 ],
#                 table_range="A2:C2"

#             )  # type: ignore
#         else:
#             self.worksheet.append_row(
#                 values=[
#                     product_name,
#                     category,
#                     before,
#                 ]
#             )  # type: ignore
#         product_position:Cell = self.product_position(name=product_name)

#         if stock_in:
#             old_stock_in = self.get_product_stock_in(row=product_position.row,col=self.col_index_by_day)
#             self.update_stock_in(row=product_position.row, amount=old_stock_in, old_stock_in=self.col_index_by_day)
#         elif stock_out:
#             # + 1 because stock_out in next row
#             old_stock_out:int = self.get_product_stock_out(row=product_position.row,col=self.col_index_by_day)
#             self.update_stock_out(row=product_position.row, amount=old_stock_out, old_stock_out=self.col_index_by_day)

#     def update_stock_in(self, amount: int, row: int, old_stock_in:int) -> None:
#         increment_values: int = old_stock_in + amount
#         logger.info(f"update day report stock_out by value'{increment_values}'")
#         self.worksheet.update_cell(row=row, col=self.col_index_by_day, value=increment_values)

#     def update_stock_out(self, amount: int, row: int, old_stock_out:int) -> None:
#         # + 1 because stock_out in next row
#         increment_values: int = old_stock_out + amount
#         logger.info(f"update monthly stock_out by value '{amount}'")
#         self.worksheet.update_cell(row=row + 1, col=self.col_index_by_day, value=-abs(increment_values))

#     def product_position(self, name: str) -> Cell:
#         product: Cell | None = self.worksheet.find(name, in_column=1)

#         if not product:
#             raise ValueError(f"product by name {name} was deleted")

#         return product

#     def product_exist(self, product_name: str) -> bool:
#         product: Cell | None = self.worksheet.find(query=product_name, in_column=1)

#         if product:
#             return True
#         else:
#             return False

#     def get_product_stock_in(self, row:int, col:int) -> int:

#         response: str | None = self.worksheet.cell(row=row,col=col).value
#         if response is None:
#             raise ValueError("monthly stock in data is empty")
#         return int(response)

#     def get_product_stock_out(self, row:int, col:int) -> int:

#         response: str | None = self.worksheet.cell(row=row + 1,col=col).value
#         if response is None:
#             raise ValueError("monthly stock in data is empty")
#         return int(response)
