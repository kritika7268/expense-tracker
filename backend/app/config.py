import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Expensely API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database URL default: MySQL, with graceful SQLite fallback if MySQL is unreachable
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/expense_tracker"
    )
    
    # JWT & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_jwt_key_expensely_production_style_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
