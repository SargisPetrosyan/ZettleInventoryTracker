from services.google_drive.client import GoogleDriveClient, SpreadSheetClient
import os
from validaton import validate_inventory_update, validating_product_data
from dotenv import load_dotenv

import json

load_dotenv()


class ZettleWebhookHandler:
    def __init__(self) -> None:
        self.drive_client = GoogleDriveClient()
        self.sheet_client = SpreadSheetClient()

    def process_webhook(self, inventory_update, product_data):
        payload = json.load(inventory_update)
        product_data = json.load(product_data)
        inventory_update_validated = validate_inventory_update(payload=payload)
        product_data_validated = validating_product_data(product_data)
