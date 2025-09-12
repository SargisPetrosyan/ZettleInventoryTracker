from client import GoogleSheetServices
import pandas as pd
from pandas import DataFrame

class DriveSheetServices:
    def __init__(self,product_name: str, ) -> None:
        self.sheet = GoogleSheetServices()
        self.product_name:str = product_name
        self.row_sheet_data:DataFrame = pd.DataFrame(self.sheet.get_sheet_data())
        self.sheet_data:DataFrame = self._format_row_data_to_panda()
        self.product_data = self._check_product_exist(product_name)

        
    def _format_row_data_to_panda(self) -> DataFrame:
        df = self.row_sheet_data.copy()
        df.columns = df.iloc[0]  
        df = df[1:]               
        df = df.reset_index(drop=True)
        cols = ["opening_stock", "stock_in", "stock_out", "closing_stock"]
        df[cols] = df[cols].apply(pd.to_numeric, errors="coerce" )
        
        return df

    def _check_product_exist(self,product_name: str):
        product_exist:DataFrame = self.sheet_data.loc[self.sheet_data['product_name'] == product_name]
        
        if product_exist.empty:
            return self.create_new_object()
        return product_exist
    
    def create_new_object_row(
        self,product_name: str,
        product_id: int,
        opening_stock:int,
        stock_in: int,
        stock_out: int,
        closing_stock: int) -> None:
        
        new_row:DataFrame = pd.DataFrame({
            'product_name':[f"{product_name}"],
            'product_id' : [product_id],
            'opening_stock': [opening_stock],
            'stock_in': [stock_in],
            "stock_out": [stock_out],
            "closing_stock": [closing_stock]})
        
        
        self.sheet_data = pd.concat([self.sheet_data, new_row], ignore_index=True)
        self.product_data = new_row
    
    def update_stock_in(self,quantity:int)->None:
        self.product_data.loc[self.product_data["product_name"] == self.product_name, "stock_in"] += quantity

    def update_stock_out(self,quantity:int)->None:
        self.product_data.loc[self.product_data["product_name"] == self.product_name, "stock_out"] += quantity
    
