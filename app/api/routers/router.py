from fastapi import APIRouter

from app.api.routers import admin, auth, health, users

api_router = APIRouter()

api_router.include_router(health.health_router)
api_router.include_router(auth.auth_router)
api_router.include_router(users.users_router)
api_router.include_router(admin.admin_router)
