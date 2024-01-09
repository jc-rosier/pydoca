import abc

import pytest

import pydoca


class EmailService(pydoca.Service):
    @abc.abstractmethod
    def send_email(self, message: str) -> None:
        """Sends an email."""


class FakeEmailService(EmailService):
    def send_email(self, message: str) -> None:
        print(message)
        return


def test_port_registry():
    # Declaring EmailService class should register it
    assert pydoca.Port._registry["EmailService"] == EmailService


def test_factory_bind():
    pydoca.bind(EmailService, FakeEmailService)
    assert isinstance(pydoca.inject(EmailService), FakeEmailService)


def test_adapter_bind():
    # Test provider bind and configuration override
    email_svc = FakeEmailService()
    pydoca.bind(EmailService, email_svc)
    assert pydoca.inject(EmailService) == email_svc


def test_clear_and_error():
    pydoca.bind(EmailService, FakeEmailService)
    pydoca.clear()

    with pytest.raises(
        pydoca.AdapterNotConfiguredError,
        match="Adapter for EmailService port not configured",
    ):
        pydoca.inject(EmailService)
