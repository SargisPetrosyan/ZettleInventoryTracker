from datetime import date
from client import GoogleDriveClient

class GoogleDriveServices:
    def __init__(self):
        self.drive = GoogleDriveClient()
        
    def get_drive_file_list(self):
        results = (
            self.drive.client.files()
            .list(fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        

            


drive_servies = GoogleDriveServices()

                
drive_servies.get_drive_file_list()

    