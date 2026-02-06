from datetime import datetime, timedelta
from app.constants import ART_AND_CRAFT_NAME, CAFE_NAME, DALA_SHOP_NAME, HOUR_INTERVAL
from app.core.config import Database
from app.db.schemes import InventoryUpdateRepository
from app.google_drive.client import GoogleDriveClient, SpreadSheetClient
from app.google_drive.context import Context
from app.google_drive.drive_data_updayer import DriveSpreadsheetUpdater
from app.google_drive.drive_manager import GoogleDriveFileManager
from app.google_drive.services import DriveFileStructureEnsurer
from app.google_drive.sheet_manager import SpreadSheetFileManager
from app.models.product import PaypalProductData, ProductData
from app.zettle.services import InventoryManualDataCollector

class HourlyWorkflowRunner:
    def __init__(self,engine:Database) -> None:
        self.engine: Database = engine
        self.shops = (DALA_SHOP_NAME)
        self.google_drive_client = GoogleDriveClient()
        self.spreadsheet_file_client = SpreadSheetClient()
        self.google_drive_file_manager = GoogleDriveFileManager(client=self.google_drive_client)
        self.spreadsheet_manager = SpreadSheetFileManager(client=self.spreadsheet_file_client)

    def run(self):
        # start_date: datetime = datetime.now()
        # end_date: datetime = start_date -timedelta(hours=HOUR_INTERVAL)

        start_date: datetime = datetime.strptime("2026-01-13 10:00:00","%Y-%m-%d %H:%M:%S")
        end_date: datetime = datetime.strptime("2026-01-13 20:01:18","%Y-%m-%d %H:%M:%S")

        repo_updater: InventoryUpdateRepository = InventoryUpdateRepository(engine=self.engine)

        
        for name in self.shops:
            manual_collector = InventoryManualDataCollector(
                start_date= start_date, 
                end_date= end_date, 
                repo_updater=repo_updater,
                shop_name=name)

            # step 1 filter changed product data
            list_of_manual_products: list[PaypalProductData] | None = manual_collector.get_manual_changed_products()

            if not list_of_manual_products:
                continue

            context =Context(product=list_of_manual_products)

            # step 2 check if google drive hade proper file structure
            drive_file_ensurer = DriveFileStructureEnsurer(
                google_drive_file_manager=self.google_drive_file_manager,
                spreadsheet_file_manager=self.spreadsheet_manager)
            
            drive_file_ensurer.ensure_drive_file_structure(context=context)
            drive_file_updater = DriveSpreadsheetUpdater(context=context)
            drive_file_updater.process_data_to_worksheet(products=list_of_manual_products)


        