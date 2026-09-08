from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class BoxParameters(BaseModel):
    length_mm: float = Field(gt=0, le=100000)
    width_mm: float = Field(gt=0, le=100000)
    height_mm: float = Field(gt=0, le=100000)


class CylinderParameters(BaseModel):
    radius_mm: float = Field(gt=0, le=50000)
    height_mm: float = Field(gt=0, le=100000)


class SphereParameters(BaseModel):
    radius_mm: float = Field(gt=0, le=50000)


class CadInstruction(BaseModel):
    operation: Literal[
        "create_box",
        "create_cylinder",
        "create_sphere",
        "copy_input_step",
    ]

    box: Optional[BoxParameters] = None
    cylinder: Optional[CylinderParameters] = None
    sphere: Optional[SphereParameters] = None
    reason: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def validate_parameters(self):
        if self.operation == "create_box" and self.box is None:
            mode: Literal["local", "openai", "demo"]
        if self.operation == "create_cylinder" and self.cylinder is None:
            raise ValueError("cylinder parameters are required for create_cylinder")
        if self.operation == "create_sphere" and self.sphere is None:
            raise ValueError("sphere parameters are required for create_sphere")
        return self


class StepMetadata(BaseModel):
    file_name: str
    bounding_box_mm: list[float]
    solids: int
    volume_mm3: float


class RunRecord(BaseModel):
    run_id: str
    mode: Literal["local", "openai", "demo"]
    user_request: str
    pdf_file: Optional[str] = None
    step_file: Optional[str] = None
    step_metadata: Optional[StepMetadata] = None
    instruction: CadInstruction
    output_step: str
