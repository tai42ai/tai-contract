"""tai-contract — pure interface contracts for the TAI ecosystem.

Protocols, ABCs, and pydantic models only. No logic. At runtime this package
imports nothing but ``pydantic``; vendor types are ``TYPE_CHECKING``-only.

The primary entry points are re-exported here: the assembled ``TaiApp`` facade
and its runtime forwarding handle ``tai_app``, plus the names most consumers
need (``Agent``, ``Manifest``, ``ToolInfo``, ``Storage``, ``Backend``, and the
shared exception types). Everything else stays in its subpackage.
"""

from __future__ import annotations

from importlib.metadata import version

from tai_contract.agent import Agent
from tai_contract.app import TaiApp, tai_app
from tai_contract.backend import Backend
from tai_contract.errors import ClientDisconnectedError
from tai_contract.manifest import Manifest
from tai_contract.storage import Storage
from tai_contract.tools import ToolInfo

__version__ = version("tai-contract")

__all__ = [
    "Agent",
    "Backend",
    "ClientDisconnectedError",
    "Manifest",
    "Storage",
    "TaiApp",
    "ToolInfo",
    "__version__",
    "tai_app",
]
