import math
from typing import Any
from dotenv import load_dotenv
import os
from abc import abstractmethod,ABC
import rich
import logging

import httpx

from core.utils import CredentialContext
from core.zettle.auth import ZettleCredentialsManager
load_dotenv()


logger: logging.Logger = logging.getLogger(name=__name__)

class WebhookManager(ABC):

    @abstractmethod
    def create_subscription(self)-> None:
        raise NotImplementedError
    
    @abstractmethod
    def check_subscription(self)-> None:
        raise NotImplementedError
    
    @abstractmethod
    def delete_subscription(self)-> None:
        raise NotImplementedError
    
    @abstractmethod
    def update_subscription(self,)-> None:
        raise NotImplementedError

class WebhookSubscriptionManager(WebhookManager):
    def __init__(self, shop_name:str) -> None:
        self.shop_name:str = shop_name
        self.creds_manager: ZettleCredentialsManager = ZettleCredentialsManager(shop_name=self.shop_name)
        self.credential_context = CredentialContext(shop_name=shop_name)

    def create_subscription(self) -> None:
        access_token: str = self.creds_manager.get_access_token()
        data: dict[str,Any] = {
        "uuid": self.credential_context.subscription_uuid,
        "transportName": "WEBHOOK",
        "eventNames": self.credential_context.events,
        "destination": self.credential_context.destination_url,
        "contactEmail": self.credential_context.mail,
        }
        logger.info(msg="creating subscription")
        response: httpx.Response = httpx.post(
            url='https://pusher.izettle.com/organizations/self/subscriptions/',
            json=data,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })
        logger.info(msg=f"created subscription for shop {self.shop_name} response : {response.json()}")

    def check_subscription(self)   -> None:
        access_token: str = self.creds_manager.get_access_token()
        result: httpx.Response = httpx.get(
        url='https://pusher.izettle.com/organizations/self/subscriptions',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })
        logger.info(msg=f"subscriptions for {self.shop_name} count:{len(result.json())} data: {result.json()}")

    
    def delete_subscription(self) -> None:
        access_token: str = self.creds_manager.get_access_token()
        logger.info(msg=f"deleting subscription")
        response = httpx.delete(
        url=f'https://pusher.izettle.com/organizations/self/subscriptions/{self.credential_context.subscription_uuid}',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })
        logger.info(f"deleted shop {self.shop_name} subscription response {response.json()}")


    def update_subscription(self ) -> None:
        access_token: str = self.creds_manager.get_access_token()
        data: dict[str,Any] = {
        "eventNames": self.credential_context.events,
        "destination": self.credential_context.destination_url,
        "contactEmail": self.credential_context.mail,
    }
        logger.info(msg=f"updating subscription")
        response: httpx.Response = httpx.put(
        url=f'https://pusher.izettle.com/organizations/self/subscriptions/{self.credential_context.subscription_uuid}',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        json=data)

        logger.info(f"updated Dala shop subscription{response.json()}")
