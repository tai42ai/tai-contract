from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from tai_contract.template import ConditionMixin, ExprMixin


class TopicVerifierBinding(BaseModel):
    """A per-topic webhook-verifier binding: the name of a registered verifier
    plus its per-topic ``config``.

    This is the persisted shape a hooks manager stores for a topic. ``verifier``
    names a registered :class:`~tai_contract.webhooks.WebhookVerifier`; ``config``
    is that verifier's per-binding configuration and NEVER holds a secret value —
    only a ``secret_env`` naming the environment variable that does. The model is
    frozen so a validated binding cannot be mutated after it is read back.
    """

    model_config = ConfigDict(frozen=True)

    verifier: str = Field(min_length=1)
    config: dict[str, Any] = Field(default_factory=dict)


class HookParams(ConditionMixin, ExprMixin):
    name: str
    topic: str
    tool: str
    tool_kwargs: dict[str, Any] = Field(default_factory=dict)

    # ``expr``/``expr_id``/``condition``/``condition_id`` come from the mixins;
    # the ``*_kwargs`` fields are re-declared non-optional (hooks default them
    # to {} and never carry None).
    expr_kwargs: dict[str, Any] = Field(default_factory=dict)  # pyright: ignore[reportIncompatibleVariableOverride]
    condition_kwargs: dict[str, Any] = Field(default_factory=dict)  # pyright: ignore[reportIncompatibleVariableOverride]
