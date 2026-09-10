"""Regression coverage for the existing v0.1 contracts and local CAD pipeline.

The LLM is mocked; no server or GUI is started. CAD integration tests require
the existing application dependencies and write only into temporary directories.
The known demo-mode and missing-box-parameter bugs are outside this change.
"""

from importlib.util import find_spec
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from pydantic import BaseModel


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aied import schemas
from aied.schemas import (
    BoxParameters,
    CadInstruction,
    CylinderParameters,
    RunRecord,
    SphereParameters,
    StepMetadata,
)


class LegacySchemaTests(unittest.TestCase):
    def test_public_schema_imports_remain_available(self):
        for model in (
            BoxParameters,
            CylinderParameters,
            SphereParameters,
            CadInstruction,
            StepMetadata,
            RunRecord,
        ):
            with self.subTest(model=model.__name__):
                self.assertIs(getattr(schemas, model.__name__), model)
                self.assertTrue(issubclass(model, BaseModel))
                self.assertEqual(model.__module__, "aied.schemas")

    def test_all_four_existing_cad_operations_validate(self):
        examples = (
            ("create_box", "box", {"length_mm": 20, "width_mm": 40, "height_mm": 60}, BoxParameters),
            ("create_cylinder", "cylinder", {"radius_mm": 5, "height_mm": 30}, CylinderParameters),
            ("create_sphere", "sphere", {"radius_mm": 10}, SphereParameters),
            ("copy_input_step", None, None, None),
        )
        for operation, parameter_name, parameters, parameter_type in examples:
            with self.subTest(operation=operation):
                payload = {"operation": operation, "reason": "Existing v0.1 instruction."}
                if parameter_name is not None:
                    payload[parameter_name] = parameters

                instruction = CadInstruction.model_validate(payload)

                self.assertEqual(instruction.operation, operation)
                if parameter_name is not None:
                    self.assertIsInstance(getattr(instruction, parameter_name), parameter_type)
                self.assertEqual(
                    CadInstruction.model_validate_json(instruction.model_dump_json()),
                    instruction,
                )

    def test_legacy_run_record_json_round_trip(self):
        for mode in ("local", "openai", "demo"):
            with self.subTest(mode=mode):
                payload = {
                    "run_id": "20260909_002130_15bd48a6",
                    "mode": mode,
                    "user_request": "Kugel mit Radius 4 cm erzeugen; Größe prüfen.",
                    "pdf_file": None,
                    "step_file": "input.step",
                    "step_metadata": {
                        "file_name": "input.step",
                        "bounding_box_mm": [80.0, 80.0, 80.0],
                        "solids": 1,
                        "volume_mm3": 268082.5731,
                    },
                    "instruction": {
                        "operation": "create_sphere",
                        "box": None,
                        "cylinder": None,
                        "sphere": {"radius_mm": 40.0},
                        "reason": "4 cm entsprechen 40 mm.",
                    },
                    "output_step": "data/outputs/example/output.step",
                }

                record = RunRecord.model_validate_json(json.dumps(payload))

                self.assertIsInstance(record.instruction, CadInstruction)
                self.assertIsInstance(record.step_metadata, StepMetadata)
                self.assertEqual(json.loads(record.model_dump_json()), payload)
                self.assertEqual(RunRecord.model_validate_json(record.model_dump_json()), record)


class LegacyPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        required_modules = ("cadquery", "numpy", "dotenv", "openai", "fitz")
        missing = [name for name in required_modules if find_spec(name) is None]
        if missing:
            raise unittest.SkipTest("CAD pipeline dependencies unavailable: " + ", ".join(missing))

        # Defer heavy optional CAD imports so the schema checks also work with
        # only Pydantic installed. Import errors in installed packages still fail.
        from aied.services import pipeline
        from aied.services import cad_service

        cls.pipeline = pipeline
        cls.cad_service = cad_service

    def test_local_pipeline_exports_step_and_existing_run_record(self):
        instruction = CadInstruction(
            operation="create_box",
            box=BoxParameters(length_mm=20, width_mm=40, height_mm=60),
            reason="Create the requested box.",
        )
        user_request = "Create a 20 x 40 x 60 mm box."
        with TemporaryDirectory(prefix="aied_legacy_") as temporary_directory:
            output_root = Path(temporary_directory)
            with (
                patch.object(self.pipeline, "OUTPUT_DIR", output_root),
                patch.object(self.pipeline, "LLM_PROVIDER", "local"),
                patch.object(self.pipeline, "run_engineering_agent", return_value=instruction) as agent,
            ):
                record = self.pipeline.execute_pipeline(None, None, user_request)

            agent.assert_called_once()
            self.assertIn(user_request, agent.call_args.args[0])
            self.assertIsInstance(record, RunRecord)
            self.assertEqual(record.mode, "local")
            self.assertEqual(record.instruction, instruction)
            self.assertIsNone(record.step_metadata)
            output_step = Path(record.output_step)
            self.assertEqual(output_step, output_root / record.run_id / "output.step")
            self.assertTrue(output_step.is_file())

            metadata = self.cad_service.inspect_step(output_step)
            self.assertEqual(metadata.bounding_box_mm, [20.0, 40.0, 60.0])
            self.assertEqual(metadata.solids, 1)
            self.assertAlmostEqual(metadata.volume_mm3, 48000.0, places=3)
            persisted = RunRecord.model_validate_json(
                (output_step.parent / "run.json").read_text(encoding="utf-8")
            )
            self.assertEqual(persisted, record)

    def test_local_pipeline_copies_input_step_and_preserves_metadata(self):
        copy_instruction = CadInstruction(
            operation="copy_input_step",
            reason="Keep the supplied geometry.",
        )
        with TemporaryDirectory(prefix="aied_legacy_copy_") as temporary_directory:
            temporary_root = Path(temporary_directory)
            input_step = temporary_root / "input.step"
            self.cad_service.generate_step(
                CadInstruction(
                    operation="create_sphere",
                    sphere=SphereParameters(radius_mm=10),
                    reason="Input fixture.",
                ),
                input_step,
            )
            expected_metadata = self.cad_service.inspect_step(input_step)
            with (
                patch.object(self.pipeline, "OUTPUT_DIR", temporary_root / "outputs"),
                patch.object(self.pipeline, "LLM_PROVIDER", "local"),
                patch.object(self.pipeline, "run_engineering_agent", return_value=copy_instruction) as agent,
            ):
                record = self.pipeline.execute_pipeline(None, input_step, "Copy this STEP.")

            agent.assert_called_once()
            self.assertIn(expected_metadata.model_dump_json(indent=2), agent.call_args.args[0])
            self.assertEqual(record.step_file, str(input_step))
            self.assertEqual(record.step_metadata, expected_metadata)
            self.assertEqual(Path(record.output_step).read_bytes(), input_step.read_bytes())
            persisted = RunRecord.model_validate_json(
                (Path(record.output_step).parent / "run.json").read_text(encoding="utf-8")
            )
            self.assertEqual(persisted, record)


if __name__ == "__main__":
    unittest.main()
