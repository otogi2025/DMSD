"""设置 (config) — 从 .env / 环境变量读入。

`pydantic_settings.BaseSettings` で型安全な設定読み込み。
`get_settings()` を依存注入経由で使う (キャッシュ済 = process 全体で 1 instance)。
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用
    app_env: Literal["dev", "staging", "production"] = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # DB
    database_url: str = "sqlite:///./tomoshibi_dev.db"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_min: int = 1440      # 24h
    jwt_refresh_expire_min: int = 43200    # 30d

    # SendGrid (D1)
    sendgrid_api_key: str = ""
    email_from: str = "noreply@tomoshibi.example.jp"
    email_from_name: str = "Tomoshibi 通知"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ログ
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
