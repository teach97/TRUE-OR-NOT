"""Request boundary compatible with the existing TypeScript request fields."""
import base64
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


ModelId = Literal["gemini-3.8-flash", "gemini-3.7-flash", "gpt-6-luna"]
ModelPreference = Literal["auto", "gemini-3.8-flash", "gemini-3.7-flash", "gpt-6-luna"]
MODEL_CATALOG: tuple[tuple[ModelId, str], ...] = (
    ("gemini-3.8-flash", "Gemini 3.8 Flash"),
    ("gemini-3.7-flash", "Gemini 3.7 Flash"),
    ("gpt-6-luna", "GPT-6 Luna Max"),
)

_IMAGE_MIMES = ("image/jpeg", "image/png", "image/webp")
_MAX_IMAGE_BYTES = 1_500_000


class ImageAttachment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    mime: Literal["image/jpeg", "image/png", "image/webp"]
    data: str = Field(min_length=1, max_length=2_000_000)

    @field_validator("data")
    @classmethod
    def validate_data(cls, value):
        try:
            raw = base64.b64decode(value, validate=True)
        except ValueError:
            raise ValueError("Image data must be base64")
        if not raw or len(raw) > _MAX_IMAGE_BYTES:
            raise ValueError("Image size out of bounds")
        return value


class FactCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    text: str = Field(max_length=12000)
    focus: str = Field(max_length=500)
    consent: bool
    modelPreference: ModelPreference = "auto"
    linkUrl: str | None = Field(default=None, max_length=2048)
    image: ImageAttachment | None = None
    jevMode: bool = False

    @field_validator("text", "focus")
    @classmethod
    def validate_text_length(cls, value, info):
        # JavaScript string.length counts UTF-16 code units, not code points.
        limit = 12000 if info.field_name == "text" else 500
        if len(value.encode("utf-16-le", errors="surrogatepass")) // 2 > limit:
            raise ValueError("Input exceeds the UTF-16 length limit")
        return value

    @field_validator("linkUrl")
    @classmethod
    def validate_link_url(cls, value):
        if value is None:
            return None
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port is not None
        ):
            raise ValueError("Link URL must be a plain http(s) URL")
        return value

    @model_validator(mode="after")
    def validate_text_or_image(self):
        if not self.text.strip() and self.image is None:
            raise ValueError("Text must not be blank without an image")
        return self

    @field_validator("consent")
    @classmethod
    def require_consent(cls, value):
        if value is not True:
            raise ValueError("Explicit consent is required")
        return value
