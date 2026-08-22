from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración vía variables de entorno (ver .env.example)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://sport_api:sport_api@localhost:5432/sport_api"
    app_name: str = "sport-api"


settings = Settings()
