from typing import Annotated

from fastapi import Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import (
    CategoryRepository,
    ProductRepository,
    RefreshSessionRepository,
    RoleRepository,
    UserRepository,
)
from gems_marketplace.core.security.jwt_auth import (
    check_and_decode_access_token,
    oauth2_scheme,
)
from gems_marketplace.db.deps import get_session_tx
from gems_marketplace.models.models import User
from gems_marketplace.repositories.sqlalchemy.categories import (
    SqlalchemyCategoryRepository,
)
from gems_marketplace.repositories.sqlalchemy.products import (
    SqlalchemyProductRepository,
)
from gems_marketplace.repositories.sqlalchemy.refresh_sessions import (
    SqlAlchemyRefSessionRepository,
)
from gems_marketplace.repositories.sqlalchemy.roles import (
    SqlAlchemyRoleRepository,
)
from gems_marketplace.repositories.sqlalchemy.users import (
    SqlalchemyUserRepository,
)
from gems_marketplace.services.admin_services import AdminService
from gems_marketplace.services.auth_service import AuthService
from gems_marketplace.services.category_service import CategoryService
from gems_marketplace.services.product_service import ProductService
from gems_marketplace.services.role_service import RoleService
from gems_marketplace.services.user_service import UserService


####### repositories dependencies
async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> SqlalchemyUserRepository:
    return SqlalchemyUserRepository(session)


async def get_role_repository(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> SqlAlchemyRoleRepository:
    return SqlAlchemyRoleRepository(session)


async def get_ref_session_repository(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> SqlAlchemyRefSessionRepository:
    return SqlAlchemyRefSessionRepository(session)


async def get_category_repository(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> SqlalchemyCategoryRepository:
    return SqlalchemyCategoryRepository(session)


async def get_product_repository(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> SqlalchemyProductRepository:
    return SqlalchemyProductRepository(session)


####### services dependencies
async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
    ref_session_repo: Annotated[
        RefreshSessionRepository, Depends(get_ref_session_repository)
    ],
) -> AuthService:
    return AuthService(
        session=session,
        user_repo=user_repo,
        role_repo=role_repo,
        ref_session_repo=ref_session_repo,
    )


async def get_category_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    category_repo: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> CategoryService:
    return CategoryService(
        session=session,
        category_repo=category_repo,
    )


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(session=session, user_repo=user_repo)


async def get_product_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    product_repo: Annotated[ProductRepository, Depends(get_product_repository)],
) -> ProductService:
    return ProductService(session=session, product_repo=product_repo)


async def get_role_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
) -> RoleService:
    return RoleService(session=session, role_repo=role_repo)


async def get_admin_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> AdminService:
    return AdminService(
        session=session,
        user_service=user_service,
        role_service=role_service,
    )


######################## trash=)
async def requred_admin_role(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> bool:
    user = await auth_service.check_and_get_user_by_token(token)
    user_role = await role_service.get_by_id(user.role_id)
    if user_role.name != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        return True


async def requred_seller_role(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> bool:
    user = await auth_service.check_and_get_user_by_token(token)
    user_role = await role_service.get_by_id(user.role_id)
    if user_role.name != "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        return True


async def get_curent_user_from_token(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    payload = check_and_decode_access_token(token)
    user = await session.get(User, payload["user_id"])
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    return user


async def get_user_by_user_id_from_body(
    user_id: Annotated[int, Body(embed=True)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return await user_service.get_by_id(user_id)
