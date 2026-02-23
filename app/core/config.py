from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL_NAME: str = "gemini-3-flash-preview"
    API_REQUEST_DELAY: float = 0.5

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()