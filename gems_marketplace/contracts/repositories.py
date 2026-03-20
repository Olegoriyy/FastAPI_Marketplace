from abc import ABC, abstractmethod

from gems_marketplace.models.models import Category, Product, RefreshSession, Role, User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_name(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def add_in_db(self, user: User) -> None: ...

    @abstractmethod
    async def delete(self, user: User) -> None: ...


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
    async def get_by_jti(self, jti: int) -> RefreshSession | None: ...

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


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product | None: ...

    @abstractmethod
    async def add_in_db(self, product: Product) -> None: ...

    @abstractmethod
    async def list_by_category_id(
        self, category_id: int, limit: int, published: bool
    ) -> list[Product]: ...

    @abstractmethod
    async def list_by_seller_id(
        self, seller_id: int, limit: int, published: bool
    ) -> list[Product]: ...

    @abstractmethod
    async def delete(self, product: Product) -> None: ...
