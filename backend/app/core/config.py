from functools import lru_cache
from typing import List

import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Recruit Flow API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/recruit_flow"

    secret_key: str = "change-me"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7

    allowed_origins: List[str] = ["http://localhost:5173"]

    resume_upload_dir: str = "./uploads/resumes"
    spacy_model: str = "en_core_web_sm"
    resume_parser_url: str | None = None
    resume_parser_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", env_nested_delimiter=None)

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                stripped = value.strip().strip("[]")
                return [origin.strip().strip("\"'") for origin in stripped.split(",") if origin.strip()]
            return []
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
