from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from tai42_contract.template import ConditionMixin


class IdentityRecord(BaseModel):
    """Schema for data stored at 'ac:key:{hash}'. Represents purely WHO the user is."""

    user_id: str

    # Extra fields (email, org_id, etc.) are treated as identity claims
    model_config = ConfigDict(extra="allow")


class AccessPolicy(ConditionMixin):
    """Schema for data stored at 'ac:policy:{user_id}'. Represents WHAT the user
    can do (permissions & logic)."""

    scopes: list[str] = Field(default_factory=list)

    # Static data required for policy decisions (e.g., {"plan_limit": 100})
    policy_data: dict[str, Any] = Field(default_factory=dict)

    # Note: 'condition' field is provided by ConditionMixin


class JqAuthContext(BaseModel):
    """The unified JSON object passed to JQ for evaluation."""

    # Standard Claims
    sub: str = "anon"
    scopes: list[str] = Field(default_factory=list)

    # IDENTITY: Who they are (mapped from AccessToken.claims)
    identity: dict[str, Any] = Field(default_factory=dict)

    # POLICY: Static rules assigned to them (from AccessPolicy)
    policy: dict[str, Any] = Field(default_factory=dict)

    # CONTEXT: Dynamic environment data (from Redis ac:context:...)
    context: dict[str, Any] = Field(default_factory=dict)

    # REQUEST: The current operation
    request: dict[str, Any] = Field(default_factory=dict)

    # SYSTEM: caller-supplied time/constants (e.g. {"time": <epoch seconds>})
    system: dict[str, float] = Field(default_factory=dict)
