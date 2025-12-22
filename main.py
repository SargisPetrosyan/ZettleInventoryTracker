from ast import Dict
from blinker import ANY
from fastapi import FastAPI, Request
import logging

import rich
from core.zettle.validation.inventory_update_validation import InventoryBalanceUpdateValidation
from logging_config import setup_logger
from setup_db import Database
from webhook_handler import SubscriptionHandler

setup_logger()
logger: logging.Logger = logging.getLogger(name=__name__)

database: Database = Database()
webhook_handler = SubscriptionHandler()

app = FastAPI()

@app.post(path="/store_inventory_data_webhook")
async def store_inventory_data_webhook(request: Request) -> None | dict:
    if request.headers["user-agent"] == "PusherApplication (WebHookPushClient)": # need to change 
        return {"status":"202"}
    payload:dict = await request.json() 
    validated_data = InventoryBalanceUpdateValidation(**payload)
    webhook_handler.process_subscription(inventory_update=validated_data, database=database)

