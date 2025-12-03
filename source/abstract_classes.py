from abc import ABC, abstractmethod

from gspread import Cell

from source.context import Context


class WorksheetProductReader(ABC):
    @abstractmethod
    def get_product_row_position(self, product_name: str) -> int | None:
        raise NotImplementedError

    @abstractmethod
    def get_product_stock_in(self, product_row: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_product_stock_out(self, product_row: int) -> int:
        raise NotImplementedError


class WorksheetProductWriter(ABC):
    @abstractmethod
    def add_new_product(self, context: Context):
        raise NotImplementedError

    @abstractmethod
    def update_stock_in(self, old_stock_in: int, amount: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_stock_out(self, old_stock_out: int, amount: int) -> None:
        raise NotImplementedError
