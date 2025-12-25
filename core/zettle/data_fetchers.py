from datetime import datetime
from typing import Any
import httpx
from core.zettle.auth import ZettleCredentialsManager
from dotenv import load_dotenv

load_dotenv()

class PurchasesFetcher:
    def __init__(self, shop_name:str,) -> None:
        self.creds_manager: ZettleCredentialsManager = ZettleCredentialsManager(shop_name=shop_name)

    def get_purchases(self,start_date:datetime, end_date:datetime, descending: bool = False) -> dict[Any,Any]:
        access_token: str = self.creds_manager.get_access_token()
        response: httpx.Response = httpx.get(
            url=f'https://purchase.izettle.com/purchases/v2',
            params = {
                "startDate":start_date.isoformat(),
                "endDate":end_date.isoformat(),
                "descending":descending
            },
            headers={
                'Authorization': f'Bearer {access_token}',
            },
        )
        response.raise_for_status()

        return response.json()

class ProductDataFetcher:
    def __init__(self, shop_name:str,) -> None:
        self.creds_manager: ZettleCredentialsManager = ZettleCredentialsManager(shop_name=shop_name)
        

    def get_product_data(self,product_uuid:str, organization_id:str)  -> dict:
        access_token: str = self.creds_manager.get_access_token()
        response: httpx.Response = httpx.get(
        url=f'https://products.izettle.com/organizations/{organization_id}/products/{product_uuid}',
        headers={
            'Authorization': f'Bearer {access_token}',
        })
        response.raise_for_status()
        return response.json()



    