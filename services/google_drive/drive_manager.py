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
        sample_file_id: str,
        nested_file_name: str,
    ):
        # create year folder
        year_folder = self.client.create_folder(
            folder_name=year, parent_folder_id=parent_folder_id
        )
        year_folder_id = year_folder["id"]

        # create nested month folder
        self.client.create_folder(folder_name="months", parent_folder_id=year_folder_id)

        # copy month file sample
        return self.client.copy(
            file_id=sample_file_id,
            parent_folder_id=year_folder_id,
            file_name=nested_file_name,
        )

    def file_exist(
        self, file_name: str, parent_folder_id: str, folder: bool, page_size: int
    ) -> None | str:
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

        files: list[dict[str, str]] = files_list.get("files")

        # check if multiple files raise error
        if files:
            if len(files) > 1:
                print("folder/file has duplicate")
                raise ValueError(f"{folder}/{file_name} has duplicate")
            else:
                print(f"{folder}/{file_name} has duplicate")
                return files[0]["id"]

        return None

    def if_miss_create_folder(
        self,
        folder: None | dict[str, str],
        name: FileName,
        parent_folder_id: str,
        sample_file_id: str,
    ):
        if not folder:
            drive_file = self.create_year_folder(
                year=name.year,
                parent_folder_id=parent_folder_id,
                sample_file_id=sample_file_id,
                nested_file_name=name.name,
            )
            return drive_file.get("id")
        return folder.get("id")
