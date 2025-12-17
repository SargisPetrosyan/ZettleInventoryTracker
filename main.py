from fastapi import FastAPI, Request
from flask import request
from pandas import date_range
import rich
from core.utils import ManagersCreator
from core.zettle.handler import ZettleWebhookHandler
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

@app.get(path="/")
def test_server() -> dict[str, str]:
    data: dict[str, str] = {"test":"working"}
    return data

@app.post("/store_inventory_data_webhook")
async def store_inventory_data_webhook(request: Request):
    body = await request.body()
    rich.print(body.decode())
    return {"status": "ok"}

