"""Runtime metadata contract schema."""

from pydantic import BaseModel, ConfigDict


class RuntimeMeta(BaseModel):
    """Descriptive runtime metadata."""

    model_config = ConfigDict(frozen=True)

    service: str
    environment: str
    version: str
    build_sha: str | None = None
