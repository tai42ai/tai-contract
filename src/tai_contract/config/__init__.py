"""Configuration contract: the ``ConfigManager`` ABC and the settings
cache-accessor protocol (concrete settings primitives live in the implementing
layer)."""

from __future__ import annotations

from tai_contract.config.manager import ConfigManager
from tai_contract.config.settings import SettingsCacheRegistry

__all__ = ["ConfigManager", "SettingsCacheRegistry"]
