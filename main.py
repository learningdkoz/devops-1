# Точка входа для совместимости со старым запуском `python main.py`.
# Под капотом — пакет app, чтобы по нему можно было гонять тесты и пайплайн.
from app.greeter import greet


def print_hi(name: str) -> None:
    # Тупой Hello-World — реальный код тут не нужен, важна сама обвязка трубы.
    print(greet(name))


if __name__ == "__main__":
    print_hi("PyCharm")
