
from pandas import DataFrame  # type:ignore
import logging
import pandas as pd

from app.models.product import PaypalProductData

logger: logging.Logger = logging.getLogger(name=__name__)

class DayProductDataFrameManager:
    def __init__(self, sheet:list[list]) -> None:
        logger.info(f"initializing panda Dataframe from raw data")
        self.sheet_data: DataFrame = DataFrame.from_records(
            data=sheet[1:], columns=sheet[0], index="name"
        )
        self._convert_to_int()
    
    def add_new_product(self,product:DataFrame) -> None:
        self.sheet_data = pd.concat([self.sheet_data,product])
        logger.info(f"new product was added successfully")
    
    def new_dataframe(self,product:PaypalProductData) -> DataFrame:
        data = {
            "category": product.category_name, 
            "variant": product.variant_name,
            "cost_price": product.price,
            "stock_in": product.after - product.before if product.after - product.before > 0 else 0,
            "stock_out": product.after - product.before if product.after - product.before < 0 else 0,
            "ID": product.product_variant_uuid,
    }
        return pd.DataFrame(data=data, index=[product.name])

    def increment_stock_in(self, product_variant_id: str, amount: int) -> None:
        self.sheet_data.loc[self.sheet_data["ID"] == product_variant_id, "stock_in"] += int(amount)

    def increment_stock_out(self, product_variant_id: str, amount: int) -> None:
        self.sheet_data.loc[self.sheet_data["ID"] == product_variant_id, "stock_out"] += amount
    
    def product_exist(self, product_variant_id: str) -> bool:
        return product_variant_id in self.sheet_data.values

    def _convert_to_int(self) -> None:
        self.sheet_data[["stock_in", "stock_out","cost_price"]] = self.sheet_data[["stock_in", "stock_out","cost_price"]].astype(int)


class MonthProductDataFrameManager:
    def __init__(self, sheet:list[list]) -> None:
        logger.info(f"initializing panda Dataframe from raw data")
        self.sheet_data: DataFrame = DataFrame.from_records(
            data=sheet[1:], columns=sheet[0], index="name"
        )
        self._convert_to_int()
    
    def add_new_product(self,product:DataFrame) -> None:
        self.sheet_data = pd.concat([self.sheet_data,product])
        logger.info(f"new product was added successfully")

    def new_dataframe(self,product:PaypalProductData) -> DataFrame:
        data = {
            "category": product.category_name, 
            "variant": product.variant_name,
            "cost_price": product.price,
            str(product.timestamp.day): product.after - product.before if product.after - product.before > 0 else 0,
            str(product.timestamp.day + 1): product.after - product.before if product.after - product.before < 0 else 0,
            "ID": product.product_variant_uuid,
    }
        return pd.DataFrame(data=data, index=[product.name])

    def increment_stock_in(self, product_variant_id: str,day:int, amount: int) -> None:
        self.sheet_data.loc[self.sheet_data["ID"] == product_variant_id, str(day)] += int(amount)

    def increment_stock_out(self, product_variant_id: str, day:int, amount: int) -> None:
        self.sheet_data.loc[self.sheet_data["ID"] == product_variant_id, str(day)] += amount
    
    def product_exist(self, product_variant_id: str) -> bool:
        return product_variant_id in self.sheet_data.values

    def _convert_to_int(self) -> None:
        self.sheet_data[[str(x) for x in range(1,101)]] = self.sheet_data[[str(x) for x in range(1,101)]].astype(int)

