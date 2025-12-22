from operator import inv
from fastapi import FastAPI, Request
from flask import request
import rich
from core.utils import OrganizationsNameMappedId
import logging
from core.zettle.validation.inventory_update_validation import InventoryBalanceUpdateValidation
from logging_config import setup_logger
from setup_db import Database
from webhook_handler import SubscriptionHandler

setup_logger()
logger: logging.Logger = logging.getLogger(name=__name__)

database: Database = Database()
webhook_handler = SubscriptionHandler()

app = FastAPI()

@app.post("/store_inventory_data_webhook")
async def store_inventory_data_webhook(request: Request) -> None:
    payload = await request.json() 
    validated_data = InventoryBalanceUpdateValidation(**payload)
    webhook_handler.process_subscription(inventory_update=validated_data, database=database)

