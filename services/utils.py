from datetime import datetime



class FileName:
    def __init__(self, date: datetime) -> None:
        self.year: str = str(object=date.year)
        self.month: str = str(object=date.month).zfill(2)
        self.day: str = str(object=date.day).zfill(2)
        self.month_name: str = str(object=date.strftime("%B"))
        self.file_name: str = f"{self.year}-{self.month}-{self.month_name}"


def check_stock_in_or_out(before: int, after: int, change: int) -> dict[str, int]:
    if before > after:
        return {"stock_in": 0, "stock_out": change, "before": before}
    else:
        return {"stock_in": change, "stock_out": 0, "before": before}


def sheet_exist(items: dict[str, int], sheet_name: str) -> int | None:
    for sheet, index in items.items():
        if sheet == sheet_name:
            return index
    return None
