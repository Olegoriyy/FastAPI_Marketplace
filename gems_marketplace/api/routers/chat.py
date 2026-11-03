from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket

from gems_marketplace.dependencies import (
    get_chat_service,
    get_curent_user_from_token,
    get_current_ws_user,
    get_Message_service,
)
from gems_marketplace.models.models import User
from gems_marketplace.services.chat_service import ChatService
from gems_marketplace.services.message_service import MessageService

chat_router = APIRouter(tags=["chats"])


@chat_router.websocket("/chats/{chat_id}/ws")
async def chat_websocket(
    websocket: WebSocket,
    chat_id: int,
    user: Annotated[User, Depends(get_current_ws_user)],
    message_service: Annotated[MessageService, Depends(get_Message_service)],
):
    await message_service.communicate(
        websocket=websocket, chat_id=chat_id, user_id=user.id
    )


@chat_router.post("/chats/seller")
async def create_seller_chat(
    buyer: Annotated[User, Depends(get_curent_user_from_token)],
    seller_id: int,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    chat = await chat_service.create_chat_with_seller_without_product(
        buyer_id=buyer.id,
        seller_id=seller_id,
    )
    return {"chat_id": chat.id}


@chat_router.post("/chats/support")
async def create_support_chat(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    chat = await chat_service.create_support_chat(user_id=user.id)
    return {"chat_id": chat.id}


@chat_router.post("/chats/ai")
async def create_ai_chat(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    chat = await chat_service.create_ai_support_chat(user_id=user.id)
    return {"chat_id": chat.id}


@chat_router.post("/chats/{chat_id}/close", status_code=204)
async def close_chat(
    chat_id: int,
    user: Annotated[User, Depends(get_curent_user_from_token)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> None:
    await chat_service.close_chat(chat_id=chat_id, user_id=user.id)
