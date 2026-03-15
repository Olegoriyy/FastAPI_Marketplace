from fastapi import APIRouter

from gems_marketplace.api.routers import admin, auth, category, health, products, users

api_router = APIRouter()

api_router.include_router(health.health_router)
api_router.include_router(auth.auth_router)
api_router.include_router(users.users_router)
api_router.include_router(admin.admin_router)
api_router.include_router(products.products_router)
api_router.include_router(category.categories_router)
