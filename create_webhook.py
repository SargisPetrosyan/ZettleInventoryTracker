from dotenv import load_dotenv
import os
import rich
import uuid
load_dotenv()

access_token: str | None = os.getenv(key="ACCESS_TOKEN")


import httpx

def create_subscription():
    data = {
    "uuid": "a195fb02-d765-11f0-9f7d-32a86d443d24",
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

# create_subscription()

def check_webhook():
    result: httpx.Response = httpx.get(
    url='https://pusher.izettle.com/organizations/self/subscriptions',
    headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    })
    rich.print(result.json())

check_webhook()