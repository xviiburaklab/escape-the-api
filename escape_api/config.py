import warnings
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:escape123@localhost:5434/escape_db"
    ADMIN_KEY: str = ""
    ALLOWED_ORIGINS: str = "*"
    SESSION_REQUEST_LIMIT: int = 150

    @property
    def allowed_origins_list(self) -> list[str]:
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()

if not settings.ADMIN_KEY:
    warnings.warn(
        "ADMIN_KEY is not set in .env — admin endpoints are unprotected!",
        RuntimeWarning,
        stacklevel=2,
    )
