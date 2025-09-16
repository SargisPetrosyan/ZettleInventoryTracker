import gspread
from googleapiclient.errors import HttpError
from gspread import Cell,utils
from auth import get_drive_credentials
import os 
from pandas import DataFrame,Series
from dotenv import load_dotenv
from typing import Any

load_dotenv()
  
SPREADSHEET_ID = os.getenv("DAY_TEMPLATE_SAMPLE_ID")

class SheetManager:
    def __init__(self, spreadsheet_id, worksheet_name:str) -> None:
        credentials = get_drive_credentials()
        try:
            self.client = gspread.authorize(credentials)
        except HttpError as error:
            raise RuntimeError(f"Failed to build sheet client: {error}")
        self.spreadsheet = self.client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
        self.raw_data = self.spreadsheet.get(return_type=utils.GridRangeType.ListOfLists)
        self.name_col:int = 1
        self.category_col:int = 2
        self.opening_stock_col:int = 3
        self.stock_in_col:int = 4
        self.stock_out_col:int = 5
        self.closing_stock_col:int = 6
        
    def add_product(
        self,
        product_name:str,
        category:str,
        opening_stock:int,
        stock_in: int,
        stock_out:int,
        closing_stock:int, 
        last_row:int,
        ) -> None:
        
        last_element = last_row + 1
        new_row = [[product_name, category, opening_stock, stock_in, stock_out, closing_stock]]
        self.spreadsheet.update(range_name = f"A{last_element}:F{last_element}", values=new_row)
        
        
    def update_stock_in(self, value:int,row:int)-> None:
        self.spreadsheet.update_cell(row=row + 2, col=self.stock_in_col, value=value)
        
    def update_stock_out(self, value:int,row:int)-> None:
        self.spreadsheet.update_cell(row=row + 2, col=self.stock_out_col, value=value)
        


class ProductDataFrame:
    def __init__(self, sheet:SheetManager,) -> None:
        self.sheet_data = DataFrame.from_records(
            sheet.raw_data[1:],
            columns=sheet.raw_data[0],
            index="name"
        )
           
    def get_product_data(self, product_name:str) -> DataFrame | Series:
        return self.sheet_data.loc[f"{product_name}"]
 
    def get_product_row_index(self,product_name:str):
        return self.sheet_data.index.get_loc(product_name)
    
    def increment_stock_in(self, product_name:str, amount:int) -> dict:
        row_index = self.get_product_row_index(product_name)
        old_value:int = int(self.sheet_data.at[product_name, "stock_in"])
        updated:dict = {
            'row':row_index, 
            "value":old_value + amount
            }
        return updated
    
    def increment_stock_out(self, product_name:str, amount:int) -> dict:
        row_index = self.get_product_row_index(product_name)
        old_value:int = int(self.sheet_data.at[product_name, "stock_out"])
        updated:dict = {
            'row':row_index, 
            "value":old_value + amount
            }
        return updated
    
    def last_row_index(self) -> int:
        row:int = self.sheet_data.shape[0] + 1
        return row

