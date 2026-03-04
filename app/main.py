from fastapi import FastAPI

from app.api.routers.router import api_router

app = FastAPI()
app.include_router(api_router)
