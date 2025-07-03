from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference # type: ignore[import-untyped]

from app.api.routers.auth import auth_router
from app.api.routers.food import food_router
from app.api.routers.roles import roles_router
from app.api.routers.users import users_router
from app.api.routers.utils import utils_router
from app.core.container import DIContainer
from app.database.initializer import init_db, seed_db
from app.middlewares import *


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    seed_db()
    yield


container = DIContainer()

app = FastAPI(
    lifespan=lifespan, 
    title="Kalorie Tracker API",
    middleware=[BearerTokenAuthenticationMiddleware], 
    debug=container.app_settings().DEBUG
)

app.include_router(auth_router)
app.include_router(food_router)
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(utils_router)


@app.get("/scalar", include_in_schema=False)
def scalar_html() -> Any:
    return get_scalar_api_reference(
        openapi_url=app.openapi_url, # pyright: ignore
        title=app.title,
    )
