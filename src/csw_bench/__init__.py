"""csw-bench — a Matrix Language Frame benchmark for intrasentential code-switching.

The names re-exported here are the interface `matriz` depends on. Treat them as a
contract: adding is safe, renaming or changing their semantics breaks a published
experiment.
"""

from csw_bench.accounting import PricePerMTok, RunAccounting
from csw_bench.cache import CacheError, ResponseCache
from csw_bench.loader import ItemLoadError, ItemSet, load_item, load_items
from csw_bench.prompts import TEMPLATE_IDS, render
from csw_bench.providers import (
    PROVIDER_FAMILIES,
    CompletionRequest,
    ModelProvider,
    ModelResponse,
    ProviderError,
    create_provider,
)
from csw_bench.results import Cell, Report, TaskDelta, above_chance, compare, load_run, summarize
from csw_bench.runner import RetentionError, RunConfig, RunRecord, RunResult, run, run_id
from csw_bench.schema import Item, Provenance
from csw_bench.scoring import Score, score
from csw_bench.stats import bootstrap_ci
from csw_bench.taxonomy import (
    RESOLUTION_ORDER,
    VIOLATION_SPECS,
    Language,
    SystemMorphemeClass,
    TaskType,
    ViolationType,
)

__version__ = "1.0.0"

__all__ = [
    "PROVIDER_FAMILIES",
    "RESOLUTION_ORDER",
    "TEMPLATE_IDS",
    "VIOLATION_SPECS",
    "CacheError",
    "Cell",
    "CompletionRequest",
    "Item",
    "ItemLoadError",
    "ItemSet",
    "Language",
    "ModelProvider",
    "ModelResponse",
    "PricePerMTok",
    "Provenance",
    "ProviderError",
    "Report",
    "ResponseCache",
    "RetentionError",
    "RunAccounting",
    "RunConfig",
    "RunRecord",
    "RunResult",
    "Score",
    "SystemMorphemeClass",
    "TaskDelta",
    "TaskType",
    "ViolationType",
    "__version__",
    "above_chance",
    "bootstrap_ci",
    "compare",
    "create_provider",
    "load_item",
    "load_items",
    "load_run",
    "render",
    "run",
    "run_id",
    "score",
    "summarize",
]
