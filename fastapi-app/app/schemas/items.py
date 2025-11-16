"""
Схемы Pydantic для Items
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    """Базовая схема Item"""
    name: str = Field(..., min_length=1, max_length=100, description="Название товара")
    description: Optional[str] = Field(None, max_length=500, description="Описание товара")
    price: float = Field(..., gt=0, description="Цена товара")
    is_available: bool = Field(True, description="Доступность товара")


class ItemCreate(ItemBase):
    """Схема для создания Item"""
    pass


class ItemUpdate(BaseModel):
    """Схема для обновления Item"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None


class Item(ItemBase):
    """Схема Item с ID"""
    id: int = Field(..., description="Уникальный идентификатор")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Пример товара",
                "description": "Описание товара",
                "price": 99.99,
                "is_available": True,
                "created_at": "2024-01-01T00:00:00"
            }
        }


class ItemResponse(BaseModel):
    """Схема ответа для Item"""
    item: Item
    message: str = "Item retrieved successfully"


class ItemsListResponse(BaseModel):
    """Схема ответа для списка Items"""
    items: list[Item]
    total: int
    message: str = "Items retrieved successfully"

