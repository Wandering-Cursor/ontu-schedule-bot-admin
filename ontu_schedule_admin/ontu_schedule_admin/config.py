import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_prefix="app__",
        validate_default=True,
    )

    debug: bool = False
    security_key: str

    allowed_hosts: list[str] = [".localhost", "127.0.0.1", "[::1]", "backend", "backend:8000"]

    redis_url: pydantic.RedisDsn = pydantic.RedisDsn("redis://cache:6379/0")
    db_url: pydantic.PostgresDsn = pydantic.PostgresDsn(
        "postgresql://postgres:local@db:5432/postgres"
    )


app_settings = Settings()  # pyright: ignore[reportCallIssue]
