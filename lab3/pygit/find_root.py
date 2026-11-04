import os
from lab3.constants import PYGIT_DIRECTORY


def find_repo_root(start: str) -> str | None:
    """
    Команда, помогающая найти корневую директорию репозитория,
    чтобы команды можно было запускать и находясь в ее поддиректориях
    """
    current = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(current, PYGIT_DIRECTORY)):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            print('Здесь нет репозитория')
            return None
        current = parent
