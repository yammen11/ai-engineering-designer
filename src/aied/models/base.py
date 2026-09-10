"""Shared contracts for the generic engineering model (independent of v0.1)."""

from typing import Annotated, Iterable

from pydantic import BaseModel, ConfigDict, StringConstraints


NonEmptyString = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]


class CoreModel(BaseModel):
    """Validate at input boundaries; extensibility belongs in explicit properties."""

    model_config = ConfigDict(
        extra="forbid", validate_default=True, allow_inf_nan=False,
        revalidate_instances="always",
    )


def unique_ids(ids: Iterable[str], context: str) -> set[str]:
    result: set[str] = set()
    for identifier in ids:
        if identifier in result:
            raise ValueError(f"Duplicate ID {identifier!r} in {context}")
        result.add(identifier)
    return result


def require_references(ids: Iterable[str], available: set[str], context: str) -> None:
    for identifier in ids:
        if identifier not in available:
            raise ValueError(f"Unresolved reference {identifier!r} in {context}")
