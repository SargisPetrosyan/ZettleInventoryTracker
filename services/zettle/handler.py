from services.google_drive.client import GoogleDriveClient, SpreadSheetClient
from services.zettle.validaton import InventoryBalanceChanged, ProductData  # type:ignore
from dotenv import load_dotenv
from pydantic import BaseModel
from services.google_drive.utils import create_name
import json

import os 
from dotenv import load_dotenv

load_dotenv()

ROOT_FOLDER = os.getenv("ROOT_FOLDER_ID")
DAY_SAMPLE = os.getenv("DAY_TEMPLATE_SAMPLE_ID")


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
        inventory_update:BaseModel = InventoryBalanceChanged(**INVENTORY_UPDATE)
        product_update:BaseModel = ProductData(**PRODUCT_UPDATE)
        
        name:dict = create_name(inventory_update.timestamp)
        
        #check_year folder
        if not self.drive_client.file_exist(file_name=name.get('year'), folder_name=ROOT_FOLDER, folder=True):
            self.drive_client.create_folder(name=name.get('year'))


        else:
            #select year folder 
            
        
            
        
                
        
    
        print(inventory_update.timestamp)
        
if __name__ == "__main__":
    test = ZettleWebhookHandler()

    test.process_webhook()

