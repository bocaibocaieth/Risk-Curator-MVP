"""Application configuration using Pydantic Settings."""

import logging
import warnings
from typing import List, Literal
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: Literal["development", "staging", "production"] = "development"

    # Database - no default in production
    database_url: str = "sqlite+aiosqlite:///./risk_monitor.db"

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

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Validate settings for production environment."""
        if self.is_production:
            # Warn if debug is enabled in production
            if self.debug:
                warnings.warn(
                    "DEBUG mode is enabled in PRODUCTION environment! "
                    "This is a security risk.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                logger.warning("DEBUG mode is enabled in PRODUCTION - this is a security risk")

            # Warn if using SQLite in production
            if "sqlite" in self.database_url.lower():
                warnings.warn(
                    "SQLite is not recommended for production use. "
                    "Consider using PostgreSQL.",
                    RuntimeWarning,
                    stacklevel=2,
                )

            # Warn if no API key is set
            if not self.api_key:
                logger.warning("No API_KEY configured - API is open without authentication")

        return self


settings = Settings()
