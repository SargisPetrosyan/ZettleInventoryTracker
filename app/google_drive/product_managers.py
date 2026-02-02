from typing import List
from fastapi.responses import JSONResponse
from gspread import Cell, ValueRange, Worksheet
import rich
from sqlalchemy import values

from app.constants import (
    DAY_PRODUCT_AND_VARIANT_ID_COL,
    DAY_PRODUCT_STOCK_IN_COL,
    DAY_PRODUCT_STOCK_OUT_COL,
    MONTH_PRODUCT_AND_VARIANT_ID_COL,
    MONTH_PRODUCT_STOCK_OUT_ROW_OFFSET,
    MONTH_WORKSHEET_FIRST_CELL,
    MONTH_PRODUCT_DATA_CELL_RANGE,
    DAY_PRODUCT_NAME_COL,
    MONTH_PRODUCT_NAME_COL,
)
from app.google_drive.context import Context
import logging

from app.models.google_drive import RowEditResponse
from app.utils import extract_row_from_notation

logger: logging.Logger = logging.getLogger(name=__name__)