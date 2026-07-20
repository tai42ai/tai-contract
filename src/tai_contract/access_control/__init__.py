"""Access-control contract: identity, policy/context models, and the ``Verifier``
/ ``PolicyEnforcer`` protocols."""

from __future__ import annotations

from tai_contract.access_control.context import (
    get_current_user_id,
    reset_request_user_id,
    set_request_user_id,
)
from tai_contract.access_control.identity import (
    OWNER_USER_ID_CLAIM,
    ApiKeyIdentityProvider,
    AuthIdentity,
    IdentityProvider,
    IdentityProviderSettings,
)
from tai_contract.access_control.models import (
    AccessPolicy,
    IdentityRecord,
    JqAuthContext,
)
from tai_contract.access_control.policy import PolicyEnforcer
from tai_contract.access_control.registry import (
    get_identity_provider_factory,
    register_identity_provider,
    reset_registry,
)
from tai_contract.access_control.verifier import Verifier

__all__ = [
    "OWNER_USER_ID_CLAIM",
    "AccessPolicy",
    "ApiKeyIdentityProvider",
    "AuthIdentity",
    "IdentityProvider",
    "IdentityProviderSettings",
    "IdentityRecord",
    "JqAuthContext",
    "PolicyEnforcer",
    "Verifier",
    "get_current_user_id",
    "get_identity_provider_factory",
    "register_identity_provider",
    "reset_registry",
    "reset_request_user_id",
    "set_request_user_id",
]
