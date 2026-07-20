"""The assembled ``TaiApp`` facade.

One ``Protocol`` per feature (see :mod:`tai_contract.app.facets`), composed into
a single ``TaiApp`` protocol that exposes them as namespaces (``app.tools``,
``app.agents``, ...). The app members are partitioned across the
sub-protocols — each lives in exactly one, save the shared leaf names
``store`` (``versioning`` + ``presets``) and ``register``/``get``
(``webhook_verifiers`` + ``channels``). The runtime forwarding handle is
``tai_app`` (see :mod:`tai_contract.app.handle`).
"""

from __future__ import annotations

from typing import Protocol, cast, runtime_checkable

from tai_contract.tools import AppTools

from .facets import (
    AppAdmin,
    AppAgents,
    AppBackends,
    AppBackup,
    AppChannels,
    AppClients,
    AppConfig,
    AppConnectors,
    AppExtensions,
    AppHttp,
    AppLifecycle,
    AppMonitoring,
    AppPresets,
    AppStorage,
    AppSubApp,
    AppVersioning,
    AppWebhookVerifiers,
)
from .handle import tai_app as _tai_app_handle


@runtime_checkable
class TaiApp(Protocol):
    """The assembled facade — per-feature sub-protocols exposed as namespaces."""

    @property
    def tools(self) -> AppTools: ...

    @property
    def agents(self) -> AppAgents: ...

    @property
    def backends(self) -> AppBackends: ...

    @property
    def storage(self) -> AppStorage: ...

    @property
    def connectors(self) -> AppConnectors: ...

    @property
    def webhook_verifiers(self) -> AppWebhookVerifiers: ...

    @property
    def channels(self) -> AppChannels: ...

    @property
    def monitoring(self) -> AppMonitoring: ...

    @property
    def extensions(self) -> AppExtensions: ...

    @property
    def http(self) -> AppHttp: ...

    @property
    def clients(self) -> AppClients: ...

    @property
    def lifecycle(self) -> AppLifecycle: ...

    @property
    def admin(self) -> AppAdmin: ...

    @property
    def config(self) -> AppConfig: ...

    @property
    def backup(self) -> AppBackup: ...

    @property
    def sub_app(self) -> AppSubApp: ...

    @property
    def versioning(self) -> AppVersioning: ...

    @property
    def presets(self) -> AppPresets: ...


class _TaiAppRuntime(TaiApp, Protocol):
    """The runtime forwarding handle: the assembled ``TaiApp`` facade plus the
    startup binder the runtime calls once to inject the concrete app impl."""

    def bind(self, impl: object) -> None: ...


# The runtime object is the forwarding handle; consumers see it typed as the
# assembled facade (so ``tai_app.tools`` etc. carry their real types instead of
# the handle's ``__getattr__ -> Any``) plus ``bind`` for the startup wiring.
# ``cast`` is a runtime no-op.
tai_app: _TaiAppRuntime = cast("_TaiAppRuntime", _tai_app_handle)


__all__ = [
    "AppAdmin",
    "AppAgents",
    "AppBackends",
    "AppBackup",
    "AppChannels",
    "AppClients",
    "AppConfig",
    "AppConnectors",
    "AppExtensions",
    "AppHttp",
    "AppLifecycle",
    "AppMonitoring",
    "AppPresets",
    "AppStorage",
    "AppSubApp",
    "AppTools",
    "AppVersioning",
    "AppWebhookVerifiers",
    "TaiApp",
    "tai_app",
]
