from fastapi import FastAPI, Request
import logging
from core.utils import json_to_dict
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
    data:dict = await request.json() 
    if data["eventName"] == "TestMessage": # need to change 
        logger.info("request for set subscription")
        return {"status":"200"}
    parsed_data:dict = await json_to_dict(request=request) # need to change 
    logger.info("request from webhook")
    validated_data: InventoryBalanceUpdateValidation = InventoryBalanceUpdateValidation.model_validate(obj=parsed_data)
    webhook_handler.process_subscription(inventory_update=validated_data, database=database)

