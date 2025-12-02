import datetime
from typing import Any
from fastapi import FastAPI, Request
from pandas import date_range
from source.services import ManagerCreator
from source.utils import FileName
from source.zettle.handler import ZettleWebhookHandler
from source.zettle.validaton import InventoryBalanceChanged
import logging
from logging_config import setup_logger

setup_logger()

logger: logging.Logger = logging.getLogger(name=__name__)


managers = ManagerCreator()

handler = ZettleWebhookHandler(
    google_drive_file_manager=managers.google_drive_manager,
    spreadsheet_file_manager=managers.spreadsheet_manager,
)

app = FastAPI()


@app.post(path="/store_inventory_data_webhook")
def store_inventory_data_webhook(request: InventoryBalanceChanged) -> None:
    handler.process_webhook(request=request)
