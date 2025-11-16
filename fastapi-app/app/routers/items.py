"""
Роутер для работы с Items
"""
from fastapi import APIRouter, status
from typing import List
from app.schemas.items import (
    Item,
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemsListResponse
)
from app.services.items_service import ItemsService

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=ItemsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить все items",
    description="Возвращает список всех доступных items"
)
async def get_items() -> ItemsListResponse:
    """Получить все items"""
    items = ItemsService.get_all_items()
    return ItemsListResponse(
        items=items,
        total=len(items),
        message="Items retrieved successfully"
    )


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить item по ID",
    description="Возвращает информацию о конкретном item"
)
async def get_item(item_id: int) -> ItemResponse:
    """Получить item по ID"""
    item = ItemsService.get_item_by_id(item_id)
    return ItemResponse(
        item=item,
        message=f"Item {item_id} retrieved successfully"
    )


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый item",
    description="Создает новый item в системе"
)
async def create_item(item: ItemCreate) -> ItemResponse:
    """Создать новый item"""
    new_item = ItemsService.create_item(item)
    return ItemResponse(
        item=new_item,
        message="Item created successfully"
    )


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить item",
    description="Обновляет информацию о существующем item"
)
async def update_item(item_id: int, item_update: ItemUpdate) -> ItemResponse:
    """Обновить item"""
    updated_item = ItemsService.update_item(item_id, item_update)
    return ItemResponse(
        item=updated_item,
        message=f"Item {item_id} updated successfully"
    )


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить item",
    description="Удаляет item из системы"
)
async def delete_item(item_id: int) -> dict:
    """Удалить item"""
    return ItemsService.delete_item(item_id)

