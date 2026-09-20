"""Request boundary compatible with the existing TypeScript request fields."""
from pydantic import BaseModel, ConfigDict, Field, field_validator


class FactCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    text: str = Field(min_length=1, max_length=12000)
    focus: str = Field(max_length=500)
    consent: bool

    @field_validator("text", "focus")
    @classmethod
    def validate_text_length(cls, value, info):
        # JavaScript string.length counts UTF-16 code units, not code points.
        limit = 12000 if info.field_name == "text" else 500
        if len(value.encode("utf-16-le", errors="surrogatepass")) // 2 > limit:
            raise ValueError("Input exceeds the UTF-16 length limit")
        if info.field_name == "text" and not value.strip():
            raise ValueError("Text must not be blank")
        return value

    @field_validator("consent")
    @classmethod
    def require_consent(cls, value):
        if value is not True:
            raise ValueError("Explicit consent is required")
        return value
