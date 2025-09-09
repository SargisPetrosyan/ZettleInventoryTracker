import os
from dotenv import load_dotenv
from datetime import date
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from client import get_drive_credentials

load_dotenv()

class GoogleDriveServices:
    def __init__(self) -> None:
        creds = get_drive_credentials()
        try:
            self.client = build("drive", "v3", credentials=creds)
        except HttpError as error:
            raise RuntimeError(f"Failed to build drive client: {error}")
        
        self.INVENTORY_FOLDER_ID = os.getenv("INVENTORY_TRACKING_FOLDER_ID")
        self.INVENTORY_SAMPLE_FILE_ID = os.getenv("INVENTORY_SAMPLE_FILE_ID")
        self.folder_query = f"'{self.INVENTORY_FOLDER_ID}' in parents and trashed=false"
        
    def get_drive_file_list(self) -> list:
        results = self.client.files().list(
            q=self.folder_query,
            pageSize=100,
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        return results.get("files", [])
    
    def duplicate_drive_file(self):
        self.client.files().copy(
            fileId=self.INVENTORY_SAMPLE_FILE_ID
        ).execute()
    
    def delete_drive_file(self):
        self.client.files().delete(
            fileId=self.INVENTORY_SAMPLE_FILE_ID
        ).execute()
        
    def drive_get_file(self):
        self.client.files().get(
            fileId=self.INVENTORY_SAMPLE_FILE_ID,
            fields="id, name, permissions"
            ).execute()
        
    