from fastapi import APIRouter

from app.api.routers import auth, health, users

api_router = APIRouter()

api_router.include_router(health.health_router)
api_router.include_router(auth.auth_router)
api_router.include_router(users.users_router)
