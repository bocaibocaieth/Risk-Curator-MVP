"""Application configuration using Pydantic Settings."""

from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: Literal["development", "staging", "production"] = "development"

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/risk_monitor"

    # Redis (optional)
    redis_url: str = "redis://localhost:6379"

    # External APIs
    coingecko_api_key: str = ""
    defillama_base_url: str = "https://api.llama.fi"

    # RPC Endpoints
    eth_rpc_url: str = "https://eth.llamarpc.com"
    arb_rpc_url: str = "https://arb1.arbitrum.io/rpc"
    base_rpc_url: str = "https://mainnet.base.org"

    # Telegram
    telegram_bot_token: str = ""
    telegram_default_chat_id: str = ""

    # App Settings
    debug: bool = False  # Default to False for security
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # API Authentication
    api_key: str = ""  # Optional API key for authentication
    api_key_header: str = "X-API-Key"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


settings = Settings()
