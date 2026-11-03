from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import RefreshSessionRepository
from gems_marketplace.models.models import RefreshSession


class SqlAlchemyRefSessionRepository(RefreshSessionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_jti(self, jti: str) -> RefreshSession | None:
        stmt = (
            select(RefreshSession)
            .where(RefreshSession.hashed_token == jti)
            .with_for_update()
        )

        result = await self.session.scalars(stmt)
        return result.one_or_none()

    async def add_in_db(self, ref_session: RefreshSession) -> None:
        return self.session.add(ref_session)
