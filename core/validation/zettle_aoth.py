from datetime import datetime
from pydantic import BaseModel

class ZettleAccessToken(BaseModel):
    access_token: str
    expiry: datetime

class ZettleCredentials(BaseModel):
    client_id: str
    key: str
    grant_type: str
    auth_url: str
    headers: str

class ZettleNewAccessToken(BaseModel):
    access_token: str