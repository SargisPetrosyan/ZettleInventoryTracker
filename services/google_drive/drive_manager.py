from services.google_drive.client import GoogleDriveClient
from services.google_drive import utils
import datetime
import json
import os 
from dotenv import load_dotenv

load_dotenv()

ROOT_FOLDER = os.getenv("ROOT_FOLDER_ID")

class DriveFileManager:
    def __init__(self, client:GoogleDriveClient) -> None:
        self.client =  client
        
    def create_year_folder(self, year:str, parent_folder_id:str, sample_file_id:str, nested_file_name:str):
        year_folder = self.client.create_folder(folder_name=year, parent_folder_id=parent_folder_id)
        year_folder_id = year_folder.get('id')
        self.client.create_folder(folder_name='months', parent_folder_id=year_folder_id)
        
        return self.client.duplicate_drive_file(
            file_id=sample_file_id, 
            parent_folder_id=year_folder_id,
            file_name=nested_file_name)