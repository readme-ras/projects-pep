from datetime import datetime
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    description: str = ""

class Item(ItemCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
