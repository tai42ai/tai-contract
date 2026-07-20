"""The presets contract: the :class:`~tai_contract.agent.base.PresetSpec` data
model, the :class:`PresetBody` persisted shape, the preset-specific errors, and
the :class:`PresetStore` Protocol.

A *preset* is a base tool with a partial set of keyword arguments baked in,
exposed as a new named, versioned tool. It is the FIRST typed VIEW over the
generic versioned-document store (``kind="preset"``): the store holds the opaque
body, this Protocol is the typed interface over it. tai-contract owns only the
Protocol + models + errors; the concrete view that delegates to the store,
validates/reshapes the body, and maps the generic errors to these preset errors
lives in the skeleton (no versioning code in the view).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable

from tai_contract.agent.base import PresetSpec
from tai_contract.manifest import ExtensionElement
from tai_contract.presets.errors import (
    PresetError,
    PresetExistsError,
    PresetNameConflictError,
    PresetNotFoundError,
    PresetVersionNotFoundError,
)
from tai_contract.presets.models import CARRY_FORWARD, CarryForward, PresetBody
from tai_contract.versioning.models import DocumentRecord, DocumentVersion


@runtime_checkable
class PresetStore(Protocol):
    """The typed interface over the versioned-document store with ``kind="preset"``.

    Delegation, body validation/reshaping, and error mapping are the concrete
    (skeleton) view's job — this Protocol pins only the surface. A preset body is
    always the full :class:`PresetBody` (``{base_tool, description, fixed_kwargs,
    extensions, tags}``); the editable-field methods reconstruct it under the
    carry-forward rules documented on :meth:`save_version`.
    """

    async def create_preset(
        self,
        spec: PresetSpec,
        extensions: Sequence[Sequence[ExtensionElement]],
        tags: list[str],
        output_schema: dict[str, Any] | None = None,
    ) -> DocumentRecord:
        """Create a versioned preset. ``spec`` carries ``name``/``description``/
        ``base_tool``/``fixed_kwargs``; ``extensions`` (the combos list), the
        categorization ``tags``, and the optional ``output_schema`` ride alongside —
        all of them land in the persisted :class:`PresetBody`. Raise
        :class:`PresetExistsError` on a duplicate name,
        :class:`PresetNameConflictError` if the name collides with a base tool."""
        ...

    async def save_version(
        self,
        name: str,
        fixed_kwargs: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        extensions: Sequence[Sequence[ExtensionElement]] | None = None,
        output_schema: dict[str, Any] | None | CarryForward = CARRY_FORWARD,
    ) -> DocumentVersion:
        """Append a new version from the editable body fields.

        A version body is the FULL :class:`PresetBody`, so the view reconstructs
        the new body by ALWAYS carrying ``base_tool`` and ``description`` forward
        from the ACTIVE version body, then applying each of ``fixed_kwargs``,
        ``tags``, ``extensions`` under one UNIFORM sentinel: omitted/``None`` =
        carry the active value forward unchanged; an explicit empty list (``tags=[]``
        / ``extensions=[]``) = deliberately CLEAR that field. An explicitly provided
        empty list is a value, never "not provided". ``output_schema`` follows the
        SAME rule but with a distinct :data:`CARRY_FORWARD` sentinel (its cleared
        state is ``None``, so ``None`` cannot double as "not provided"): omitted =
        carry forward, an explicit ``None`` = clear, an explicit dict = wins. An
        empty INNER combo (``[[]]`` or any ``[]`` member of ``extensions``) is
        REJECTED. The new body never DROPS a field. ``tags`` here is the preset-body
        categorization field, NOT the generic per-version ``DocumentVersion.tags``
        label. Raise :class:`PresetNotFoundError` if the preset is absent."""
        ...

    async def list_presets(self) -> list[DocumentRecord]:
        """List the active versioned presets."""
        ...

    async def get_preset(self, name: str) -> DocumentRecord:
        """Fetch a preset's active record. Raise :class:`PresetNotFoundError` if
        absent."""
        ...

    async def get_active_kwargs(self, name: str) -> dict[str, Any]:
        """Return the active version's baked ``fixed_kwargs``. Raise
        :class:`PresetNotFoundError` if absent."""
        ...

    async def list_versions(self, name: str) -> list[DocumentVersion]:
        """List every version of the preset, each carrying its ``is_current``
        signal. Raise :class:`PresetNotFoundError` if the preset is absent."""
        ...

    async def get_version(self, name: str, version: int) -> DocumentVersion:
        """Fetch one version. Raise :class:`PresetVersionNotFoundError` if that
        version does not exist."""
        ...

    async def get_active_body(self, name: str) -> PresetBody:
        """Return the FULL active-version body (``{base_tool, description,
        fixed_kwargs, extensions, tags}``) so reload/startup can re-register from
        the whole body, not just ``fixed_kwargs``. Raise
        :class:`PresetNotFoundError` if absent."""
        ...

    async def rollback(self, name: str, version: int) -> DocumentRecord:
        """Re-point the active version to ``version`` (no data copy). Raise
        :class:`PresetVersionNotFoundError` if that version does not exist."""
        ...

    async def soft_delete(self, name: str) -> None:
        """Soft-delete the preset, keeping its version history (audit). Raise
        :class:`PresetNotFoundError` if absent."""
        ...

    async def rename_preset(self, name: str, new_name: str) -> DocumentRecord:
        """Re-key a preset from ``name`` to ``new_name``, delegating to the generic
        store's rename under ``kind="preset"``. The version history, every per-version
        ``tags`` label, and the ``active_version`` pointer are preserved by the store
        contract — a rename moves a key, it never rewrites the body. Raise
        :class:`PresetNotFoundError` for an absent ``name``, :class:`PresetExistsError`
        when ``new_name`` is already a live preset, and :class:`PresetNameConflictError`
        when the injected collision predicate says ``new_name`` is held by a live
        non-preset tool (the same predicate :meth:`create_preset` consults)."""
        ...


__all__ = [
    "CARRY_FORWARD",
    "CarryForward",
    "PresetBody",
    "PresetError",
    "PresetExistsError",
    "PresetNameConflictError",
    "PresetNotFoundError",
    "PresetSpec",
    "PresetStore",
    "PresetVersionNotFoundError",
]
