from datetime import datetime, timezone
from random import choice

from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import ChatRepository, MessageRepository
from gems_marketplace.models.models import Chat
from gems_marketplace.services.message_service import MessageService
from gems_marketplace.services.role_service import RoleService
from gems_marketplace.services.user_service import UserService


class ChatService:
    def __init__(
        self,
        session: AsyncSession,
        chat_repo: ChatRepository,
        user_service: UserService,
        role_service: RoleService,
        message_repo: MessageRepository,
        message_service: MessageService,
    ) -> None:
        self.chat_repo = chat_repo
        self.session = session
        self.user_service = user_service
        self.role_service = role_service
        self.message_repo = message_repo
        self.message_service = message_service

    # chat types ["ai","support","seller","ai,support"]
    async def create_ai_support_chat(self, user_id: int) -> Chat:
        chat = Chat(
            type="ai",
            product_id=None,
            first_user_id=user_id,
            second_user_id=None,
        )

        await self.chat_repo.add_in_db(chat)
        await self.session.flush()
        await self.session.refresh(chat)
        return chat

    async def create_support_chat(self, user_id: int) -> Chat:

        support_role = await self.role_service.get_by_name("support")
        all_supports = await self.user_service.get_all_by_role(role=support_role.name)

        random_support = choice(all_supports)

        chat = Chat(
            type="support",
            product_id=None,
            first_user_id=user_id,
            second_user_id=random_support.id,
        )
        await self.chat_repo.add_in_db(chat)
        await self.session.flush()
        await self.session.refresh(chat)
        return chat

    async def create_chat_with_seller_without_product(
        self, buyer_id: int, seller_id: int
    ) -> Chat:

        if buyer_id == seller_id:
            raise HTTPException(400, "Нельзя создать чат с самим собой")

        seller = await self.user_service.get_by_id(seller_id)
        seller_role = await self.role_service.get_by_id(seller.role_id)

        if not seller.is_active or seller_role.name != "seller":
            raise HTTPException(
                400,
                "Пользователь не является активным продавцом",
            )

        chat = Chat(
            type="seller",
            product_id=None,
            first_user_id=buyer_id,
            second_user_id=seller_id,
        )
        await self.chat_repo.add_in_db(chat)
        await self.session.flush()
        await self.session.refresh(chat)
        return chat

    async def get_by_id(self, user_id: int, chat_id: int):

        chat = await self.chat_repo.get_by_id(chat_id=chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")

        chat_users = [chat.first_user_id, chat.second_user_id]
        if user_id not in chat_users:
            raise HTTPException(status_code=403, detail="Not enough permission")

        return chat

    async def close_chat(self, chat_id: int, user_id: int) -> None:

        chat = await self.get_by_id(user_id=user_id, chat_id=chat_id)

        if chat.closed_at is None:
            chat.closed_at = datetime.now(timezone.utc)

        await self.session.commit()
