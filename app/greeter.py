# Чисто бизнес-логика: формируем приветствие.
# Вынесено отдельно, чтобы было что тестить юнит-тестами.
from __future__ import annotations


def greet(name: str) -> str:
    # Имя обязательное и непустое — иначе шлём ValueError, чтобы линтер/тесты
    # реально проверили негативный путь, а не только happy-path.
    if not name or not name.strip():
        raise ValueError("name must be a non-empty string")
    return f"Hi, {name.strip()}"
