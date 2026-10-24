from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict
from sqlalchemy import URL
from pydantic import SecretStr

class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    JWT_SECRET_KEY :SecretStr
    JWT_ALGORITHM :str ="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> URL:
        return URL.create(
            "postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT, 
            database=self.DB_NAME
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()
