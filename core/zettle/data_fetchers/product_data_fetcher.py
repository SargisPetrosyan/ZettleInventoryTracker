import httpx
import rich
from core.zettle.auth import ZettleCredentialsManager


class ProductDataFetcher:
    def __init__(self, shop_name:str,) -> None:
        self.creds_manager: ZettleCredentialsManager = ZettleCredentialsManager(shop_name=shop_name)

    def get_product_data(self,product_uuid:str,organization_uuid:str)  -> bytes:
        access_token: str = self.creds_manager.get_access_token()
        response: httpx.Response = httpx.get(
        url=f'https://products.izettle.com/organizations/{organization_uuid}/products/{product_uuid}',
        headers={
            'Authorization': f'Bearer {access_token}',
        })
        response.raise_for_status()
        return response.json()

    