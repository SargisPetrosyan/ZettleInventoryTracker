from services.google_drive.client import GoogleDriveClient
from services import utils
import datetime
import json
import os
from dotenv import load_dotenv
from services.utils import FileName

load_dotenv()

ROOT_FOLDER = os.getenv("ROOT_FOLDER_ID")


class DriveFileManager:
    def __init__(self, client: GoogleDriveClient) -> None:
        self.client = client

    def create_year_folder(
        self,
        year: str,
        parent_folder_id: str,
    ) -> str:
        # create year folder
        year_folder = self.client.create_folder(
            folder_name=year, parent_folder_id=parent_folder_id
        )

        year_folder_id: str = year_folder["id"]
        # create nested month folder
        self.client.create_folder(
            folder_name="months", parent_folder_id=parent_folder_id
        )

        return year_folder_id

    def file_exist(
        self, file_name: str, parent_folder_id: str, folder: bool, page_size: int
    ) -> str | None:
        # if folder is False mimetype is Spreadsheet if not Folder
        file_mime_type: str = (
            "application/vnd.google-apps.folder"
            if folder
            else "application/vnd.google-apps.spreadsheet"
        )

        files_list: dict = self.client.list(
            q=f"name = '{file_name}' and mimeType = '{file_mime_type}' and '{parent_folder_id}' in parents and trashed = false",
            fields="files(id, name)",
            page_size=page_size,
        )

        files: dict[str, str] = files_list[0]

        # check if multiple files raise error
        if files:
            if len(files) > 1:
                print("folder/file has duplicate")
                raise ValueError(f"{folder}/{file_name} has duplicate")
            else:
                print(f"{folder}/{file_name} has duplicate")
                return files.get("id")

        return None

    # def if_miss_create_item(
    #     self,
    #     folder: None | str,
    #     name: FileName,
    #     parent_folder_id: str,
    #     sample_file_id: str,
    # ) -> str:
    #     if not folder:
    #         drive_file = self.create_year_folder(
    #             year=name.year,
    #             parent_folder_id=parent_folder_id,
    #             sample_file_id=sample_file_id,
    #             nested_file_name=name.name,
    #         )
    #         return drive_file["id"]
    #     return folder

    def list_folder_files(self, folder_id: str):
        self.client.list(
            q=f"'{folder_id}' in parents and trashed=false",
            page_size=30,
            fields="files(id, name, mimeType)",
        )
