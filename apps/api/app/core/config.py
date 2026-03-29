from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "thinking-api"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/thinking"
    redis_url: str = "redis://localhost:6379/0"
    temporal_host: str = "localhost:7233"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
