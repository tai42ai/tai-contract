"""The generic versioned-document store contract.

A ``kind``-discriminated, body-opaque persistence primitive: append-only version
rows over an opaque JSONB ``body``, an active-version pointer, and rollback. The
store knows NOTHING about presets/policies/agents — those are typed VIEWS layered
on top. Identity is ``(kind, name)`` throughout; every write is one transaction.

This package holds the :class:`VersionedStore` Protocol plus its record models
(:class:`DocumentRecord`, :class:`DocumentVersion`) and typed errors. It is
reached from the assembled facade as ``app.versioning.store`` (see
:class:`~tai_contract.app.facets.AppVersioning`).
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from tai_contract.versioning.errors import (
    DocumentExistsError,
    DocumentNotFoundError,
    DocumentStoreError,
    DocumentVersionNotFoundError,
)
from tai_contract.versioning.models import DocumentRecord, DocumentVersion


@runtime_checkable
class VersionedStore(Protocol):
    """Kind-discriminated, body-opaque version store. Identity is ``(kind, name)``.

    The ``body`` is opaque ``dict``/JSONB — the store never inspects it; the caller
    (a typed view) owns its shape. Every method raises loudly on a missing,
    duplicate, or invalid target — never a silent default. ``tags`` is the generic
    per-version grouping label (see :class:`DocumentVersion`), distinct from any
    categorization a ``kind``'s body may carry.
    """

    async def create(self, kind: str, name: str, body: dict[str, Any], tags: list[str] | None = None) -> DocumentRecord:
        """Insert a new document at ``active_version = 1`` plus its version 1, one
        transaction. Raise :class:`DocumentExistsError` if ``(kind, name)`` is
        already a live document."""
        ...

    async def save_version(
        self, kind: str, name: str, body: dict[str, Any], tags: list[str] | None = None
    ) -> DocumentVersion:
        """Append a new version (``new_version = max(version) + 1``, NOT
        ``active_version + 1``) and bump the active pointer to it, one transaction
        (a partial failure rolls the whole save back — no orphan version, no
        half-bumped pointer). Raise :class:`DocumentNotFoundError` if absent."""
        ...

    async def list(self, kind: str) -> list[DocumentRecord]:
        """List the active (non-soft-deleted) documents of ``kind``."""
        ...

    async def get(self, kind: str, name: str) -> DocumentRecord:
        """Fetch the active record for ``(kind, name)``. Raise
        :class:`DocumentNotFoundError` if absent."""
        ...

    async def get_active_body(self, kind: str, name: str) -> dict[str, Any]:
        """Return the ``body`` of the active version for ``(kind, name)``. Raise
        :class:`DocumentNotFoundError` if absent."""
        ...

    async def list_versions(self, kind: str, name: str) -> list[DocumentVersion]:
        """List every version of ``(kind, name)``, each carrying the
        :attr:`DocumentVersion.is_current` signal derived from ``active_version``.
        Raise :class:`DocumentNotFoundError` if the document is absent."""
        ...

    async def get_version(self, kind: str, name: str, version: int) -> DocumentVersion:
        """Fetch one version. Raise :class:`DocumentVersionNotFoundError` if that
        version does not exist."""
        ...

    async def rollback(self, kind: str, name: str, version: int) -> DocumentRecord:
        """Re-point ``active_version`` to ``version`` (NO data copy). Raise
        :class:`DocumentVersionNotFoundError` if that version does not exist."""
        ...

    async def soft_delete(self, kind: str, name: str) -> None:
        """Set ``is_active = False``, keeping the version history (audit). The
        document drops out of ``list``/``get`` but its rows survive."""
        ...

    async def delete(self, kind: str, name: str) -> None:
        """HARD delete, DISTINCT from :meth:`soft_delete`: remove ONLY the ACTIVE
        document row for ``(kind, name)`` AND its version rows, so nothing of the
        active document survives; a soft-deleted ghost of the same name is left
        untouched. Raise :class:`DocumentNotFoundError` if there is no active row.
        Used to roll a never-succeeded create fully back and to remove a conflicted
        record without leaving the ghost + spurious history a soft delete would."""
        ...

    async def rename(self, kind: str, name: str, new_name: str) -> DocumentRecord:
        """Re-key the ACTIVE document ``(kind, name)`` to ``(kind, new_name)`` in one
        atomic write. The whole version history, every per-version ``tags`` label, and
        the ``active_version`` pointer move untouched — versions key on the document,
        not the name, so nothing is copied. The ``body`` is never inspected (the store
        stays body-opaque). A soft-deleted ghost named ``new_name`` does NOT block (the
        same partial-unique identity rule :meth:`create` follows), and a soft-deleted
        ghost of ``name`` is left untouched as audit history. Raise
        :class:`DocumentNotFoundError` if ``(kind, name)`` has no active row; raise
        :class:`DocumentExistsError` (carrying ``new_name``) if ``(kind, new_name)`` is
        already a live document."""
        ...


__all__ = [
    "DocumentExistsError",
    "DocumentNotFoundError",
    "DocumentRecord",
    "DocumentStoreError",
    "DocumentVersion",
    "DocumentVersionNotFoundError",
    "VersionedStore",
]
