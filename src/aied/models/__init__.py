"""Generic engineering data contracts. Legacy workflow schemas stay in aied.schemas."""

from .data import DataStatus, DataValue, GeometryReference, SourceReference
from .engineering import (
    AssemblyRelation,
    AssetInterface,
    AssetRequirement,
    AutomationConcept,
    CanonicalAsset,
    Capability,
    CapabilityRequirement,
    Component,
    Constraint,
    EngineeringProject,
    MatchResult,
    MatchStatus,
    Operation,
    Process,
    Product,
    ResourceAssignment,
)
from .spatial import LayoutPlan, Pose, SceneObject

__all__ = [
    "AssemblyRelation", "AssetInterface", "AssetRequirement", "AutomationConcept", "CanonicalAsset",
    "Capability", "CapabilityRequirement", "Component", "Constraint", "DataStatus", "DataValue",
    "EngineeringProject", "GeometryReference", "LayoutPlan", "MatchResult",
    "MatchStatus", "Operation", "Pose", "Process", "Product",
    "ResourceAssignment", "SceneObject", "SourceReference",
]
