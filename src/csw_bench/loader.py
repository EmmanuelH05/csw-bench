from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from csw_bench.schema import Item
from csw_bench.taxonomy import TaskType, ViolationType

_ITEM_ADAPTER: TypeAdapter[Item] = TypeAdapter(Item)


class ItemLoadError(Exception):
    def __init__(self, path: Path, cause: str) -> None:
        super().__init__(f"{path}: {cause}")
        self.path = path


class ItemSet:
    """Items are parsed once at construction and indexed by violation type.

    `matriz` calls `filter_by_violation_type` repeatedly to build held-out splits, so the
    index is built up front rather than scanning on every call.
    """

    def __init__(self, items: Iterable[Item]) -> None:
        self._items: tuple[Item, ...] = tuple(items)

        duplicates = sorted(
            item_id for item_id, count in Counter(i.id for i in self._items).items() if count > 1
        )
        if duplicates:
            raise ValueError(f"duplicate item ids: {duplicates}")

        buckets: dict[ViolationType, list[Item]] = {v: [] for v in ViolationType}
        for item in self._items:
            buckets[item.primary_violation].append(item)
        self._by_violation: dict[ViolationType, tuple[Item, ...]] = {
            violation: tuple(bucket) for violation, bucket in buckets.items()
        }

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Item]:
        return iter(self._items)

    @property
    def items(self) -> tuple[Item, ...]:
        return self._items

    def filter_by_violation_type(self, *violations: ViolationType) -> tuple[Item, ...]:
        """Disjoint by construction: every item has exactly one primary violation, so
        filtering on distinct types can never return overlapping sets.
        """
        if not violations:
            return ()
        seen: set[ViolationType] = set()
        result: list[Item] = []
        for violation in violations:
            if violation in seen:
                continue
            seen.add(violation)
            result.extend(self._by_violation[violation])
        return tuple(result)

    def filter_by_task_type(self, *tasks: TaskType) -> tuple[Item, ...]:
        wanted = set(tasks)
        return tuple(item for item in self._items if item.task_type in wanted)

    def exclude_synthetic(self) -> ItemSet:
        """Headline results never include synthetic items."""
        return ItemSet(i for i in self._items if i.provenance.source != "synthetic")

    def counts_by_violation_type(self) -> dict[ViolationType, int]:
        return {v: len(items) for v, items in self._by_violation.items()}

    def filter_by_license(self, *licenses: str) -> tuple[Item, ...]:
        """CC BY-NC-SA and CC BY-NC-ND material cannot be pooled into one derived set --
        SA demands share-alike, ND forbids adaptation -- so consumers select
        license-compatible subsets rather than assuming the set is homogeneous.
        """
        wanted = set(licenses)
        return tuple(i for i in self._items if i.provenance.license in wanted)

    def counts_by_license(self) -> dict[str, int]:
        return dict(Counter(i.provenance.license for i in self._items))

    def hash(self) -> str:
        """SHA-256 over items sorted by id, excluding load order and file mtime.

        `matriz` records this to prove which item set it evaluated against, so the
        procedure is fixed permanently -- a change to how the hash is computed is
        indistinguishable from a change to the data.
        """
        digest = hashlib.sha256()
        for item in sorted(self._items, key=lambda i: i.id):
            payload = item.model_dump(mode="json")
            digest.update(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode())
        return digest.hexdigest()


def load_item(path: Path) -> Item:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ItemLoadError(path, f"invalid JSON: {exc}") from exc
    try:
        return _ITEM_ADAPTER.validate_python(raw)
    except ValidationError as exc:
        raise ItemLoadError(path, f"schema violation: {exc}") from exc


def load_items(items_root: Path) -> ItemSet:
    if not items_root.is_dir():
        raise ItemLoadError(items_root, "not a directory")
    return ItemSet(load_item(p) for p in sorted(items_root.rglob("*.json")))
