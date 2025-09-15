import gspread
from googleapiclient.errors import HttpError
from gspread import Cell
from auth import get_drive_credentials
import os 
from dotenv import load_dotenv

load_dotenv()
  
SPREADSHEET_ID = os.getenv("DAY_TEMPLATE_SAMPLE_ID")

class SpreadsheetManager:
    def __init__(self, spreadsheet_id, worksheet_name:str) -> None:
        credentials = get_drive_credentials()
        try:
            self.client = gspread.authorize(credentials)
        except HttpError as error:
            raise RuntimeError(f"Failed to build sheet client: {error}")
        self.spreadsheet = self.client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    
    def get_product(self, product_name:str) -> Cell | None:
        return self.spreadsheet.find(product_name)
    
    
    def get_all_values(self):
        return self.spreadsheet.get_all_values()
    
    def update_numeric_call(self,row,amount:int):
        
        self.spreadsheet.update()
        
    
    def append_element(
        self,
        product_name:str,
        category:str,
        opening_stock:int,
        stock_in: int,
        stock_out:int,
        closing_stock:int, 
        ) -> None:
        last_element = len(self.get_all_values()) + 1
        
        new_row = [[product_name, category, opening_stock, stock_in, stock_out, closing_stock]]
        self.spreadsheet.update(range_name = f"A{last_element}:F{last_element}", values=new_row)
        
        
    def stock_in(self, 
        product_name:str,
        category:str,
        opening_stock:int,
        stock_in: int,
        stock_out:int,
        closing_stock:int,
        )-> None:
        
        if not self.get_product(product_name=product_name):
            self.append_element(
                product_name=product_name,
                category=category,
                opening_stock=opening_stock,
                stock_in=stock_in,
                stock_out=stock_out,
                closing_stock=closing_stock)
            

