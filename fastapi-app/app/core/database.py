"""
Модуль для работы с базой данных
Пока используется in-memory хранилище, можно расширить для реальной БД
"""
from typing import Dict, List, Optional
from app.schemas.items import ItemCreate, ItemUpdate, Item


# In-memory хранилище (для примера)
# В production можно заменить на реальную БД (PostgreSQL, MongoDB и т.д.)
_items_db: Dict[int, Item] = {}
_next_id: int = 1


class Database:
    """Класс для работы с данными"""
    
    @staticmethod
    def get_all_items() -> List[Item]:
        """Получить все items"""
        return list(_items_db.values())
    
    @staticmethod
    def get_item_by_id(item_id: int) -> Optional[Item]:
        """Получить item по ID"""
        return _items_db.get(item_id)
    
    @staticmethod
    def create_item(item: ItemCreate) -> Item:
        """Создать новый item"""
        global _next_id
        new_item = Item(
            id=_next_id,
            name=item.name,
            description=item.description,
            price=item.price,
            is_available=item.is_available
        )
        _items_db[_next_id] = new_item
        _next_id += 1
        return new_item
    
    @staticmethod
    def update_item(item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """Обновить item"""
        if item_id not in _items_db:
            return None
        
        existing_item = _items_db[item_id]
        update_data = item_update.model_dump(exclude_unset=True)
        updated_item = existing_item.model_copy(update=update_data)
        _items_db[item_id] = updated_item
        return updated_item
    
    @staticmethod
    def delete_item(item_id: int) -> bool:
        """Удалить item"""
        if item_id in _items_db:
            del _items_db[item_id]
            return True
        return False
    
    @staticmethod
    def clear_all() -> None:
        """Очистить все items (для тестирования)"""
        global _next_id
        _items_db.clear()
        _next_id = 1

