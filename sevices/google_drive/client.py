import os
from dotenv import load_dotenv
from datetime import date
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from sevices.google_drive.auth import get_drive_credentials
from typing import Any, Optional



class GoogleDriveServices:
    def __init__(self) -> None:
        creds = get_drive_credentials()
        try:
            self.client = build("drive", "v3", credentials=creds)
        except HttpError as error:
            raise RuntimeError(f"Failed to build drive client: {error}")
        
    def get_drive_file_list(self,folder_id: str, page_size: int ) -> dict[str, dict[str, Any] | Any]:
        """List files matching a query."""
        results = self.client.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=page_size,
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        return results.get("files", [])
    
    def duplicate_drive_file(self, file_id: Optional[str], file_name:str | None, parent_folder_id: str
        ) -> dict[str, dict[str, Any] | Any]:
        """Duplicate a file and return metadata for the new copy."""
        return self.client.files().copy(
            fileId=file_id,
            body={'name': file_name,
                  'parents': [parent_folder_id]}
        ).execute()
    
    def delete_drive_file(self,file_id:str) -> dict:
        """Delete drive file by id"""
        return self.client.files().delete(
            fileId=file_id
        ).execute()
        
    def get_drive_file(self,file_id:str) -> dict[str, dict[str, Any] | Any]:
        return self.client.files().get(
            fileId=file_id,
            ).execute()
        
    
        
    