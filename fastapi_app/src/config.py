import os
from pprint import pprint
from typing import Dict

from pydantic_settings import BaseSettings, SettingsConfigDict

from fastapi_app.logging_config import LOGGING_CONFIG

_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(_root_dir, ".env"), extra="allow"
    )

    mode: str
    db_host: str
    db_port: str
    db_user: str
    db_pass: str
    db_name: str

    def __init__(self, **data):
        super().__init__(**data)
        self.dsn = self.async_postgres_dsn

    @property
    def async_postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg"
            f"://{self.db_user}"
            f":{self.db_pass}@{self.db_host}"
            f":{self.db_port}/{self.db_name}"
        )


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(_root_dir, ".env.redis"), extra="allow"
    )

    redis_host: str
    redis_port: str
    redis_db: str

    def __init__(self, **data):
        super().__init__(**data)
        self.url = self.redis_url

    @property
    def redis_url(self) -> str:
        return f"redis" f"://{self.redis_host}" f":{self.redis_port}/{self.redis_db}"


def merge_dicts(*dicts: Dict) -> Dict:
    merged = {}
    for d in dicts:
        for key, value in d.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = merge_dicts(merged[key], value)
            else:
                merged[key] = value
    return merged


if __name__ == "__main__":
    db_settings = DatabaseSettings()
    log_settings_dict = LOGGING_CONFIG
    settings_dict = merge_dicts(
        {"database": db_settings.model_dump()}, {"logging": log_settings_dict}
    )

    redis_settings = RedisSettings()
    pprint(settings_dict)
    print(redis_settings.url)
