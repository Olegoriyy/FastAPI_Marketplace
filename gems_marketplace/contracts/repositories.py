from abc import ABC, abstractmethod

from gems_marketplace.models.models import (
    Category,
    Chat,
    Message,
    Product,
    RefreshSession,
    Role,
    User,
)


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def add_in_db(self, user: User) -> None: ...

    @abstractmethod
    async def delete(self, user: User) -> None: ...

    @abstractmethod
    async def get_all_by_role(self, role: str) -> list[User] | None: ...


class RoleRepository(ABC):
    @abstractmethod
    async def get_by_id(self, role_id: int) -> Role | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None: ...

    @abstractmethod
    async def add_in_db(self, role: Role) -> None: ...

    @abstractmethod
    async def delete(self, role: Role) -> None: ...


class RefreshSessionRepository(ABC):
    @abstractmethod
    async def get_by_jti(self, jti: str) -> RefreshSession | None: ...

    @abstractmethod
    async def add_in_db(self, ref_session: RefreshSession) -> None: ...


class CategoryRepository(ABC):
    @abstractmethod
    async def add_in_db(self, category: Category) -> None: ...

    @abstractmethod
    async def get_by_id(self, category_id: int) -> Category | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Category | None: ...

    @abstractmethod
    async def get_list_all(self) -> list[Category]: ...

    @abstractmethod
    async def update(self, category_id: int, name: str) -> Category | None: ...

    @abstractmethod
    async def delete(self, category_id: int): ...


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product | None: ...

    @abstractmethod
    async def add_in_db(self, product: Product) -> None: ...

    @abstractmethod
    async def list_by_category_id(
        self,
        category_id: int,
        limit: int,
        published: bool,
        all: bool,
    ) -> list[Product]: ...

    @abstractmethod
    async def list_by_seller_id(
        self,
        seller_id: int,
        limit: int,
        published: bool,
    ) -> list[Product]: ...

    @abstractmethod
    async def list_all_products(self) -> list[Product]: ...

    @abstractmethod
    async def update(self, product_id: int, data: dict) -> Product | None: ...

    @abstractmethod
    async def delete(self, product: Product) -> None: ...


class ChatRepository(ABC):
    @abstractmethod
    async def add_in_db(self, chat: Chat) -> None: ...

    @abstractmethod
    async def get_by_id(self, chat_id: int) -> Chat | None: ...

    @abstractmethod
    async def update(self, chat_id: int, chat_data=Chat) -> Chat | None: ...

    @abstractmethod
    async def delete(self, chat: Chat) -> None: ...


class MessageRepository(ABC):
    @abstractmethod
    async def add_in_db(self, message: Message) -> None: ...

    @abstractmethod
    async def get_by_id(self, message_id=int) -> Message | None: ...

    @abstractmethod
    async def update(self, message_id: int, message_data=Message) -> Message | None: ...

    @abstractmethod
    async def delete(self, message: Message) -> None: ...

    @abstractmethod
    async def get_all_by_chat_id(self, chat_id) -> list[Message]: ...

    @abstractmethod
    async def get_any_last_messages_by_chat_id(
        self, chat_id: int, limit: int
    ) -> list[Message]: ...
