from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.database.initializer import init_db, seed_db
from app.api.routers.food import food_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_db()
    yield


app = FastAPI(lifespan=lifespan, title="Kalorie Tracker API")
app.include_router(food_router)


@app.get("/scalar", include_in_schema=False)
def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url, # type: ignore
        title=app.title,
    )
