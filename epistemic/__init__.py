"""Phase 2 deterministic epistemic layer — the system under test.

Reconstructed from docs/handoff_packet.md §1-§3. Nothing in this package makes
a model call: it is all rules, so it is cheap, auditable, and testable offline.
"""

from epistemic.budget import BudgetCeiling, BudgetExceeded
from epistemic.classifier import ClaimType, Classification, classify_claim
from epistemic.registry import Bucket, EntityRecord, EntityRegistry
from epistemic.router import Route, route

__all__ = [
    "BudgetCeiling",
    "BudgetExceeded",
    "ClaimType",
    "Classification",
    "classify_claim",
    "Bucket",
    "EntityRecord",
    "EntityRegistry",
    "Route",
    "route",
]
