from http.client import PRECONDITION_FAILED
from math import prod
from typing import List
from gspread.worksheet import JSONResponse
from gspread import Cell, ValueRange, Worksheet

from const import (
    DAY_PRODUCT_STOCK_IN_COL,
    DAY_PRODUCT_STOCK_OUT_COL,
    MONTH_WORKSHEET_FIRST_CELL,
    MONTH_PRODUCT_DATA_CELL_RANGE,
    DAY_PRODUCT_NAME_COL,
    MONTH_PRODUCT_NAME_COL,
    MONTH_PRODUCT_STOCK_IN_COL_OFFSET,
    MONTH_PRODUCT_STOCK_OUT_COL_OFFSET,
)
from core.context import Context
from core.context import Context
import logging

from core.utils import get_row_from_response

logger: logging.Logger = logging.getLogger(name=__name__)


class DayWorksheetProductReader:
    def __init__(
        self,
        worksheet: Worksheet,
    ) -> None:
        self.worksheet: Worksheet = worksheet
        self.stock_in_col: int = DAY_PRODUCT_STOCK_IN_COL
        self.stock_out_index: int = DAY_PRODUCT_STOCK_OUT_COL

    def get_product_row_by_name(self, product_name: str) -> int:
        product: Cell | None = self.worksheet.find(
            query=product_name, in_column=DAY_PRODUCT_NAME_COL
        )

        if not product:
            raise ValueError("Product was deleted")
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

    def product_exist(self, product_name: str) -> bool:
        product: Cell | None = self.worksheet.find(
            query=product_name, in_column=DAY_PRODUCT_NAME_COL
        )

        if not product:
            return False
        return True


class DayWorksheetProductWriter:
    def __init__(self, worksheet: Worksheet) -> None:
        self.worksheet: Worksheet = worksheet

    def add_new_product(self, context: Context) -> None:
        new_row: list[str | int] = [
            context.product_data.name,
            context.product_data.category,
            context.stock_in_out.before,
        ]
        self.worksheet.append_row(values=new_row)
        return

    def update_stock_in(
        self,
        old_stock_in: int,
        amount: int,
        row: int,
    ) -> None:
        increment_values: int = old_stock_in + amount
        logger.info(f"update day report stock_out by value'{increment_values}'")
        self.worksheet.update_cell(
            row=row, value=increment_values, col=DAY_PRODUCT_STOCK_IN_COL
        )

    def update_stock_out(self, old_stock_out: int, amount: int, row: int) -> None:
        old_value: int = old_stock_out
        increment_values: int = old_value + amount
        logger.info(f"update day report stock_out by value'{increment_values}'")
        self.worksheet.update_cell(
            row=row,
            col=DAY_PRODUCT_STOCK_OUT_COL,
            value=-abs(increment_values),
        )


class MonthWorksheetProductReader:
    def __init__(
        self,
        worksheet: Worksheet,
    ) -> None:
        self.worksheet: Worksheet = worksheet
        self.stock_in_col: int = DAY_PRODUCT_STOCK_IN_COL
        self.stock_out_col: int = DAY_PRODUCT_STOCK_OUT_COL

    def get_product_row_by_name(
        self,
        product_name: str,
    ) -> int:
        product: Cell | None = self.worksheet.find(
            query=product_name, in_column=MONTH_PRODUCT_NAME_COL
        )

        if not product:
            return 0

        return product.row

    def get_product_stock_in(self, product_row: int, stock_in_col: int) -> int:
        product: Cell = self.worksheet.cell(row=product_row, col=stock_in_col)

        if not product.value:
            return 0
        return int(product.value)

    def get_product_stock_out(self, product_row: int, stock_out_col: int) -> int:
        stock_out: Cell = self.worksheet.cell(row=product_row, col=stock_out_col)

        if not stock_out.value:
            return 0
        return int(stock_out.value)

    def product_exist(self, product_name: str) -> bool:
        product: Cell | None = self.worksheet.find(
            query=product_name, in_column=MONTH_PRODUCT_NAME_COL
        )

        if not product:
            return False
        return True


class MonthWorksheetProductWriter:
    def __init__(self, worksheet: Worksheet) -> None:
        self.worksheet: Worksheet = worksheet

    def add_new_product(self, context: Context) -> None:
        first_element: ValueRange | List[List[str]] = self.worksheet.get(
            range_name=MONTH_WORKSHEET_FIRST_CELL
        )
        if not first_element[0]:
            self.worksheet.append_row(
                values=[
                    context.product_data.name,
                    context.product_data.category,
                    context.product_update.inventory.before,
                ],
                table_range=MONTH_PRODUCT_DATA_CELL_RANGE,
            )

        else:
            self.worksheet.append_row(
                values=[
                    context.product_data.name,
                    context.product_data.category,
                    context.product_update.inventory.before,
                ]
            )

        self._col = int(context.name.month_stock_in_and_out_col_index)

    def update_stock_in(
        self,
        old_stock_in: int,
        amount: int,
        row: int,
        col: int,
    ) -> None:
        increment_values: int = old_stock_in + amount
        logger.info(
            msg=f"update day report stock_out by value: '{increment_values}' row:'{row}', col:'{col}'"
        )

        self.worksheet.update_cell(
            row=row,
            value=increment_values,
            col=col
            + MONTH_PRODUCT_STOCK_IN_COL_OFFSET,  # first 4 columns are 'product_name' 'category' etc.
        )

    def update_stock_out(
        self, old_stock_out: int, amount: int, row: int, col: int
    ) -> None:
        old_value: int = old_stock_out
        increment_values: int = old_value + amount
        logger.info(
            msg=f"update day report stock_out by value'{increment_values}' row:'{row}', col:'{col}'"
        )
        self.worksheet.update_cell(
            row=row,
            col=col
            + MONTH_PRODUCT_STOCK_IN_COL_OFFSET,  # first 4 columns are 'product_name' 'category' etc.
            value=-abs(increment_values),
        )
