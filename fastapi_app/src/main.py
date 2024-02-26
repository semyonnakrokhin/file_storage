import aioredis as aioredis
import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from fastapi_app.logging_config import LOGGING_CONFIG
from fastapi_app.src.config import DatabaseSettings, RedisSettings, merge_dicts
from fastapi_app.src.di_containers import AppContainer
from fastapi_app.src.router import router


def create_app() -> FastAPI:
    redis_settings = RedisSettings()
    db_settings = DatabaseSettings()
    log_settings_dict = LOGGING_CONFIG
    settings_dict = merge_dicts(
        {"database": db_settings.model_dump()}, {"logging": log_settings_dict}
    )

    container = AppContainer()
    container.config.from_dict(settings_dict)
    container.core.init_resources()
    container.wire(modules=["fastapi_app.src.router", "fastapi_app.src.dependencies"])

    redis = aioredis.from_url(url=redis_settings.url)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    app = FastAPI()
    app.container = container
    app.include_router(router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
