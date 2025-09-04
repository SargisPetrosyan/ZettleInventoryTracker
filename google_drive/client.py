#googleDrive
from auth import get_drive_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleDriveClient:
    def __init__(self):
        creds = get_drive_credentials()
        try:
            self.client = build("drive", "v3", credentials=creds)
        except HttpError as error:
            raise RuntimeError(f"Failed to build drive client: {error}")
                
            
            


            