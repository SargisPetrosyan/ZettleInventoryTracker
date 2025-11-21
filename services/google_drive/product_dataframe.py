from unittest import result
from pandas import DataFrame  # type:ignore
import logging

logger: logging.Logger = logging.getLogger(name=__name__)


class ProductDataFrame:
    def __init__(self, sheet) -> None:
        logger.info(f"initializing panda Dataframe from raw data")
        self.sheet_data: DataFrame = DataFrame.from_records(
            data=sheet[1:], columns=sheet[0], index="name"
        )

    def product_exist(self, product_name: str) -> bool:
        logger.info(f"check if product '{product_name}' exist")
        try:
            result = self.get_product_row_index(product_name=product_name)
            logger.info(f"product by name '{product_name} exist'")
            return True
        except KeyError:
            logger.info(f"product by name '{product_name}' doesn't exist !!!")
            return False

    def get_product_row_index(self, product_name: str):
        return self.sheet_data.index.get_loc(key=product_name)

    def increment_stock_in(self, product_name: str, amount: int) -> dict:
        row_index = self.get_product_row_index(product_name)
        old_value: int = int(self.sheet_data.at[product_name, "stock_in"])  # type: ignore
        updated: dict = {"row": row_index, "value": old_value + amount}
        return updated

    def increment_stock_out(self, product_name: str, amount: int) -> dict:
        row_index = self.get_product_row_index(product_name)
        old_value: int = int(self.sheet_data.at[product_name, "stock_out"])  # type: ignore
        updated: dict = {"row": row_index, "value": old_value + amount}
        return updated

    def last_row_index(self) -> int:
        row: int = self.sheet_data.shape[0] + 1
        return row
