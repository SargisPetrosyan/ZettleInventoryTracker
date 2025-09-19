from datetime import datetime


class FileName:
    def __init__(self, date: datetime) -> None:
        self.year: str = str(date.year)
        self.month: str = str(date.month).zfill(2)
        self.day: str = str(date.day).zfill(2)
        self.month_name: str = str(date.strftime("%B"))
        self.name: str = f"{self.year}-{self.month}-{self.month_name}"


def check_stock_in_or_out(before: int, after: int, change: int) -> dict[str, int]:
    if before > after:
        return {"stock_in": 0, "stock_out": change}
    else:
        return {"stock_in": change, "stock_out": 0}
