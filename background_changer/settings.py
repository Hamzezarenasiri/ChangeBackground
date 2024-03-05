import enum
import os
from pathlib import Path
from tempfile import gettempdir
from typing import List, Optional

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    users_secret: str = os.getenv("USERS_SECRET", "")
    # Variables for the database
    db_file: Path = TEMP_DIR / "db.sqlite3"
    db_echo: bool = False

    # Variables for Redis
    redis_host: str = "background_changer-redis"
    redis_port: int = 6379
    redis_user: Optional[str] = None
    redis_pass: Optional[str] = None
    redis_base: Optional[int] = None

    # Variables for RabbitMQ
    rabbit_host: str = "background_changer-rmq"
    rabbit_port: int = 5672
    rabbit_user: str = "guest"
    rabbit_pass: str = "guest"
    rabbit_vhost: str = "/"

    rabbit_pool_size: int = 2
    rabbit_channel_pool_size: int = 10

    # This variable is used to define
    # multiproc_dir. It's required for [uvi|guni]corn projects.
    prometheus_dir: Path = TEMP_DIR / "prom"

    # Sentry's configuration.
    sentry_dsn: Optional[
        str
    ] = "https://2d8fe08755186f68c69cac3adc80c7b4@o1178736.ingest.us.sentry.io/4506857577447424"
    sentry_sample_rate: float = 1.0

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(scheme="sqlite+aiosqlite", path=f"///{self.db_file}")

    @property
    def redis_url(self) -> URL:
        """
        Assemble REDIS URL from settings.

        :return: redis URL.
        """
        path = f"/{self.redis_base}" if self.redis_base is not None else ""
        return URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
            user=self.redis_user,
            password=self.redis_pass,
            path=path,
        )

    @property
    def rabbit_url(self) -> URL:
        """
        Assemble RabbitMQ URL from settings.

        :return: rabbit URL.
        """
        return URL.build(
            scheme="amqp",
            host=self.rabbit_host,
            port=self.rabbit_port,
            user=self.rabbit_user,
            password=self.rabbit_pass,
            path=self.rabbit_vhost,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BACKGROUND_CHANGER_",
        env_file_encoding="utf-8",
    )

    PROJECT_DESCRIPTION: str = "Remove background"
    PROJECT_SERVERS: List[dict[str, AnyHttpUrl]] = [
        {"url": "https://rmbg.afarin.top"},
        {"url": "http://localhost:8000"},
    ]
    USER_IMAGE_MAX_FILE_SIZE: int = 100 * 2**20  # 100MB
    DEFAULT_MAX_STR_LENGTH: int = 3145728  # 3MB
    USER_IMAGE_SUPPORTED_FORMATS: List[str] = [
        "image/jpeg",
        "image/png",
        # "image/webp",
        # "image/svg+xml",
    ]
    REQUEST_ATTACHMENT_MAX_FILE_SIZE: int = 2**30 * 2
    DEFAULT_MEDIA_PATH: str = "media"
    DEFAULT_BACKGROUND_PATH: str = f"{DEFAULT_MEDIA_PATH}/backgrounds"
    DEFAULT_IMAGES_PATH: str = f"{DEFAULT_MEDIA_PATH}/images"
    AZURE_STORAGE_ACCOUNT_ACCESS_KEY: str = "/3N7mr9p8zx4aGDv0rgQLY/BFxUPMt9/FL5dCYe1JRgKNWu7iqnnsJZZv5xAMnX9SY3gAvkq8IK2/yyFjl8pQQ=="
    AZURE_STORAGE_ACCOUNT_NAME: str = "hillzimage"


settings = Settings()
