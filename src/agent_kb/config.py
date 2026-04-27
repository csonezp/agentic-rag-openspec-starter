from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: Optional[str]
    model: str
    embedding_model: str

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "AppConfig":
        return cls(
            openai_api_key=env.get("OPENAI_API_KEY") or None,
            model=env.get("OPENAI_MODEL", "gpt-4.1-mini"),
            embedding_model=env.get(
                "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
            ),
        )

    @property
    def has_openai_api_key(self) -> bool:
        return bool(self.openai_api_key)
