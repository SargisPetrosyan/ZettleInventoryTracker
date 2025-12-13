from typing import Any
from dotenv import load_dotenv
import os
import rich
from core.utils import ZettleCredsPathManager
from core.zettle.auth import ZettleCredentialsManager
load_dotenv()
import logging

logger: logging.Logger = logging.getLogger(name=__name__)


path_manager = ZettleCredsPathManager()
manager = ZettleCredentialsManager(path_manager=path_manager)

import httpx

class WebhookSubscriptionManager:
    def __init__(
            self, 
            access_token:str,
            uuid:str,
            events:list[str],
            destination_url:str,
            mail: str) -> None:
        self.access_token: str = access_token
        self.uuid: str = uuid
        self.events: list[str] = events
        self.destination_url:str = destination_url
        self.mail: str = mail

    def create_subscription(self,) -> None:
        data: dict[str,Any] = {
        "uuid": self.uuid,
        "transportName": "WEBHOOK",
        "eventNames": self.events,
        "destination": self.destination_url,
        "contactEmail": self.mail
        }
        logger.info("creating subscription")
        httpx.post(
            url='https://pusher.izettle.com/organizations/self/subscriptions',
            json=data,
            headers={
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })

    def check_webhook(self)   -> None:
        result: httpx.Response = httpx.get(
        url='https://pusher.izettle.com/organizations/self/subscriptions',
        headers={
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        })
        logger.info(msg=f"you have {len(result.json())}")
    
    def delete_webhook(self,subscription_uuid:str) -> None:
        logger.info(msg=f"deleting subscription")
        httpx.delete(
        url=f'https://pusher.izettle.com/organizations/self/subscriptions/{subscription_uuid}',
        headers={
            'Authorization': f'Bearer {self.access_token}',
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
        logger.info(msg=f"updating subscription")
        httpx.put(
        url=f'https://pusher.izettle.com/organizations/self/subscriptions/{subscription_uuid}',
        headers={
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        },
        json=data)


