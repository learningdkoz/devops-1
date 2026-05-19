# Юнит-тесты на greeter — отрабатываем gate CI-10 (Unit Tests) и CI-11 (Coverage).
from __future__ import annotations

import pytest

from app.greeter import greet


def test_greet_basic():
    assert greet("World") == "Hi, World"


def test_greet_strips_whitespace():
    # Пробелы по краям обрезаем — мелочь, но без теста легко проворонить.
    assert greet("  Vasya  ") == "Hi, Vasya"


@pytest.mark.parametrize("bad", ["", "   ", "\t\n"])
def test_greet_rejects_empty(bad: str):
    # Негативный путь — без него coverage и mutation testing будут красные.
    with pytest.raises(ValueError):
        greet(bad)
