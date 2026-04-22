from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "LexVellum Differential"
    VERSION: str = "0.1.0"
    
    # Vector DB
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "lexvellumlaws"
    PINECONE_ENVIRONMENT: str = "us-east-1" # Or whatever region you use
    
    # Google Gemini
    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
