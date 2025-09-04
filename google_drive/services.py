from datetime import date
from client import GoogleDriveClient

class GoogleDriveServices:
    def __init__(self) -> None:
        self.drive = GoogleDriveClient()
        self.file_name = "inventory_upload" + str(date.today()).strip()
        
    def get_drive_files(self) -> list:
        results = (
            self.
            drive.
            client.
            files().list(fields="nextPageToken, files(id, name)").
            execute()
        )
        print(results.get("files", []))
    
    def find_drive_file(self,file_name:str):
        drive_files = self.get_drive_files()
        
        for file in drive_files:
            if file.get["name"] = self.file_name