import os
from lab3.constants import PYGIT_DIRECTORY
from lab3.pygit.find_root import find_repo_root


def get_ref_path() -> str | None:
    """
    Функция, которая читает путь из указателя HEAD
    """
    repo_root = find_repo_root(os.getcwd())
    if repo_root is None:
        return None
    head_path = os.path.join(repo_root, PYGIT_DIRECTORY, 'HEAD')

    if not os.path.exists(head_path):
        print(f'Не смогли найти указатель HEAD по пути {head_path}')
        return None

    with open(head_path, 'r', encoding='utf-8') as f:
        line = f.read().strip()

    if not line.startswith('ref: '):
        print('Некорректное содержимое HEAD')
        return None

    ref = line[len('ref: '):]
    ref_path = os.path.join(repo_root, PYGIT_DIRECTORY, *ref.split('/'))
    return ref_path


def read_current_commit() -> str | None:
    """
    Функция, которая находит хеш последнего коммита,
    читая файл, на который указывает HEAD.
    """
    ref_path = get_ref_path()
    if ref_path is None or not os.path.exists(ref_path):
        return None
    with open(ref_path, 'r', encoding='utf-8') as f:
        sha = f.read().strip()
    if sha == '':
        return None
    return sha
