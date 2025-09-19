from pandas import DataFrame


class ProductDataFrame:
    def __init__(self, sheet) -> None:
        self.sheet_data = DataFrame.from_records(
            sheet[1:], columns=sheet[0], index="name"
        )

    def get_product_data(self, product_name: str):
        return self.sheet_data.get([f"{product_name}"])

    def get_product_row_index(self, product_name: str):
        return self.sheet_data.index.get_loc(product_name)

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
