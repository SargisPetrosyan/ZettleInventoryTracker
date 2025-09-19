from datetime import datetime
from services.zettle.validaton import InventoryBalanceChanged

def create_name(date: datetime ) -> dict:
    year:int = date.date().year
    month:int = date.date().month
    month_name: str = date.strftime("%B")
    day:int = date.date().day
    file_name: str = f"{year}-{month}-{month_name}"
    
    date_data:dict = {
        "file_name": file_name, 
        "day": str(day),
        "year": str(year),
        "month": str(month)
        }
    
    return date_data
