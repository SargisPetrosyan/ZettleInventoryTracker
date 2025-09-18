from services.google_drive.client import GoogleDriveClient, SpreadSheetClient
from services.zettle.validaton import validate_inventory_update, validating_product_data  # type:ignore
from dotenv import load_dotenv
from pydantic import BaseModel
import pdb
import json


with open("data/InventoryBalanceChanged.json", "r") as fp:
    INVENTORY_UPDATE = json.load(fp)
with open("data/Product.json", "r") as fp:
    PRODUCT_UPDATE = json.load(fp)

load_dotenv()


class ZettleWebhookHandler:
    def __init__(self) -> None:
        self.drive_client = GoogleDriveClient()
        self.sheet_client = SpreadSheetClient()

    def process_webhook(self):
        inventory_update:BaseModel = validate_inventory_update(payload=INVENTORY_UPDATE)
        product_update:BaseModel = validate_inventory_update(payload=PRODUCT_UPDATE)
        
        

if __name__ == "__main__":
    test = ZettleWebhookHandler()

    test.process_webhook()

