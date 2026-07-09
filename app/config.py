from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    secret_key: str
    database_url: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    cookie_secure: bool = True
    cookie_samesite: str = "lax"
    model_config = SettingsConfigDict(env_file = ".env")

settings = Settings()