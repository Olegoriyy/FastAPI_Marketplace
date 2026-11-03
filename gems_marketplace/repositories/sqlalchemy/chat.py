from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import ChatRepository
from gems_marketplace.models.models import Chat


class SqlalchemyChatRepository(ChatRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_in_db(self, chat: Chat) -> None:
        return self.session.add(chat)

    async def get_by_id(self, chat_id=int) -> Chat | None:

        return await self.session.get(Chat, chat_id)

    async def update(self, chat_id: int, chat_data=Chat) -> Chat | None: ...

    async def delete(self, chat: Chat) -> None:
        return await self.session.delete(chat)
