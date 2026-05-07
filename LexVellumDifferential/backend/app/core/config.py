from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    PROJECT_NAME: str = "LexVellum Differential"
    VERSION: str = "0.1.0"
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "lexvellumlaws"
    PINECONE_ENVIRONMENT: str = "us-east-1" 
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./lexvellum.db"
    SECRET_KEY: str = "9a3f2d8e4c1b5a7d0f2e8d9c6b4a1f0e2d4c8b6a3f1e9d5c7b2a0f4e8d9c6b4a"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CEO_EMAIL: str = "ceo@lexvellum.com"
    CEO_PASSWORD: str = "LexVellumCEO2024!"
    SMTP_EMAIL: str = ""
    SMTP_PASSWORD: str = ""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
settings = Settings()
