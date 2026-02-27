from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Item
from app.schemas import ItemCreate, ItemUpdate


async def get_items(db: AsyncSession, skip: int = 0, limit: int = 50,
                    category: str = None, completed: bool = None):
    query = select(Item)
    if category:
        query = query.where(Item.category == category)
    if completed is not None:
        query = query.where(Item.completed == completed)
    query = query.offset(skip).limit(limit).order_by(Item.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def count_items(db: AsyncSession):
    result = await db.execute(select(func.count()).select_from(Item))
    return result.scalar()


async def get_item(db: AsyncSession, item_id: int):
    result = await db.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()


async def create_item(db: AsyncSession, item: ItemCreate):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def update_item(db: AsyncSession, item_id: int, item: ItemUpdate):
    db_item = await get_item(db, item_id)
    if not db_item:
        return None
    for key, val in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, val)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def delete_item(db: AsyncSession, item_id: int) -> bool:
    db_item = await get_item(db, item_id)
    if not db_item:
        return False
    await db.delete(db_item)
    await db.commit()
    return True
