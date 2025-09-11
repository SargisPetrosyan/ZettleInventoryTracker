from client import GoogleSheetServices
import pandas as pd
from pandas import DataFrame

class DriveSheetServices:
    def __init__(self) -> None:
        self.sheet = GoogleSheetServices()
        self.row_sheet_data = pd.DataFrame(self.sheet.get_sheet_data())
        self.sheet_data = self._format_row_data_to_panda()

        
    def _format_row_data_to_panda(self) -> DataFrame:
        df = self.row_sheet_data.copy()
        df.columns = df.iloc[0]  
        df = df[1:]               
        df = df.reset_index(drop=True)
        
        return df
