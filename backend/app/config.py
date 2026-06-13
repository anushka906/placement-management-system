import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


def load_env_file() -> None:
    env_file = Path(__file__).resolve().parents[1] / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    app_name: str = "Placement Management System"
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/placement_db")
    )
    jwt_secret_key: str = field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", "change-this-secret-key"))
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    access_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    )


@lru_cache
def get_settings() -> Settings:
    load_env_file()
    return Settings()
