import httpx
import rich
from core.zettle.auth import ZettleCredentialsManager
from datetime import datetime, timedelta


class PurchasesService:
    def __init__(self, shop_name:str,) -> None:
        self.creds_manager: ZettleCredentialsManager = ZettleCredentialsManager(shop_name=shop_name)

    def get_purchases(self,time_interval_hours:int) -> dict:
        access_token: str = self.creds_manager.get_access_token()
        end_date: datetime = datetime.now()
        start_date: datetime = end_date - timedelta(hours=time_interval_hours)
        result: httpx.Response = httpx.get(
            url=f'https://purchase.izettle.com/purchases/v2',
            params = {
                "startDate":start_date.isoformat(),
                "endDate":end_date.isoformat(),
            },
            headers={
                'Authorization': f'Bearer {access_token}',
            },
        )
        return result.json()

    