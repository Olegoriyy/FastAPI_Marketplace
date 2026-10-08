from fastapi import FastAPI

from gems_marketplace.api.routers.router import api_router

gems_marketplace = FastAPI()
gems_marketplace.include_router(api_router)
