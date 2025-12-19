import httpx
from core.zettle.auth import ZettleCredentialsManager


class PurchasesFetcher:
    def __init__(self, shop_name:str,) -> None:
        self.creds_manager: ZettleCredentialsManager = ZettleCredentialsManager(shop_name=shop_name)

    def get_purchases(self,start_date:str, end_date:str) -> dict:
        access_token: str = self.creds_manager.get_access_token()
        response: httpx.Response = httpx.get(
            url=f'https://purchase.izettle.com/purchases/v2',
            params = {
                "startDate":start_date,
                "endDate":end_date,
            },
            headers={
                'Authorization': f'Bearer {access_token}',
            },
        )
        response.raise_for_status()

        return response.json()
    


    