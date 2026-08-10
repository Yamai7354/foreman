"""
Configuration module for Foreman.
Loads settings from .env file using python-dotenv.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

# Load .env file from project root
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)


@dataclass
class Config:
    """Central configuration for Foreman."""

    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    templates_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "templates")
    reports_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "reports")
    website_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "website")

    # GitHub settings (loaded from .env)
    github_username: Optional[str] = field(default_factory=lambda: os.getenv("GITHUB_USERNAME"))
    github_token: Optional[str] = field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))

    # LLM settings (loaded from .env)
    llm_enabled: bool = field(default_factory=lambda: os.getenv("LLM_ENABLED", "true").lower() == "true")
    llm_base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", "http://localhost:5001/v1"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "local-model"))

    # Autolog LLM settings (optional - falls back to main LLM if not set)
    llm_autolog_url: str = field(default_factory=lambda: os.getenv("LLM_AUTOLOG_URL") or os.getenv("LLM_BASE_URL", "http://localhost:5001/v1"))
    llm_autolog_model: str = field(default_factory=lambda: os.getenv("LLM_AUTOLOG_MODEL") or os.getenv("LLM_MODEL", "local-model"))

    # Codewatch LLM settings (optional - falls back to main LLM if not set)
    llm_codewatch_url: str = field(default_factory=lambda: os.getenv("LLM_CODEWATCH_URL") or os.getenv("LLM_BASE_URL", "http://localhost:5001/v1"))
    llm_codewatch_model: str = field(default_factory=lambda: os.getenv("LLM_CODEWATCH_MODEL") or os.getenv("LLM_MODEL", "local-model"))

    # Default author info (loaded from .env)
    author_name: str = field(default_factory=lambda: os.getenv("AUTHOR_NAME", "Randy Johnson"))
    author_email: str = field(default_factory=lambda: os.getenv("AUTHOR_EMAIL", ""))

    def __post_init__(self):
        """Ensure directories exist."""
        for dir_path in [self.data_dir, self.templates_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from a YAML file."""
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        return cls()

    def save(self, config_path: Path):
        """Save configuration to a YAML file."""
        data = {
            "github_username": self.github_username,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "llm_enabled": self.llm_enabled,
            "llm_base_url": self.llm_base_url,
            "llm_model": self.llm_model,
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
        _config = Config.from_file(config_path)
    return _config
