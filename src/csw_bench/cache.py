"""Persistent response cache, keyed by content hash of the full request.

The Phase 3 requirement is that a rerun never re-bills: identical settings hit the
cache, any settings change misses it. Each entry stores the request alongside the
response so a hit can be verified against what it claims to answer -- a corrupt or
mismatched entry fails loudly rather than silently serving a wrong response as if the
model had produced it.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

from csw_bench.providers import CompletionRequest, ModelResponse


class CacheError(Exception):
    pass


class CacheEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    request: CompletionRequest
    response: ModelResponse


class ResponseCache:
    def __init__(self, root: Path) -> None:
        self._root = root

    @staticmethod
    def key(request: CompletionRequest) -> str:
        payload = json.dumps(request.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _path(self, key: str) -> Path:
        return self._root / key[:2] / f"{key}.json"

    def get(self, request: CompletionRequest) -> ModelResponse | None:
        path = self._path(self.key(request))
        if not path.exists():
            return None
        try:
            entry = CacheEntry.model_validate_json(path.read_text(encoding="utf-8"))
        except ValidationError as exc:
            raise CacheError(f"{path}: corrupt cache entry: {exc}") from exc
        if entry.request != request:
            raise CacheError(f"{path}: stored request does not match its key")
        return entry.response

    def put(self, request: CompletionRequest, response: ModelResponse) -> None:
        path = self._path(self.key(request))
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = CacheEntry(request=request, response=response)
        path.write_text(entry.model_dump_json(indent=2), encoding="utf-8")
