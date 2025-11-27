import logging

from gspread import Cell
from const import (
    PRODUCT_NAME_INDEX,
    PRODUCT_CATEGORY_INDEX,
    PRODUCT_OPENING_STOCK_INDEX,
    PRODUCT_STOCK_IN_INDEX,
    PRODUCT_STOCK_OUT_INDEX,
    PRODUCT_CLOSING_STOCK_INDEX,
)

logger: logging.Logger = logging.getLogger(name=__name__)

# class MounthlyDataFrame:
#     def __init__(self, sheet, day) -> None:
#         logger.info(f"initializing panda Dataframe from raw data")
#         self.sheet_data: DataFrame = DataFrame.from_records(
#             data=sheet[1:], columns=sheet[0], index="name"
#         )
#         self.day:int = day

#     def product_exist(self, product_name: str) -> bool:
#         logger.info(f"check if product '{product_name}' exist")
#         try:
#             self.get_product_row_index(product_name=product_name)
#             logger.info(f"product by name '{product_name} exist'")
#             return True
#         except KeyError:
#             logger.info(f"product by name '{product_name}' doesn't exist !!!")
#             return False

#     def get_product_row_index(self, product_name: str) -> int:
#         return self.sheet_data.index.get_loc(key=product_name) #type: ignore

#     def increment_stock_in(self, product_name: str, amount: int) -> dict:
#         row_index: int = self.get_product_row_index(product_name=product_name)
#         old_value: int = int(self.sheet_data.at[product_name, str(self.day)])  # type: ignore
#         updated: dict = {"row": row_index, "value": old_value + amount}
#         return updated

#     def increment_stock_out(self, product_name: str, amount) -> dict:
#         row_index: int = self.get_product_row_index(product_name=product_name) + 1
#         old_value: int = int(self.sheet_data.iloc[row_index, self.day + 2])  # type: ignore
#         updated: dict = {"row": row_index, "value": old_value + amount}
#         return updated

#     def last_row_index(self) -> int:
#         row: int = self.sheet_data.shape[0] + 1
#         return row
