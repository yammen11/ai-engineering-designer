from pathlib import Path
import shutil

import cadquery as cq
import numpy as np

from aied.schemas import CadInstruction, StepMetadata


def _load_step(step_path: Path):
    return cq.importers.importStep(str(step_path))


def inspect_step(step_path: Path) -> StepMetadata:
    obj = _load_step(step_path)

    solids = obj.solids().vals()
    solid_count = len(solids)

    shape = obj.val()
    bbox = shape.BoundingBox()

    volume = 0.0
    for solid in solids:
        try:
            volume += float(solid.Volume())
        except Exception:
            pass

    return StepMetadata(
        file_name=step_path.name,
        bounding_box_mm=[
            round(float(bbox.xlen), 4),
            round(float(bbox.ylen), 4),
            round(float(bbox.zlen), 4),
        ],
        solids=solid_count,
        volume_mm3=round(volume, 4),
    )


def generate_step(
    instruction: CadInstruction,
    output_path: Path,
    input_step_path: Path | None = None,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if instruction.operation == "copy_input_step":
        if input_step_path is None:
            raise ValueError(
                "Agent requested copy_input_step, but no STEP input was provided."
            )
        shutil.copy2(input_step_path, output_path)
        return output_path

    if instruction.operation == "create_box":
        p = instruction.box
        model = cq.Workplane("XY").box(
            p.length_mm,
            p.width_mm,
            p.height_mm,
            centered=(True, True, False),
        )

    elif instruction.operation == "create_cylinder":
        p = instruction.cylinder
        model = cq.Workplane("XY").circle(p.radius_mm).extrude(p.height_mm)

    elif instruction.operation == "create_sphere":
        p = instruction.sphere
        model = cq.Workplane("XY").sphere(p.radius_mm)

    else:
        raise ValueError(f"Unsupported operation: {instruction.operation}")

    cq.exporters.export(model, str(output_path))
    return output_path


def step_to_mesh_data(step_path: Path):
    # Convert STEP B-Rep into triangles for the GUI viewer.
    obj = _load_step(step_path)

    vertices_all = []
    faces_flat = []
    vertex_offset = 0

    shapes = obj.solids().vals()
    if not shapes:
        shapes = [obj.val()]

    for shape in shapes:
        vertices, triangles = shape.tessellate(0.5)

        verts_np = np.asarray(
            [v.toTuple() for v in vertices],
            dtype=float,
        )
        vertices_all.append(verts_np)

        for tri in triangles:
            faces_flat.extend(
                [
                    3,
                    tri[0] + vertex_offset,
                    tri[1] + vertex_offset,
                    tri[2] + vertex_offset,
                ]
            )

        vertex_offset += len(vertices)

    if not vertices_all:
        raise ValueError("No displayable geometry was found in the STEP file.")

    return (
        np.vstack(vertices_all),
        np.asarray(faces_flat, dtype=np.int64),
    )
