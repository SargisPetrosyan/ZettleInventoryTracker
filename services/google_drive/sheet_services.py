from client import GoogleSheetServices
import pandas as pd
from pandas import DataFrame

class DriveSheetServices:
    def __init__(self,product_name: str) -> None:
        self.sheet = GoogleSheetServices()
        self.product_name:str = product_name
        self.row_sheet_data:DataFrame = pd.DataFrame(self.sheet.get_sheet_data())
        self.sheet_data:DataFrame = self._format_row_data_to_panda()
        self.product_data:DataFrame = self._check_product_exist(product_name)

        
    def _format_row_data_to_panda(self) -> DataFrame:
        df = self.row_sheet_data.copy()
        df.columns = df.iloc[0]  
        df = df[1:]               
        df = df.reset_index(drop=True)
        
        return df

    def _check_product_exist(self,product_name: str):
        product_exist:DataFrame = self.sheet_data.loc[self.sheet_data['product_name'] == product_name]
        
        if product_exist.empty:
            return self.create_new_object()
        return product_exist
    
    def create_new_object(self) ->DataFrame:
        return 'new product was created'
    