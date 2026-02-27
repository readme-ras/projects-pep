from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ItemCreate, ItemUpdate, ItemOut, ItemList
from app import crud

router = APIRouter()


@router.get("", response_model=ItemList)
async def list_items(
    skip:      int            = Query(default=0, ge=0),
    limit:     int            = Query(default=50, le=200),
    category:  Optional[str]  = Query(default=None),
    completed: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    items = await crud.get_items(db, skip, limit, category, completed)
    total = await crud.count_items(db)
    return ItemList(items=items, total=total)


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=ItemOut, status_code=201)
async def create_item(body: ItemCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_item(db, body)


@router.patch("/{item_id}", response_model=ItemOut)
async def update_item(item_id: int, body: ItemUpdate, db: AsyncSession = Depends(get_db)):
    item = await crud.update_item(db, item_id, body)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    if not await crud.delete_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
