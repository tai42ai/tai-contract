"""Tests for the channel contract types.

The ``AppChannels`` protocol membership is covered by the frozen-facade
partition test; here we pin the typed error, the ``Channel`` Protocol shape
(``deliver`` + ``notify``), the ``ChannelDelivery`` model's frozen +
per-format + recipient validation, the ``ChannelNotification`` model's
frozen + message + recipient + sender_identity validation, the ``notify``
list-of-ids return, and the ``AskUser`` ``channel`` / ``recipient`` keywords.
"""

from __future__ import annotations

import asyncio
import inspect
from datetime import UTC, datetime
from typing import Any

import pytest


def _delivery_kwargs(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "interaction_id": "int-1",
        "question": "Approve the deploy?",
        "answer_format": "text",
        "callback_url": "https://host.example/api/interactions/callback/tkt",
        "timeout_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return base


def test_delivery_error_is_a_distinct_exception_type():
    from tai42_contract.channels import ChannelDeliveryError

    assert issubclass(ChannelDeliveryError, Exception)
    # A distinct type so the ask helper can catch delivery failure without also
    # swallowing unrelated errors.
    assert ChannelDeliveryError is not Exception
    with pytest.raises(ChannelDeliveryError):
        raise ChannelDeliveryError("send rejected")


def test_channel_protocol_is_runtime_checkable_and_shaped():
    from tai42_contract.channels import Channel, ChannelDelivery, ChannelNotification

    class _Ok:
        async def deliver(self, delivery: ChannelDelivery) -> None:
            return None

        async def notify(self, notification: ChannelNotification) -> None:
            return None

    class _DeliverOnly:
        async def deliver(self, delivery: ChannelDelivery) -> None:
            return None

    class _Missing:
        pass

    assert isinstance(_Ok(), Channel)
    # ``notify`` is a required protocol member, not an optional extra.
    assert not isinstance(_DeliverOnly(), Channel)
    assert not isinstance(_Missing(), Channel)


def test_deliver_is_a_coroutine_signature():
    from tai42_contract.channels import Channel

    assert inspect.iscoroutinefunction(Channel.deliver)
    sig = inspect.signature(Channel.deliver)
    assert list(sig.parameters) == ["self", "delivery"]


def test_notify_is_a_coroutine_signature():
    from tai42_contract.channels import Channel

    assert inspect.iscoroutinefunction(Channel.notify)
    sig = inspect.signature(Channel.notify)
    assert list(sig.parameters) == ["self", "notification"]


def test_notify_returns_a_list_of_message_ids():
    from tai42_contract.channels import Channel

    # ``notify`` yields the per-message ids the medium assigned the send, so an
    # out-of-band delivery receipt can be correlated back to what was sent.
    sig = inspect.signature(Channel.notify)
    assert sig.return_annotation == "list[str]"


def test_notify_protocol_default_raises_not_implemented():
    from tai42_contract.channels import Channel, ChannelDelivery, ChannelNotification

    class _DeliverCapableOnly(Channel):
        """Explicit subclass keeping the inherited ``notify`` default body."""

        async def deliver(self, delivery: ChannelDelivery) -> None:
            return None

    # Pyright treats the ``raise NotImplementedError`` protocol body as abstract;
    # the contract supplies it as a real, loud default, so instantiating is intended.
    channel = _DeliverCapableOnly()  # pyright: ignore[reportAbstractUsage]
    with pytest.raises(NotImplementedError):
        asyncio.run(channel.notify(ChannelNotification(message="ping")))


def test_notification_model_is_frozen():
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelNotification

    notification = ChannelNotification(message="deploy finished")
    with pytest.raises(ValidationError):
        notification.message = "changed"


@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
def test_notification_rejects_blank_message(blank: str):
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelNotification

    with pytest.raises(ValidationError, match="non-blank"):
        ChannelNotification(message=blank)


def test_notification_recipient_defaults_to_none_and_accepts_an_address():
    from tai42_contract.channels import ChannelNotification

    assert ChannelNotification(message="hi").recipient is None
    assert ChannelNotification(message="hi", recipient="@ops-team").recipient == "@ops-team"


@pytest.mark.parametrize("empty", ["", "   ", "\t\n"])
def test_notification_recipient_rejects_empty_when_present(empty: str):
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelNotification

    with pytest.raises(ValidationError, match="non-empty address"):
        ChannelNotification(message="hi", recipient=empty)


def test_notification_sender_identity_defaults_to_none_and_accepts_an_address():
    from tai42_contract.channels import ChannelNotification

    assert ChannelNotification(message="hi").sender_identity is None
    assert ChannelNotification(message="hi", sender_identity="+15550001111").sender_identity == "+15550001111"


@pytest.mark.parametrize("empty", ["", "   ", "\t\n"])
def test_notification_sender_identity_rejects_empty_when_present(empty: str):
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelNotification

    with pytest.raises(ValidationError, match="non-empty address"):
        ChannelNotification(message="hi", sender_identity=empty)


def test_delivery_model_is_frozen():
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelDelivery

    delivery = ChannelDelivery(**_delivery_kwargs())
    with pytest.raises(ValidationError):
        delivery.question = "changed"


def test_delivery_select_requires_options():
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelDelivery

    with pytest.raises(ValidationError, match="non-empty options"):
        ChannelDelivery(**_delivery_kwargs(answer_format="select"))
    ok = ChannelDelivery(**_delivery_kwargs(answer_format="select", options=["yes", "no"]))
    assert ok.options == ["yes", "no"]


def test_delivery_non_select_forbids_options():
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelDelivery

    with pytest.raises(ValidationError, match="carries no options"):
        ChannelDelivery(**_delivery_kwargs(options=["stray"]))


def test_delivery_unknown_answer_format_rejected():
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelDelivery

    with pytest.raises(ValidationError, match="answer_format"):
        ChannelDelivery(**_delivery_kwargs(answer_format="carrier-pigeon"))


def test_delivery_form_answer_format_rejected():
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelDelivery

    # "form" is a valid AnswerFormat but not channel-deliverable: a multi-field
    # form has no single-reply mapping, so the model itself rejects it.
    with pytest.raises(ValidationError, match="answer_format"):
        ChannelDelivery(**_delivery_kwargs(answer_format="form"))


def test_delivery_recipient_defaults_to_none_and_accepts_an_address():
    from tai42_contract.channels import ChannelDelivery

    assert ChannelDelivery(**_delivery_kwargs()).recipient is None
    assert ChannelDelivery(**_delivery_kwargs(recipient="@ops-team")).recipient == "@ops-team"


@pytest.mark.parametrize("empty", ["", "   ", "\t\n"])
def test_delivery_recipient_rejects_empty_when_present(empty: str):
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelDelivery

    with pytest.raises(ValidationError, match="non-empty address"):
        ChannelDelivery(**_delivery_kwargs(recipient=empty))


def test_delivery_timeout_must_be_tz_aware():
    from pydantic import ValidationError

    from tai42_contract.channels import ChannelDelivery

    with pytest.raises(ValidationError, match="timezone-aware"):
        ChannelDelivery(**_delivery_kwargs(timeout_at=datetime(2026, 1, 1)))


def test_ask_user_accepts_channel_and_recipient_keywords():
    from tai42_contract.interactions.asker import AskUser

    params = inspect.signature(AskUser.__call__).parameters
    for name in ("channel", "recipient"):
        assert params[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert params[name].default is None
    # ``recipient`` sits between ``channel`` and ``sensitive`` in the ordered
    # call surface.
    ordered = list(params)
    assert ordered[ordered.index("channel") + 1] == "recipient"
    assert ordered[ordered.index("recipient") + 1] == "sensitive"
