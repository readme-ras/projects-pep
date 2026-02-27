from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    title:       str  = Field(..., min_length=1, max_length=200, example="Buy groceries")
    description: str  = Field(default="", example="Milk, eggs, bread")
    category:    str  = Field(default="general", example="shopping")
    completed:   bool = Field(default=False)


class ItemUpdate(BaseModel):
    title:       Optional[str]  = Field(None, min_length=1, max_length=200)
    description: Optional[str]  = None
    category:    Optional[str]  = None
    completed:   Optional[bool] = None


class ItemOut(BaseModel):
    id:          int
    title:       str
    description: str
    category:    str
    completed:   bool
    created_at:  datetime
    updated_at:  datetime

    model_config = {"from_attributes": True}


class ItemList(BaseModel):
    items: list[ItemOut]
    total: int
