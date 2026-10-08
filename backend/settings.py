"""Server-side settings and secret loading."""
import os
from pathlib import Path

from dotenv import dotenv_values
from pydantic import BaseModel, SecretStr

class Settings(BaseModel):
    api_key: SecretStr
    explabs_api_key: SecretStr = SecretStr("")
    gemini_api_key: SecretStr = SecretStr("")
    youtube_api_key: SecretStr = SecretStr("")
    tavily_api_key: SecretStr = SecretStr("")
    typesafe_api_key: SecretStr = SecretStr("")
    finnhub_api_key: SecretStr = SecretStr("")
    kosis_api_key: SecretStr = SecretStr("")

def load_settings(env_path: Path | None = None) -> Settings:
    """Read the backend-local file without mutating process environment."""
    path = env_path if env_path is not None else Path(__file__).with_name(".env")
    values = dotenv_values(path, encoding="utf-8-sig", interpolate=False)
    key = os.environ.get("OPENAI_API_KEY", values.get("OPENAI_API_KEY") or "")
    explabs_key = os.environ.get("EXPLABS_API_KEY", values.get("EXPLABS_API_KEY") or "")
    gemini_key = os.environ.get("GEMINI_API_KEY", values.get("GEMINI_API_KEY") or "")
    youtube_key = os.environ.get("YOUTUBE_API_KEY", values.get("YOUTUBE_API_KEY") or "")
    tavily_key = os.environ.get("TAVILY_API_KEY", values.get("TAVILY_API_KEY") or "")
    gateway_key = os.environ.get("TYPESAFE_API_KEY", values.get("TYPESAFE_API_KEY") or "")
    finnhub_key = os.environ.get("FINNHUB_API_KEY", values.get("FINNHUB_API_KEY") or "")
    kosis_key = os.environ.get("KOSIS_API_KEY", values.get("KOSIS_API_KEY") or "")
    return Settings(
        api_key=SecretStr(key.strip()),
        explabs_api_key=SecretStr(explabs_key.strip()),
        gemini_api_key=SecretStr(gemini_key.strip()),
        youtube_api_key=SecretStr(youtube_key.strip()),
        tavily_api_key=SecretStr(tavily_key.strip()),
        typesafe_api_key=SecretStr(gateway_key.strip()),
        finnhub_api_key=SecretStr(finnhub_key.strip()),
        kosis_api_key=SecretStr(kosis_key.strip()),
    )
