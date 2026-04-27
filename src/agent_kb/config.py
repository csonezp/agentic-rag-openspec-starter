from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class AppConfig:
    model_provider: str
    deepseek_api_key: Optional[str]
    deepseek_base_url: str
    deepseek_model: str
    openai_api_key: Optional[str]
    model: str
    embedding_model: str

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "AppConfig":
        return cls(
            model_provider=env.get("MODEL_PROVIDER", "deepseek"),
            deepseek_api_key=env.get("DEEPSEEK_API_KEY") or None,
            deepseek_base_url=env.get(
                "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
            ).rstrip("/"),
            deepseek_model=env.get("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            openai_api_key=env.get("OPENAI_API_KEY") or None,
            model=env.get("OPENAI_MODEL", "gpt-4.1-mini"),
            embedding_model=env.get(
                "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
            ),
        )

    @property
    def has_openai_api_key(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_deepseek_api_key(self) -> bool:
        return bool(self.deepseek_api_key)
