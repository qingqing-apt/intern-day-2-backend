import os


def _split_origins(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    """全部配置来自环境变量，默认值仅用于本地练习。"""

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
        self.allowed_origins = _split_origins(os.getenv("ALLOWED_ORIGINS", "http://localhost:5173"))
        self.session_ttl_minutes = int(os.getenv("SESSION_TTL_MINUTES", "60"))
        self.seed_username = os.getenv("SEED_USERNAME", "intern")
        self.seed_password = os.getenv("SEED_PASSWORD", "intern-pass-123")
        self.collect_interval_seconds = float(os.getenv("COLLECT_INTERVAL_SECONDS", "5"))
        self.metrics_retention = int(os.getenv("METRICS_RETENTION", "720"))


settings = Settings()
