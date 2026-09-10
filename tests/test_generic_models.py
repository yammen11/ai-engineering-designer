"""Contract tests; require only Pydantic v2 and the Python standard library."""

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import unittest

from pydantic import BaseModel, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aied import models
from aied.models import (
    AssetInterface, AssetRequirement, CanonicalAsset, Capability,
    CapabilityRequirement, Component, Constraint, DataStatus, DataValue,
    EngineeringProject, MatchResult, MatchStatus, Pose, SourceReference,
)


def example_payload():
    return json.loads((ROOT / "examples/generic_project.json").read_text(encoding="utf-8"))


class DataValueTests(unittest.TestCase):
    def test_all_five_states_round_trip(self):
        for state in DataStatus:
            value = None if state in {DataStatus.UNKNOWN, DataStatus.NOT_APPLICABLE} else 4.5
            with self.subTest(state=state):
                item = DataValue(status=state, value=value, unit="kg")
                self.assertEqual(DataValue.model_validate_json(item.model_dump_json()), item)
                self.assertEqual(json.loads(item.model_dump_json())["status"], state.value)
        self.assertEqual(DataValue().status, DataStatus.UNKNOWN)

    def test_state_and_value_must_agree(self):
        for state in ("known", "estimated", "derived"):
            for payload in ({"status": state}, {"status": state, "value": None}):
                with self.subTest(payload=payload), self.assertRaises(ValidationError):
                    DataValue.model_validate(payload)
        for state in ("unknown", "not_applicable"):
            for value in (0, False, "", [], {}, 1.0):
                with self.subTest(state=state, value=value), self.assertRaises(ValidationError):
                    DataValue(status=state, value=value)
        with self.assertRaises(ValidationError):
            DataValue(status="missing")

    def test_json_values_keep_their_types_including_false_and_zero(self):
        for value in (0, 0.0, False, True, "", "001", [], {}, [1, False], {"nested": [0, None]}):
            with self.subTest(value=value):
                item = DataValue(status="known", value=value)
                restored = DataValue.model_validate_json(item.model_dump_json())
                self.assertEqual(restored.value, value)
                self.assertIs(type(restored.value), type(value))

    def test_values_are_finite_json_data_only(self):
        invalid = (
            float("nan"), float("inf"), float("-inf"),
            {"nested": [float("nan")]}, {"nested": {"x": float("inf")}},
            datetime(2026, 9, 10), Path("model.step"), object(), b"abc", (1, 2), {1: "x"},
        )
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                DataValue(status="known", value=value)

    def test_provenance_units_and_semantics_round_trip_without_file_access(self):
        item = DataValue(
            status="derived", value=0.012, unit="m",
            semantic_id="urn:example:width", derivation="12 mm / 1000",
            sources=[SourceReference(id="source-1", kind="file", uri="missing.pdf", locator="page 3")],
        )
        restored = DataValue.model_validate_json(item.model_dump_json())
        self.assertEqual(restored, item)
        self.assertEqual(restored.unit, "m")
        self.assertEqual(restored.value, 0.012)

    def test_unknown_is_independent_of_match_status(self):
        result = MatchResult(
            requirement_id="required", asset_id="asset",
            evidence={"payload": DataValue()},
        )
        self.assertEqual(result.status, MatchStatus.UNKNOWN)
        for status in MatchStatus:
            with self.subTest(status=status):
                item = MatchResult(requirement_id="r", asset_id="a", status=status)
                self.assertEqual(MatchResult.model_validate_json(item.model_dump_json()), item)
        with self.assertRaises(ValidationError):
            MatchResult(requirement_id="r", asset_id="a", status="known")


class GenericModelTests(unittest.TestCase):
    def test_complete_example_round_trips_through_json_and_python(self):
        project = EngineeringProject.model_validate(example_payload())
        self.assertEqual(EngineeringProject.model_validate_json(project.model_dump_json()), project)
        self.assertEqual(EngineeringProject.model_validate(project.model_dump()), project)
        self.assertEqual(project.product.components[2].quantity, 2)
        concept = project.automation_concepts[0]
        self.assertEqual(concept.resource_assignments[0].match_result.status, MatchStatus.UNKNOWN)
        self.assertIsNone(concept.layout_plan.scene_objects[1].pose)

    def test_project_can_grow_from_empty_to_product_to_process(self):
        payload = example_payload()
        draft = {"id": payload["id"]}
        for section in (None, "product", "process", "resources", "automation_concepts"):
            with self.subTest(section=section):
                if section is not None:
                    draft[section] = payload[section]
                project = EngineeringProject.model_validate(draft)
                self.assertEqual(EngineeringProject.model_validate_json(project.model_dump_json()), project)

    def test_open_asset_types_capabilities_and_properties(self):
        for kind in ("robot", "human", "conveyor", "custom_future_resource"):
            with self.subTest(kind=kind):
                asset = CanonicalAsset(
                    id="asset", asset_type=kind,
                    capabilities=[Capability(
                        id="custom-cap", capability="custom_future_capability",
                        parameters={"custom_measure": DataValue(status="estimated", value=3)},
                    )],
                    properties={"vendor:custom_flag": DataValue(status="known", value=False)},
                )
                self.assertEqual(CanonicalAsset.model_validate_json(asset.model_dump_json()), asset)

    def test_every_public_model_has_json_schema_and_rejects_extra_fields(self):
        for name in models.__all__:
            model = getattr(models, name)
            if not issubclass(model, BaseModel):
                continue
            with self.subTest(model=name):
                schema = model.model_json_schema()
                self.assertFalse(schema["additionalProperties"])
                json.dumps(schema, allow_nan=False)
                with self.assertRaises(ValidationError) as caught:
                    model.model_validate({"misspelled_field": True})
                self.assertIn("extra_forbidden", [error["type"] for error in caught.exception.errors()])
        with self.assertRaises(ValidationError):
            EngineeringProject(id="p", schema_version="2.0")

    def test_empty_identifiers_and_property_keys_are_rejected(self):
        for identifier in ("", " \t", 42):
            with self.subTest(identifier=identifier), self.assertRaises(ValidationError):
                Component(id=identifier)
        for key in ("", "   "):
            with self.subTest(key=key), self.assertRaises(ValidationError):
                Component(id="component", properties={key: DataValue()})

    def test_quantities_are_positive_integers_without_coercion(self):
        for model in (Component, AssetRequirement):
            self.assertEqual(model(id="item").quantity, 1)
            for quantity in (0, -1, True, 1.5, "2"):
                with self.subTest(model=model.__name__, quantity=quantity), self.assertRaises(ValidationError):
                    model(id="item", quantity=quantity)

    def test_mutable_defaults_are_isolated(self):
        first, second = EngineeringProject(id="first"), EngineeringProject(id="second")
        first.resources.append(CanonicalAsset(id="resource"))
        first.metadata["goal"] = DataValue(status="known", value="Example")
        self.assertEqual(second.resources, [])
        self.assertEqual(second.metadata, {})
        left, right = DataValue(), DataValue()
        left.sources.append(SourceReference(id="s", kind="manual"))
        self.assertEqual(right.sources, [])

    def test_revalidating_an_instance_catches_invalid_in_place_edits(self):
        project = EngineeringProject.model_validate(example_payload())
        project.product.components.append(project.product.components[0])
        with self.assertRaises(ValidationError):
            EngineeringProject.model_validate(project)
        value = DataValue()
        value.value = 5
        with self.assertRaises(ValidationError):
            DataValue.model_validate(value)

    def test_import_has_no_workflow_cad_gui_or_configuration_dependencies(self):
        code = (
            "import sys; sys.path.insert(0, sys.argv[1]); import aied.models; "
            "blocked = ('aied.schemas', 'aied.config', 'cadquery', 'PySide6', 'openai'); "
            "assert not any(name in sys.modules for name in blocked)"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-c", code, str(ROOT / "src")],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


class ReferenceTests(unittest.TestCase):
    def test_dangling_references_are_rejected_at_project_boundary(self):
        paths = (
            ("product", "assembly_relations", 0, "parent_component_id"),
            ("product", "assembly_relations", 0, "child_component_id"),
            ("process", "operations", 0, "component_ids", 0),
            ("automation_concepts", 0, "process_id"),
            ("automation_concepts", 0, "asset_requirements", 0, "operation_ids", 0),
            ("automation_concepts", 0, "resource_assignments", 0, "asset_requirement_id"),
            ("automation_concepts", 0, "resource_assignments", 0, "asset_id"),
            ("automation_concepts", 0, "resource_assignments", 0, "operation_ids", 0),
            ("automation_concepts", 0, "layout_plan", "scene_objects", 0, "entity_id"),
            ("automation_concepts", 0, "layout_plan", "scene_objects", 1, "entity_id"),
        )
        for path in paths:
            payload = example_payload()
            # Test actual project link validation independently of match consistency.
            payload["automation_concepts"][0]["resource_assignments"][0].pop("match_result")
            target = payload
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = "does-not-exist"
            with self.subTest(path=path), self.assertRaisesRegex(ValidationError, "Unresolved reference"):
                EngineeringProject.model_validate(payload)

    def test_duplicate_owned_ids_are_rejected(self):
        paths = (
            ("product", "components"), ("product", "assembly_relations"),
            ("resources", 0, "capabilities"), ("resources", 0, "interfaces"),
            ("process", "operations", 0, "capability_requirements", 0, "constraints"),
            ("automation_concepts", 0, "asset_requirements", 0, "constraints"),
            ("process", "operations"), ("process", "operations", 0, "capability_requirements"),
            ("resources",), ("automation_concepts",),
            ("automation_concepts", 0, "asset_requirements"),
            ("automation_concepts", 0, "asset_requirements", 0, "capability_requirements"),
            ("automation_concepts", 0, "resource_assignments"),
            ("automation_concepts", 0, "layout_plan", "scene_objects"),
        )
        for path in paths:
            payload = example_payload()
            target = payload
            for key in path:
                target = target[key]
            target.append(deepcopy(target[0]))
            with self.subTest(path=path), self.assertRaisesRegex(ValidationError, "Duplicate ID"):
                EngineeringProject.model_validate(payload)

    def test_invalid_predecessors_and_self_relations_are_rejected(self):
        for predecessor in ("does-not-exist", "tighten-screws"):
            payload = example_payload()
            payload["process"]["operations"][0]["predecessor_ids"] = [predecessor]
            with self.subTest(predecessor=predecessor), self.assertRaises(ValidationError):
                EngineeringProject.model_validate(payload)
        payload = example_payload()
        payload["product"]["assembly_relations"][0]["child_component_id"] = "base-plate"
        with self.assertRaises(ValidationError):
            EngineeringProject.model_validate(payload)

    def test_matching_result_must_describe_the_assignment(self):
        for field in ("asset_id", "requirement_id"):
            payload = example_payload()
            payload["automation_concepts"][0]["resource_assignments"][0]["match_result"][field] = "different"
            with self.subTest(field=field), self.assertRaises(ValidationError):
                EngineeringProject.model_validate(payload)


class StabilizationTests(unittest.TestCase):
    def test_confidence_is_optional_bounded_and_preserves_states(self):
        self.assertIsNone(DataValue().confidence)
        for state in DataStatus:
            value = None if state in {DataStatus.UNKNOWN, DataStatus.NOT_APPLICABLE} else 5
            for confidence in (None, 0, 0.5, 1):
                with self.subTest(state=state, confidence=confidence):
                    item = DataValue(status=state, value=value, confidence=confidence)
                    self.assertEqual(DataValue.model_validate_json(item.model_dump_json()), item)
        for confidence in (-0.01, 1.01, True, "0.5", float("nan"), float("inf")):
            with self.subTest(confidence=confidence), self.assertRaises(ValidationError):
                DataValue(confidence=confidence)
        result = MatchResult(requirement_id="r", asset_id="a", evidence={"x": DataValue(confidence=1)})
        self.assertEqual(result.status, MatchStatus.UNKNOWN)

    def test_capabilities_and_interfaces_preserve_open_types_and_provenance(self):
        source = SourceReference(id="s", kind="example")
        capability = Capability(
            id="c", capability="future:ability", name="Example capability",
            semantic_id="urn:example:cap", description="Synthetic capability",
            sources=[source], parameters={"x": DataValue(status="derived", value=4, confidence=0.8)},
        )
        kinds = ("mechanical", "electrical", "communication", "pneumatic", "hydraulic", "software", "future:interface")
        interfaces = [AssetInterface(
            id=kind, interface_type=kind, standard="future:standard",
            semantic_id="urn:example:interface", sources=[source],
            properties={"custom": DataValue(status="known", value={"enabled": True})},
        ) for kind in kinds]
        asset = CanonicalAsset(id="a", capabilities=[capability], interfaces=interfaces)
        self.assertEqual(CanonicalAsset.model_validate_json(asset.model_dump_json()), asset)
        for model, field in ((Capability, "capability"), (AssetInterface, "interface_type")):
            for value in ("", "   ", None):
                with self.subTest(model=model, value=value), self.assertRaises(ValidationError):
                    model.model_validate({"id": "x", field: value})

    def test_all_constraint_operators_round_trip(self):
        operands = {"=": False, "!=": "x", ">": 1, ">=": 0, "<": 5, "<=": 4,
                    "between": [1, 4], "in": ["a", "b"], "contains": "feature"}
        for operator, operand in operands.items():
            for strength in ("hard", "soft"):
                with self.subTest(operator=operator, strength=strength):
                    constraint = Constraint(
                        id="c", property_ref="custom", semantic_ref="urn:example:custom",
                        operator=operator, strength=strength,
                        value=DataValue(status="known", value=operand, unit="custom_unit"),
                    )
                    self.assertEqual(Constraint.model_validate_json(constraint.model_dump_json()), constraint)

    def test_constraint_requires_reference_operator_and_qualified_value(self):
        base = {"id": "c", "property_ref": "mass", "operator": "<=",
                "value": {"status": "known", "value": 2, "unit": "kg"}}
        self.assertEqual(Constraint.model_validate(base).strength, "hard")
        semantic_only = dict(base, semantic_ref="urn:example:mass")
        semantic_only.pop("property_ref")
        self.assertEqual(Constraint.model_validate(semantic_only).semantic_ref, "urn:example:mass")
        invalid = [dict(base, property_ref=None), dict(base, property_ref=" "),
                   dict(base, semantic_ref=""), dict(base, operator="equals"),
                   dict(base, strength="mandatory"), dict(base, value=2)]
        for missing in ("operator", "value"):
            payload = dict(base)
            payload.pop(missing)
            invalid.append(payload)
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                Constraint.model_validate(payload)

    def test_constraint_operand_shapes_are_checked_without_matching(self):
        for operator, operand in (("between", [2, 1]), ("between", [1]),
                                  ("between", [True, 2]), ("between", ["1", "2"]),
                                  ("in", []), ("in", "a"), (">", True), ("<=", "2")):
            with self.subTest(operator=operator, operand=operand), self.assertRaises(ValidationError):
                Constraint(id="c", property_ref="x", operator=operator,
                           value=DataValue(status="known", value=operand))
        for operator in ("between", "in", ">", "contains"):
            for state in ("unknown", "not_applicable"):
                item = Constraint(id="c", property_ref="x", operator=operator, value=DataValue(status=state))
                self.assertEqual(Constraint.model_validate_json(item.model_dump_json()), item)

    def test_nested_revalidation_and_independent_defaults(self):
        first = CanonicalAsset(id="a")
        second = CanonicalAsset(id="b")
        first.interfaces.append(AssetInterface(id="i", interface_type="software"))
        first.capabilities.append(Capability(id="c", capability="custom"))
        self.assertEqual(second.interfaces, [])
        self.assertEqual(second.capabilities, [])
        left, right = Capability(id="l", capability="x"), Capability(id="r", capability="x")
        left.parameters["x"] = DataValue()
        self.assertEqual(right.parameters, {})
        for model, kwargs in ((AssetRequirement, {}), (CapabilityRequirement, {"capability": "x"})):
            a, b = model(id="a", **kwargs), model(id="b", **kwargs)
            a.constraints.append(Constraint(id="c", property_ref="x", operator="=", value=DataValue()))
            self.assertEqual(b.constraints, [])
        project = EngineeringProject.model_validate(example_payload())
        project.resources[0].interfaces[1].properties["voltage"].confidence = 2
        with self.assertRaises(ValidationError):
            EngineeringProject.model_validate(project)

    def test_example_uses_stabilized_contract_and_rejects_old_shape(self):
        project = EngineeringProject.model_validate(example_payload())
        self.assertEqual(project.schema_version, "1.1")
        self.assertIsInstance(project.resources[0].capabilities[0], Capability)
        self.assertIsInstance(project.resources[0].interfaces[0], AssetInterface)
        self.assertIsInstance(project.process.operations[0].capability_requirements[0].constraints[0], Constraint)
        with self.assertRaises(ValidationError):
            EngineeringProject(id="p", schema_version="1.0")
        with self.assertRaises(ValidationError):
            CanonicalAsset(id="a", capabilities={"handling": {}})


class PoseTests(unittest.TestCase):
    def test_pose_round_trip_and_explicit_identity(self):
        self.assertEqual(Pose().translation_mm, (0.0, 0.0, 0.0))
        pose = Pose(translation_mm=(1, 2, 3), rotation_deg=(0, 0, 90), frame_id="fixture")
        self.assertEqual(Pose.model_validate_json(pose.model_dump_json()), pose)

    def test_pose_requires_three_finite_numbers(self):
        for field in ("translation_mm", "rotation_deg"):
            for vector in ([1, 2], [1, 2, 3, 4], [True, 0, 0], ["1", 0, 0], [float("nan"), 0, 0], [float("inf"), 0, 0]):
                with self.subTest(field=field, vector=vector), self.assertRaises(ValidationError):
                    Pose.model_validate({field: vector})


if __name__ == "__main__":
    unittest.main()
