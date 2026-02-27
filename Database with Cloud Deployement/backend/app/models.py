from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category    = Column(String(100), default="general")
    completed   = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
