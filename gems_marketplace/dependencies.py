from typing import Annotated

from fastapi import Body, Depends, HTTPException, WebSocket, WebSocketException
from fastapi.security.utils import get_authorization_scheme_param
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import AsyncQdrantClient
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.config import settings
from gems_marketplace.contracts.repositories import (
    CategoryRepository,
    ChatRepository,
    MessageRepository,
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
from gems_marketplace.repositories.sqlalchemy.chat import SqlalchemyChatRepository
from gems_marketplace.repositories.sqlalchemy.message import SqlalchemyMessageRepository
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
from gems_marketplace.services.ai_service import AiService
from gems_marketplace.services.auth_service import AuthService
from gems_marketplace.services.category_service import CategoryService
from gems_marketplace.services.chat_service import ChatService
from gems_marketplace.services.message_service import MessageService
from gems_marketplace.services.product_service import ProductService
from gems_marketplace.services.role_service import RoleService
from gems_marketplace.services.seller_service import SellerService
from gems_marketplace.services.user_service import UserService


async def get_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(url=settings.QDRANT_HOST, port=settings.QDRANT_PORT)


async def get_embeddings() -> Embeddings:
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,  # Модель для преобразования текста в числа
        api_key=settings.OPENROUTER_API_KEY,  # Ввод ключа при запуске
        base_url=settings.OPENROUTER_BASE_URL,
        check_embedding_ctx_length=False,  # Настройки совместимости с OpenRouter
        model_kwargs={"encoding_format": "float"},
    )


async def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.CHAT_MODEL,  # Название разговорной модели у твоего сервиса
        api_key=settings.OPENROUTER_API_KEY,  # Используй уже рабочий ключ
        base_url=settings.OPENROUTER_BASE_URL,  # Используй уже рабочий адрес
    )


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


async def get_chat_repository(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> SqlalchemyChatRepository:
    return SqlalchemyChatRepository(session)


async def get_message_repository(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> SqlalchemyMessageRepository:
    return SqlalchemyMessageRepository(session)


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
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
) -> UserService:
    return UserService(session=session, user_repo=user_repo, role_repo=role_repo)


async def get_role_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
) -> RoleService:
    return RoleService(session=session, role_repo=role_repo)


async def get_product_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    product_repo: Annotated[ProductRepository, Depends(get_product_repository)],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> ProductService:
    return ProductService(
        session=session,
        product_repo=product_repo,
        category_service=category_service,
        role_service=role_service,
    )


async def get_ai_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    qdrant_client: Annotated[AsyncQdrantClient, Depends(get_qdrant_client)],
    embeddings: Annotated[Embeddings, Depends(get_embeddings)],
    llm: Annotated[ChatOpenAI, Depends(get_llm)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> AiService:
    return AiService(
        session=session,
        qdrant_client=qdrant_client,
        embeddings=embeddings,
        llm=llm,
        collection_name=settings.QDRANT_COLLECTION,
        product_service=product_service,
    )


async def get_Message_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    chat_repo: Annotated[ChatRepository, Depends(get_chat_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
    message_repo: Annotated[MessageRepository, Depends(get_message_repository)],
    ai_service: Annotated[AiService, Depends(get_ai_service)],
) -> MessageService:
    return MessageService(
        session=session,
        chat_repo=chat_repo,
        user_repo=user_repo,
        role_repo=role_repo,
        message_repo=message_repo,
        ai_service=ai_service,
    )


async def get_chat_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    chat_repo: Annotated[ChatRepository, Depends(get_chat_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    message_repo: Annotated[MessageRepository, Depends(get_message_repository)],
    message_service: Annotated[MessageService, Depends(get_Message_service)],
) -> ChatService:
    return ChatService(
        session=session,
        chat_repo=chat_repo,
        user_service=user_service,
        role_service=role_service,
        message_repo=message_repo,
        message_service=message_service,
    )


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


async def get_seller_service(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> SellerService:
    return SellerService(
        session=session,
        product_service=product_service,
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


async def requred_seller_or_admin_role(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> bool:
    user = await auth_service.check_and_get_user_by_token(token)
    user_role = await role_service.get_by_id(user.role_id)
    if user_role.name in ("seller", "admin"):
        return True
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")


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


async def get_current_ws_user(
    websocket: WebSocket, session: Annotated[AsyncSession, Depends(get_session_tx)]
) -> User:

    authorization = websocket.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)

    if scheme.lower() != "bearer" or not token:
        raise WebSocketException(code=1008, reason="Unauthorized")

    try:
        payload = check_and_decode_access_token(token)
    except HTTPException as exc:
        raise WebSocketException(code=1008, reason="Unauthorized") from exc

    user_id = payload.get("user_id")

    if type(user_id) is not int or user_id <= 0:
        raise WebSocketException(code=1008, reason="Unauthorized")

    user = await session.get(User, user_id)

    if user is None or not user.is_active:
        raise WebSocketException(code=1008, reason="Unauthorized")

    return user
