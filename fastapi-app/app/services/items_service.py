"""
Сервисный слой для работы с Items
Содержит бизнес-логику приложения
"""
from typing import List, Optional
from fastapi import HTTPException, status
from app.schemas.items import Item, ItemCreate, ItemUpdate
from app.core.database import Database


class ItemsService:
    """Сервис для работы с Items"""
    
    @staticmethod
    def get_all_items() -> List[Item]:
        """Получить все items"""
        return Database.get_all_items()
    
    @staticmethod
    def get_item_by_id(item_id: int) -> Item:
        """Получить item по ID"""
        item = Database.get_item_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        return item
    
    @staticmethod
    def create_item(item_data: ItemCreate) -> Item:
        """Создать новый item"""
        # Здесь можно добавить бизнес-логику (валидация, проверки и т.д.)
        if item_data.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price must be greater than 0"
            )
        
        return Database.create_item(item_data)
    
    @staticmethod
    def update_item(item_id: int, item_update: ItemUpdate) -> Item:
        """Обновить item"""
        # Проверяем существование
        existing_item = Database.get_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        
        # Валидация цены если она обновляется
        if item_update.price is not None and item_update.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price must be greater than 0"
            )
        
        updated_item = Database.update_item(item_id, item_update)
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        
        return updated_item
    
    @staticmethod
    def delete_item(item_id: int) -> dict:
        """Удалить item"""
        # Проверяем существование
        existing_item = Database.get_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        
        success = Database.delete_item(item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        
        return {"message": f"Item {item_id} deleted successfully"}

