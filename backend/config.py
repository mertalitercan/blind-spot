from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    MODEL_NAME: str = "claude-haiku-4-5-20251001"
    CHAT_MODEL_NAME: str = "claude-sonnet-4-20250514"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
