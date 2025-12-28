from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TestProtocol(Protocol):
    a: int


class TestClass:
    a: int = 5


print(issubclass(TestClass, TestProtocol))  # True
