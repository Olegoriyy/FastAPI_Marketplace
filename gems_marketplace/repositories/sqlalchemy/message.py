from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import MessageRepository
from gems_marketplace.models.models import Message


class SqlalchemyMessageRepository(MessageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_in_db(self, message: Message) -> None:
        return self.session.add(message)

    async def get_by_id(self, message_id=int) -> Message | None:
        return await self.session.get(Message, message_id)

    async def get_all_by_chat_id(self, chat_id) -> list[Message]:
        stmt = select(Message).where(Message.chat_id == chat_id)

        result = await self.session.scalars(stmt)

        return list(result.all())

    async def get_any_last_messages_by_chat_id(
        self, chat_id: int, limit: int
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        result = await self.session.scalars(stmt)

        return list(result.all())

    async def update(self, message_id: int, message_data=Message) -> Message | None: ...

    async def delete(self, message: Message) -> None:

        return await self.session.delete(message)
