"""``tai_app`` — the runtime forwarding handle.

The one whitelisted behavioral member of the otherwise-pure contract: a minimal,
dependency-free stand-in that forwards attribute access to the concrete app impl,
injected once at startup via ``tai_app.bind(impl)``. No third-party deps, no
business logic — only forwarding. Attribute access before ``bind`` raises loudly,
never a silent ``None``.
"""

from __future__ import annotations

from typing import Any


class _TaiAppHandle:
    """Forwards attribute access to the bound app impl; raises before ``bind``."""

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl: Any = None

    def bind(self, impl: object) -> None:
        """Inject the concrete app impl. The runtime calls this once at startup."""
        self._impl = impl

    def __getattr__(self, name: str) -> Any:
        # __getattr__ runs only when normal lookup misses (i.e. not _impl/bind),
        # so every real app member routes here and forwards to the impl. Raising
        # AttributeError (not RuntimeError) keeps the attribute protocol intact:
        # hasattr/getattr(default)/inspect probes report absence loudly instead
        # of crashing, while the message still names the missing-bind cause.
        impl = object.__getattribute__(self, "_impl")
        if impl is None:
            raise AttributeError(
                f"tai_app accessed before bind(): cannot resolve {name!r}. "
                "The runtime must call tai_app.bind(app) at startup."
            )
        return getattr(impl, name)


tai_app = _TaiAppHandle()

__all__ = ["tai_app"]
