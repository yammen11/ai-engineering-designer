"""JSON-safe engineering values with explicit knowledge state and provenance."""

from enum import Enum
from typing import Self

from pydantic import Field, JsonValue, model_validator

from .base import CoreModel, NonEmptyString


class DataStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    ESTIMATED = "estimated"
    DERIVED = "derived"
    NOT_APPLICABLE = "not_applicable"


class SourceReference(CoreModel):
    """Source identity and optional locator; no file access or URL resolution."""

    id: NonEmptyString
    kind: NonEmptyString
    uri: NonEmptyString | None = None
    locator: NonEmptyString | None = None
    description: NonEmptyString | None = None


class DataValue(CoreModel):
    """A value's knowledge state is independent of technical suitability.

    Known/estimated/derived require a non-null value. Unknown/not_applicable
    require null. Zero, false and empty JSON containers are legitimate values.
    Units and semantic IDs are labels, without implicit conversion or lookup.
    """

    status: DataStatus = DataStatus.UNKNOWN
    value: JsonValue = None
    unit: NonEmptyString | None = None
    semantic_id: NonEmptyString | None = None
    sources: list[SourceReference] = Field(default_factory=list)
    description: NonEmptyString | None = None
    derivation: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        without_value = self.status in {DataStatus.UNKNOWN, DataStatus.NOT_APPLICABLE}
        if without_value and self.value is not None:
            raise ValueError(f"{self.status.value} requires a null value")
        if not without_value and self.value is None:
            raise ValueError(f"{self.status.value} requires a non-null value")
        return self


class EngineeringObject(CoreModel):
    """Stable identity plus extensible, explicitly qualified properties."""

    id: NonEmptyString
    name: NonEmptyString | None = None
    description: NonEmptyString | None = None
    semantic_id: NonEmptyString | None = None
    properties: dict[NonEmptyString, DataValue] = Field(default_factory=dict)
    sources: list[SourceReference] = Field(default_factory=list)


class GeometryReference(CoreModel):
    """Reference to geometry; neither loads nor validates a CAD file."""

    id: NonEmptyString
    uri: NonEmptyString
    format: NonEmptyString | None = None
    source: SourceReference | None = None
    properties: dict[NonEmptyString, DataValue] = Field(default_factory=dict)
