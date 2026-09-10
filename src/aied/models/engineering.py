"""Product-process-resource contracts, separate from workflow instructions."""

from enum import Enum
from typing import Literal, Self

from pydantic import Field, StrictInt, model_validator

from .base import CoreModel, NonEmptyString, require_references, unique_ids
from .data import DataValue, EngineeringObject, GeometryReference
from .spatial import LayoutPlan, Pose


class Component(EngineeringObject):
    quantity: StrictInt = Field(default=1, gt=0)
    geometry: list[GeometryReference] = Field(default_factory=list)


class AssemblyRelation(EngineeringObject):
    """Generic directed relationship between two components of one product."""

    parent_component_id: NonEmptyString
    child_component_id: NonEmptyString
    relation_type: NonEmptyString
    relative_pose: Pose | None = None

    @model_validator(mode="after")
    def validate_endpoints(self) -> Self:
        if self.parent_component_id == self.child_component_id:
            raise ValueError("An assembly relation requires two distinct components")
        return self


class Product(EngineeringObject):
    components: list[Component] = Field(default_factory=list)
    assembly_relations: list[AssemblyRelation] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_structure(self) -> Self:
        components = unique_ids((item.id for item in self.components), "product.components")
        unique_ids((item.id for item in self.assembly_relations), "product.assembly_relations")
        for relation in self.assembly_relations:
            require_references(
                [relation.parent_component_id, relation.child_component_id],
                components, f"assembly relation {relation.id}",
            )
        return self


class Capability(EngineeringObject):
    """Open capability type with qualified parameters and inherited provenance."""

    capability: NonEmptyString
    parameters: dict[NonEmptyString, DataValue] = Field(default_factory=dict)


class Constraint(EngineeringObject):
    """Requirement on a property, identified by local and/or semantic reference.

    Value, unit and knowledge state live together in DataValue. References are
    labels, not resolved paths. This validates the operand shape, not a match.
    """

    property_ref: NonEmptyString | None = None
    semantic_ref: NonEmptyString | None = None
    operator: Literal["=", "!=", ">", ">=", "<", "<=", "between", "in", "contains"]
    value: DataValue
    strength: Literal["hard", "soft"] = "hard"

    @model_validator(mode="after")
    def validate_operand(self) -> Self:
        if self.property_ref is None and self.semantic_ref is None:
            raise ValueError("A constraint requires property_ref or semantic_ref")
        operand = self.value.value
        if operand is None:
            # Unknown/not_applicable are valid data states, never a failed match.
            return self
        if self.operator == "between":
            if (
                not isinstance(operand, list) or len(operand) != 2
                or any(type(bound) not in (int, float) for bound in operand)
            ):
                raise ValueError("between requires two numeric bounds [lower, upper]")
            if operand[0] > operand[1]:
                raise ValueError("between requires lower <= upper")
        elif self.operator == "in":
            if not isinstance(operand, list) or not operand:
                raise ValueError("in requires a non-empty list of alternatives")
        elif self.operator in {">", ">=", "<", "<="}:
            if type(operand) not in (int, float):
                raise ValueError("Ordered comparisons require a numeric operand")
        return self


class CapabilityRequirement(EngineeringObject):
    """Required capability, properties and constraints; no matching engine."""

    capability: NonEmptyString
    constraints: list[Constraint] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_constraints(self) -> Self:
        unique_ids((item.id for item in self.constraints), "capability_requirement.constraints")
        return self


class Operation(EngineeringObject):
    """A process step, unrelated to CadInstruction.operation."""

    component_ids: list[NonEmptyString] = Field(default_factory=list)
    predecessor_ids: list[NonEmptyString] = Field(default_factory=list)
    capability_requirements: list[CapabilityRequirement] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_links(self) -> Self:
        unique_ids(self.component_ids, "operation.component_ids")
        unique_ids(self.predecessor_ids, "operation.predecessor_ids")
        unique_ids((item.id for item in self.capability_requirements), "operation.capability_requirements")
        if self.id in self.predecessor_ids:
            raise ValueError("An operation cannot be its own predecessor")
        return self


class Process(EngineeringObject):
    operations: list[Operation] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_structure(self) -> Self:
        operations = unique_ids((item.id for item in self.operations), "process.operations")
        for operation in self.operations:
            require_references(operation.predecessor_ids, operations, f"operation {operation.id}")
        return self


class AssetRequirement(EngineeringObject):
    role: NonEmptyString | None = None
    quantity: StrictInt = Field(default=1, gt=0)
    capability_requirements: list[CapabilityRequirement] = Field(default_factory=list)
    operation_ids: list[NonEmptyString] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_links(self) -> Self:
        unique_ids(self.operation_ids, "asset_requirement.operation_ids")
        unique_ids((item.id for item in self.capability_requirements), "asset_requirement.capability_requirements")
        unique_ids((item.id for item in self.constraints), "asset_requirement.constraints")
        return self


class AssetInterface(EngineeringObject):
    """Open interface category/standard; technical details live in properties.

    Categories may be mechanical, electrical, communication, pneumatic,
    hydraulic, software or any future type. No compatibility is inferred.
    """

    interface_type: NonEmptyString
    standard: NonEmptyString | None = None


class CanonicalAsset(EngineeringObject):
    """Source-independent resource with explicit capabilities and interfaces."""

    asset_type: NonEmptyString | None = None
    capabilities: list[Capability] = Field(default_factory=list)
    interfaces: list[AssetInterface] = Field(default_factory=list)
    geometry: list[GeometryReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_structure(self) -> Self:
        unique_ids((item.id for item in self.capabilities), "asset.capabilities")
        unique_ids((item.id for item in self.interfaces), "asset.interfaces")
        return self


class MatchStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


class MatchResult(CoreModel):
    """Reported comparison outcome. No automatic derivation or aggregation."""

    requirement_id: NonEmptyString
    asset_id: NonEmptyString
    status: MatchStatus = MatchStatus.UNKNOWN
    reason: NonEmptyString | None = None
    evidence: dict[NonEmptyString, DataValue] = Field(default_factory=dict)


class ResourceAssignment(EngineeringObject):
    asset_requirement_id: NonEmptyString
    asset_id: NonEmptyString
    operation_ids: list[NonEmptyString] = Field(default_factory=list)
    match_result: MatchResult | None = None

    @model_validator(mode="after")
    def validate_links(self) -> Self:
        unique_ids(self.operation_ids, "resource_assignment.operation_ids")
        if self.match_result is not None:
            if self.match_result.asset_id != self.asset_id:
                raise ValueError("match_result.asset_id must match the assigned asset")
            if self.match_result.requirement_id != self.asset_requirement_id:
                raise ValueError("match_result.requirement_id must match the assigned requirement")
        return self


class AutomationConcept(EngineeringObject):
    """A concept may exist before any assets are selected or placed."""

    process_id: NonEmptyString | None = None
    asset_requirements: list[AssetRequirement] = Field(default_factory=list)
    resource_assignments: list[ResourceAssignment] = Field(default_factory=list)
    layout_plan: LayoutPlan | None = None

    @model_validator(mode="after")
    def validate_structure(self) -> Self:
        requirements = unique_ids((item.id for item in self.asset_requirements), "concept.asset_requirements")
        unique_ids((item.id for item in self.resource_assignments), "concept.resource_assignments")
        require_references(
            (item.asset_requirement_id for item in self.resource_assignments),
            requirements, f"concept {self.id} resource assignments",
        )
        return self


class EngineeringProject(EngineeringObject):
    """Growing PPR document; absent sections are allowed, dangling IDs are not.

    Version 1.1 is this data contract's version, not the application version.
    Validation checks structure/references, never engineering feasibility.
    """

    schema_version: Literal["1.1"] = "1.1"
    metadata: dict[NonEmptyString, DataValue] = Field(default_factory=dict)
    product: Product | None = None
    process: Process | None = None
    resources: list[CanonicalAsset] = Field(default_factory=list)
    automation_concepts: list[AutomationConcept] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        components = {item.id for item in self.product.components} if self.product else set()
        operations = {item.id for item in self.process.operations} if self.process else set()
        resources = unique_ids((item.id for item in self.resources), "project.resources")
        unique_ids((item.id for item in self.automation_concepts), "project.automation_concepts")

        if self.process is not None:
            for operation in self.process.operations:
                require_references(operation.component_ids, components, f"operation {operation.id} components")

        for concept in self.automation_concepts:
            if concept.process_id is not None:
                require_references(
                    [concept.process_id], {self.process.id} if self.process else set(),
                    f"concept {concept.id} process",
                )
            for requirement in concept.asset_requirements:
                require_references(requirement.operation_ids, operations, f"requirement {requirement.id} operations")
            for assignment in concept.resource_assignments:
                require_references([assignment.asset_id], resources, f"assignment {assignment.id} asset")
                require_references(assignment.operation_ids, operations, f"assignment {assignment.id} operations")
            if concept.layout_plan is not None:
                for obj in concept.layout_plan.scene_objects:
                    available = components if obj.entity_type == "component" else resources
                    require_references([obj.entity_id], available, f"scene object {obj.id}")
        return self
