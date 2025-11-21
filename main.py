from typing import Any
from fastapi import FastAPI, Request
from services.zettle.handler import ZettleWebhookHandler
from services.zettle.validaton import InventoryBalanceChanged
import logging
from logging_config import setup_logger

logger: logging.Logger = logging.getLogger(name=__name__)

setup_logger()

app = FastAPI()

handler = ZettleWebhookHandler()


@app.post(path="/store_inventory_data_webhook")
def store_inventory_data_webhook(request: InventoryBalanceChanged) -> None:
    request_body: dict[str, Any] = request.model_dump()
    handler.process_webhook(request=request_body)
