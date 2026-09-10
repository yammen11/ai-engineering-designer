"""Layout data only: no CAD loading, transformation or placement algorithm."""

from typing import Literal, Self

from pydantic import Field, StrictFloat, model_validator

from .base import CoreModel, NonEmptyString, unique_ids
from .data import EngineeringObject


class Pose(CoreModel):
    """Local-to-parent pose in a right-handed frame.

    Translation is XYZ in mm. Rotation is active extrinsic XYZ in degrees:
    p_parent = Rz(rz) @ Ry(ry) @ Rx(rx) @ p_local + translation_mm.
    This declares a data convention; it does not implement transformations.
    """

    translation_mm: tuple[StrictFloat, StrictFloat, StrictFloat] = (0.0, 0.0, 0.0)
    rotation_deg: tuple[StrictFloat, StrictFloat, StrictFloat] = (0.0, 0.0, 0.0)
    frame_id: NonEmptyString = "world"


class SceneObject(EngineeringObject):
    """One occurrence of a component or resource; null pose means unplaced."""

    entity_type: Literal["component", "asset"]
    entity_id: NonEmptyString
    pose: Pose | None = None


class LayoutPlan(EngineeringObject):
    scene_objects: list[SceneObject] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_objects(self) -> Self:
        unique_ids((obj.id for obj in self.scene_objects), "layout.scene_objects")
        return self
