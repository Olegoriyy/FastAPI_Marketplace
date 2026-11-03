from fastapi import FastAPI

from gems_marketplace.api.routers.router import api_router
from gems_marketplace.core.lifespan import lifespan

gems_marketplace = FastAPI(lifespan=lifespan)
gems_marketplace.include_router(api_router)
