import os
from dotenv import load_dotenv
from client import GoogleDriveServices
from googleapiclient.errors import HttpError

load_dotenv()

class DriveInventoryServices:
    def __init__(self ) -> None:
        self.drive = GoogleDriveServices()
        self.MAIN_FOLDER_ID: str | None= os.getenv("ROOT_FOLDER_ID")
        self.TEMPLATE_SAMPLE_ID: str | None = os.getenv("TEMPLATE_SAMPLE_ID")
        
    def duplicate_template(self, file_name: str, parent_folder_id: str):
        self.drive.duplicate_drive_file(
            file_id=self.TEMPLATE_SAMPLE_ID, 
            file_name = file_name,
            parent_folder_id=parent_folder_id,
            )
        
        try:
            file = self.drive.get_drive_file(file_id=file_name)
            return file
        except HttpError as error:
            print(f"An error occurred: file does't exist {error}")
            

            
        
            
        
        