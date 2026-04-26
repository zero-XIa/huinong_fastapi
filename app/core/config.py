from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    DIFY_API_BASE_URL: str = "https://api.dify.ai/v1"
    DIFY_API_KEY: str = ""
    secret_key: str = "dev-secret-key-change-in-production"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()