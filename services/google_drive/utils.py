from datetime import datetime

class FileName:
    def __init__(self,date:datetime) -> None:
        self.year:str = str(date.year)
        self.month:str = str(date.month).zfill(2)
        self.day:str = str(date.day).zfill(2)
        self.month_name:str = str(date.strftime("%B"))
        self.name: str = f"{self.year}-{self.month}-{self.month_name}"
