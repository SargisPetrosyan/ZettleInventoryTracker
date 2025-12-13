from typing import Any
from dotenv import load_dotenv
import os
import rich
from core.utils import ZettleCredsPathManager
from core.zettle.auth import ZettleCredentialsManager
load_dotenv()

path_manager = ZettleCredsPathManager()
manager = ZettleCredentialsManager(path_manager=path_manager)

access_token:str = manager.get_access_token()
uuid:str | None = os.getenv(key="ZETTLE_UUID")

import httpx

class WebhookSubscriptionManager:
    def create_subscription(self) -> None:
        data: dict[str,Any] = {
        "uuid": uuid,
        "transportName": "WEBHOOK",
        "eventNames": ["InventoryBalanceChanged"],
        "destination": "https://9230d61a116e.ngrok-free.app/store_inventory_data_webhook",
        "contactEmail": "saqomax@gmail.com"
    }


        result: httpx.Response = httpx.post(
            url='https://pusher.izettle.com/organizations/self/subscriptions',
            json=data,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })
        rich.print(result.json())

    def check_webhook(self)  :
        result: httpx.Response = httpx.get(
        url='https://pusher.izettle.com/organizations/self/subscriptions',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })
        return result.json()
    
    def delete_webhook(self,subscription_uuid:str) -> None:
        httpx.delete(
        url=f'https://pusher.izettle.com/organizations/self/subscriptions/{subscription_uuid}',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })

    def update_subscription(
            self,
            subscription_uuid:str,
            mail:str,
            destination_url:str, 
            events:list[str]) -> None:
        data: dict[str,Any] = {
        "eventNames": events,
        "destination": destination_url,
        "contactEmail": mail,
    }
        httpx.put(
        url=f'https://pusher.izettle.com/organizations/self/subscriptions/{subscription_uuid}',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        json=data)


