from fastapi import FastAPI
from core.utils import OrganizationsNameMappedId
import logging
from core.zettle.validation.inventory_update_validation import InventoryBalanceChanged
from logging_config import setup_logger
from setup_db import Database
from webhook_handler import SubscriptionHandler

setup_logger()
logger: logging.Logger = logging.getLogger(name=__name__)

database: Database = Database()
webhook_handler = SubscriptionHandler()

app = FastAPI()

@app.post(path="/store_inventory_data_webhook")
async def store_inventory_data_webhook(inventory_update: InventoryBalanceChanged) -> None:
    webhook_handler.process_subscription(inventory_update=inventory_update, database=database)

