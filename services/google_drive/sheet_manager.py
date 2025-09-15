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
        self.name_col:int = 1
        self.category_col:int = 2
        self.opening_stock_col:int = 3
        self.stock_in_col:int = 4
        self.stock_out_col:int = 5
        self.closing_stock_col:int = 6
    
    def get_product(self, product_name:str) -> Cell | None:
        return self.spreadsheet.find(product_name)
    
    def get_cell_value(self,row:int,col:int)-> str|None:
        return self.spreadsheet.cell(row=row,col=col).value
    
    def get_all_values(self):
        return self.spreadsheet.get_all_values()
    
    def update_numeric_call(self,row:int, col:int, amount:int,):
        value = self.get_cell_value(row=row,col=col)
        formula:str = f"={value}+{amount}"
        self.spreadsheet.update_cell(row, col, formula)
        
    
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
        
        product_data:Cell|None = self.get_product(product_name=product_name)
        if product_data is None:
            self.append_element(
                product_name=product_name,
                category=category,
                opening_stock=opening_stock,
                stock_in=stock_in,
                stock_out=stock_out,
                closing_stock=closing_stock)
        else:    
            self.product_data = product_data
            row:int = self.product_data.row
            self.update_numeric_call(row=row,col=self.stock_in_col, amount=stock_in)
            
test = SpreadsheetManager(spreadsheet_id=SPREADSHEET_ID,worksheet_name="Sheet1")

test.stock_in(
    product_name = "product_5",
    category = "Electronics",
    opening_stock = 120,
    stock_in = 30,
    stock_out = 0,
    closing_stock=300,
)    

            
