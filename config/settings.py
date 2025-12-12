import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    
    # Redis Configuration (optional)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Model Configuration
    # Using Mistral-7B-Instruct-v0.3 as primary SLM
    PRIMARY_MODEL: str = os.getenv("PRIMARY_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "HuggingFaceH4/zephyr-7b-beta")
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    NEWS_CACHE_TTL: int = int(os.getenv("NEWS_CACHE_TTL", "300"))
    
    # Agent Configuration
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Search Configuration
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    SEARCH_TIMELIMIT: str = os.getenv("SEARCH_TIMELIMIT", "w")  # w=week, d=day
    
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()