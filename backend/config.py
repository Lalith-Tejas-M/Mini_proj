from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Intergenerational Knowledge Agent"
    
    # Fluxbase config
    FLUXBASE_PROJECT_ID: str = "fc352d688d314602"
    FLUXBASE_API_KEY: str = "fl_049872a9d847d906ed83d8fb787b96790ec30492689285b6"
    FLUXBASE_URL: str = "https://fluxbase.vercel.app/api/execute-sql"
    
    # Ollama config
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # Optional secrets
    JWT_SECRET: str = "super_secret_key_for_jwt_tokens"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
