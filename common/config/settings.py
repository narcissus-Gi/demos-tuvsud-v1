# 加载 .env
# 校验环境变量
# 设置安全默认值
# 提供全局统一的配置对象

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Self
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import (
    Field,
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

# settings.py 位于：
# demos-tuvsud-v1/common/config/settings.py
#
# parents[0] = config
# parents[1] = common
# parents[2] = demos-tuvsud-v1
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class AppEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class RunMode(StrEnum):
    MOCK = "mock"
    REAL = "real"


class LLMProvider(StrEnum):
    MOCK = "mock"
    OPENAI = "openai"
    OPENAI_COMPATIBLE = "openai_compatible"


class CheckpointBackend(StrEnum):
    MEMORY = "memory"
    SQLITE = "sqlite"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AppSettings(BaseSettings):
    """ Demo 共用的基础运行配置。"""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",

        case_sensitive=False,

        env_ignore_empty=True,

        extra="ignore",

        frozen=True,
    )

    # ========================================================
    # Application
    # ========================================================

    app_env: AppEnvironment = AppEnvironment.DEVELOPMENT
    run_mode: RunMode = RunMode.MOCK
    log_level: LogLevel = LogLevel.INFO
    business_timezone: str = "Asia/Shanghai"

    # ========================================================
    # LLM
    # ========================================================

    llm_provider: LLMProvider = LLMProvider.MOCK
    llm_model: str | None = None
    llm_base_url: str | None = None
    llm_api_key: SecretStr | None = None

    llm_temperature: float = Field(
        default=0,
        ge=0,
        le=2,
    )
    llm_timeout_seconds: float = Field(
        default=30,
        gt=0,
        le=300,
    )
    llm_max_retries: int = Field(
        default=2,
        ge=0,
        le=10,
    )

    # ========================================================
    # LangGraph
    # ========================================================

    checkpoint_backend: CheckpointBackend = (
        CheckpointBackend.MEMORY
    )
    checkpoint_db_path: Path = Path(
        ".runtime/checkpoints.sqlite3"
    )

    graph_recursion_limit: int = Field(
        default=50,
        ge=1,
        le=1000,
    )

    # ========================================================
    # Business execution limits
    # ========================================================

    max_model_calls: int = Field(
        default=6,
        ge=1,
        le=100,
    )
    max_tool_retries: int = Field(
        default=2,
        ge=0,
        le=10,
    )
    max_execution_seconds: float = Field(
        default=60,
        gt=0,
        le=3600,
    )

    @field_validator("business_timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "business_timezone cannot be empty"
            )

        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError(
                f"unknown timezone: {value}"
            ) from error

        return value

    @field_validator("llm_model", "llm_base_url")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    @model_validator(mode="after")
    def validate_llm_configuration(self) -> Self:

        if self.run_mode == RunMode.MOCK:
            return self

        if self.llm_provider == LLMProvider.MOCK:
            raise ValueError(
                "LLM_PROVIDER cannot be mock "
                "when RUN_MODE is real"
            )

        if not self.llm_model:
            raise ValueError(
                "LLM_MODEL is required "
                "when RUN_MODE is real"
            )

        if self.llm_provider == LLMProvider.OPENAI:
            if self.llm_api_key is None:
                raise ValueError(
                    "LLM_API_KEY is required "
                    "for the OpenAI provider"
                )

        if (
            self.llm_provider
            == LLMProvider.OPENAI_COMPATIBLE
            and not self.llm_base_url
        ):
            raise ValueError(
                "LLM_BASE_URL is required "
                "for an OpenAI-compatible provider"
            )

        return self

    @property
    def checkpoint_path(self) -> Path:
        """返回检查点数据库的绝对路径，但不创建目录。"""

        if self.checkpoint_db_path.is_absolute():
            return self.checkpoint_db_path

        return PROJECT_ROOT / self.checkpoint_db_path


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """加载并缓存全局配置。"""

    return AppSettings()