from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 这里的变量名必须与 .env 中的 Key 一致
    DATABASE_URL: str
    DIFY_API_BASE_URL: str = "https://api.dify.ai/v1"
    DIFY_API_KEY: str = ""
    
    # Pydantic 自动处理 .env 读取
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()