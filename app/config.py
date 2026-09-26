from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://user:password@postgres:5432/booking_db"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "supersecretkey_change_me_in_production"
    JWT_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
