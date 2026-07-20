"""Execution-backend contract: the ``Backend`` ABC + the ``CallbackSchema``."""

from __future__ import annotations

from tai_contract.backend.base import Backend
from tai_contract.backend.callback import CallbackSchema

__all__ = ["Backend", "CallbackSchema"]
