from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "skillseed-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite+aiosqlite:///./skillseed.db"
    UPLOAD_DIR: str = "uploads"
    MAX_VIDEO_SIZE_MB: int = 500
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"

settings = Settings()
