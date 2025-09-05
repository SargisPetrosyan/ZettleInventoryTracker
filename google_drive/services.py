import os
from dotenv import load_dotenv
from datetime import date
from client import GoogleDriveClient

load_dotenv()

class GoogleDriveServices:
    def __init__(self) -> None:
        self.drive = GoogleDriveClient()
        self.INVENTORY_FOLDER_ID = os.getenv("INVENTORY_TRACKING_FOLDER_ID")
        self.INVENTORY_SAMPLE_FILE_ID = os.getenv("INVENTORY_SAMPLE_FILE_ID")
        
    def get_drive_file_list(self) -> list:
        query = f"'{self.INVENTORY_FOLDER_ID}' in parents and trashed=false"
        results = self.drive.client.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType)"
            ).execute()
        
        return results.get("files", [])
    
    def duplicate_drive_file(self):
        self.drive.client().files().copy(
            fileid=self.INVENTORY_SAMPLE_FILE_ID
        )
        
        
        