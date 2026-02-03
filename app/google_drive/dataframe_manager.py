
from pandas import DataFrame  # type:ignore
import logging
import pandas as pd

from app.models.product import MonthlyStockDataBuilder, PaypalProductData
from app.utils import dataframe_formatter

logger: logging.Logger = logging.getLogger(name=__name__)

class DayProductDataFrameManager:
    def __init__(self, day_dataframe:DataFrame ) -> None:
        self.day_dataframe: DataFrame  = day_dataframe
    
    def add_new_product(self,product:PaypalProductData) -> None:
        data = {
            "category": product.category_name, 
            "variant": product.variant_name,
            "cost_price": product.price,
            "stock_in": 0,
            "stock_out": 0,
            "ID": product.product_variant_uuid,
    }
        formatted_dataframe:DataFrame = pd.DataFrame(data=data, index=[product.name])
        self.sheet_data: DataFrame = pd.concat(objs=[self.day_dataframe,formatted_dataframe])
        logger.info(f"new product was added successfully")
    
    def increment_stock_in(self, product_variant_id: str, amount: int) -> None:
        self.sheet_data.loc[self.sheet_data["ID"] == product_variant_id, "stock_in"] += int(amount)

    def increment_stock_out(self, product_variant_id: str, amount: int) -> None:
        self.sheet_data.loc[self.sheet_data["ID"] == product_variant_id, "stock_out"] += amount
    
    def product_exist(self, product_variant_id: str) -> bool:
        return product_variant_id in self.day_dataframe.values

    def _convert_to_int(self) -> None:
        self.sheet_data[["stock_in", "stock_out","cost_price"]] = self.sheet_data[["stock_in", "stock_out","cost_price"]].astype(int)


        
class MonthProductDataFrameManager:
    def __init__(self, month_dataframe:DataFrame) -> None:
        self.month_dataframe: DataFrame = month_dataframe
    
    def add_new_product(self,product:PaypalProductData) -> None:
        product_data = MonthlyStockDataBuilder(product_data=product)
        formatted_dataframe: DataFrame = dataframe_formatter(row_data=product_data.normalized_data)
        self.sheet_data: DataFrame = pd.concat([self.month_dataframe,formatted_dataframe])
        logger.info(f"new product was added successfully")

    def increment_stock_in(self, product_variant_id: str,day:int, amount: int) -> None:
        self.sheet_data.loc[self.sheet_data["ID"] == product_variant_id, str(day)] += int(amount)

    def increment_stock_out(self, product_variant_id: str, day:int, amount: int) -> None:
        self.sheet_data.loc[self.sheet_data["ID"] == product_variant_id, str(day)] += amount
    
    def product_exist(self, product_variant_id: str) -> bool:
        return product_variant_id in self.sheet_data.values
    

    
    



