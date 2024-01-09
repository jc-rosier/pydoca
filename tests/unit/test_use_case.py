import abc

import pytest

import pydoca


def test_use_case_no_dependencies():
    class UseCaseNoDependency(pydoca.UseCase):
        def exec(self, cmd: pydoca.Command) -> str:
            return "result"

    assert UseCaseNoDependency().exec(pydoca.Command()) == "result"


class Dependency(pydoca.Service):
    """Define an abstract class representing a dependency."""

    @abc.abstractmethod
    def some_method(self) -> str:
        """Returns some string."""


class DependencyImpl(Dependency):
    def some_method(self) -> str:
        return "Real implementation"


def test_use_case_with_dependencies():
    pydoca.bind(Dependency, DependencyImpl)

    class UseCaseWithDependencies(pydoca.UseCase):
        service: Dependency  # Should be injected
        name: str  # Passed in the UC init, shouldn't be injected

        def exec(self, cmd: pydoca.Command) -> str:
            return self.service.some_method()

    assert (
        UseCaseWithDependencies(name="test").exec(pydoca.Command())
        == "Real implementation"
    )


def test_use_case_missing_dependencies():
    class UseCaseWithDependencies(pydoca.UseCase):
        service: Dependency

        def exec(self, cmd: pydoca.Command) -> str:
            return self.service.some_method()

    with pytest.raises(
        pydoca.AdapterNotConfiguredError,
        match="Adapter for Dependency port not configured",
    ):
        UseCaseWithDependencies().exec(pydoca.Command())
