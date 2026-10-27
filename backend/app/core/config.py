"""
Core application configuration for EvalForge using Pydantic Settings.
Defines MongoDB credentials, evaluation thresholds, and synthesis parameters.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EvalForge"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "eval_forge_db"

    # Evaluation Thresholds
    DEFAULT_FAITHFULNESS_THRESHOLD: float = 0.80
    DEFAULT_GROUNDEDNESS_THRESHOLD: float = 0.85
    DEFAULT_RELEVANCE_THRESHOLD: float = 0.75
    DEFAULT_CONTEXT_RECALL_THRESHOLD: float = 0.70

    # Supported Target LLMs for Benchmark
    SUPPORTED_MODELS: List[str] = [
        "gpt-4o",
        "gpt-4o-mini",
        "claude-3-5-sonnet-20241022",
        "deepseek-chat",
        "llama-3.3-70b-instruct",
        "custom-rag-pipeline"
    ]

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
