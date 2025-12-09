from fastapi import FastAPI
from pandas import date_range
from core.utils import ManagersCreator
from core.zettle.handler import ZettleWebhookHandler
from core.zettle.validaton import InventoryBalanceChanged
import logging
from logging_config import setup_logger

setup_logger()

logger: logging.Logger = logging.getLogger(name=__name__)
managers = ManagersCreator()

handler = ZettleWebhookHandler(
    google_drive_file_manager=managers.google_drive_manager,
    spreadsheet_file_manager=managers.spreadsheet_manager,
)

app = FastAPI()

@app.get(path="/hello")
def test_server() -> dict[str, str]:
    data: dict[str, str] = {"test":"working"}
    return data

@app.post(path="/store_inventory_data_webhook")
def store_inventory_data_webhook(request: InventoryBalanceChanged) -> None:
    handler.process_webhook(request=request)

