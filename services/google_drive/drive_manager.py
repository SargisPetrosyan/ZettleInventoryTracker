from services.google_drive.client import GoogleDriveClient
from services.google_drive import utils
import datetime
import os 
from dotenv import load_dotenv

load_dotenv()

ROOT_FOLDER = os.getenv("ROOT_FOLDER_ID")

class DriveFileManager:
    def __init__(self, client:GoogleDriveClient) -> None:
        self.client =  client
        
    def create_folder_(self, folder_name, )

client = GoogleDriveClient()

test = DriveFileManager(client) 
test.folder_exist()   