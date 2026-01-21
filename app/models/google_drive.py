from pydantic import BaseModel

class Updates(BaseModel):
    updatedRange: str 

class RowEditResponse(BaseModel):
    spreadsheetId: str
    updates:Updates
