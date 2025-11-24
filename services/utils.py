from datetime import datetime
import logging

logger: logging.Logger = logging.getLogger(name=__name__)


class FileName:
    def __init__(self, date: datetime) -> None:
        logger.info(f"initializing file name")
        self.year: str = str(object=date.year)
        self.month: str = str(object=date.month).zfill(2)
        self.day: str = str(object=date.day).zfill(2)
        self.month_name: str = str(object=date.strftime("%B"))
        self.file_name: str = f"{self.year}-{self.month}-{self.month_name}"
        self.monthly_report_name: str = f"{self.year}-monthly report"
        logger.info(f"file name was created 'file_name: {self.file_name}'")


def check_stock_in_or_out(before: int, after: int, change: int) -> dict[str, int]:
    logger.info("check if product update stock_in or stock out")
    if before > after:
        logger.info(f" product is 'stock_out' 'before: {before} > after: {after}'")
        return {"stock_in": 0, "stock_out": change, "before": before}
    else:
        logger.info(f" product is 'stock_in' 'before: {before} < after: {after}'")
        return {"stock_in": change, "stock_out": 0, "before": before}


def sheet_exist(items: dict[str, int], sheet_name: str) -> int | None:
    for sheet, index in items.items():
        if sheet == sheet_name:
            return index
    return None
