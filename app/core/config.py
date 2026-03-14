from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 这里的变量名必须与 .env 中的 Key 一致
    DATABASE_URL: str
    
    # Pydantic 自动处理 .env 读取
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()