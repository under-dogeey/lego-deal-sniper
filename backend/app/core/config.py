from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    brickset_api_key: str
    ebay_client_id: str
    ebay_client_secret: str
    database_url: str
    discord_webhook_url: str | None = None
    ntfy_topic: str | None = None
    health_checks_url: str | None = None


settings = Settings()
