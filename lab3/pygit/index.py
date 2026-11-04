import os
from typing import Tuple, List
from lab3.constants import PYGIT_DIRECTORY
from lab3.pygit.find_root import find_repo_root


def get_index_path(cwd: str | None = None) -> str | None:
    if cwd is None:
        cwd = os.getcwd()
    repo_root = find_repo_root(cwd)
    if repo_root is None:
        return None
    return os.path.join(repo_root, PYGIT_DIRECTORY, 'index')


def read_index() -> List[Tuple[str, str, str]]:
    """ Читает .pygit/index и возвращает список (path, sha, mode) """
    repo = os.getcwd()
    index_path = get_index_path(repo)
    entries: List[Tuple[str, str, str]] = list()
    if index_path is None:
        return entries
    if not os.path.exists(index_path):
        return entries
    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            path, sha, mode = line.split(" ", 2)
            entries.append((path, sha, mode))
    return entries


def write_index(entries: List[Tuple[str, str, str]]) -> None:
    repo = os.getcwd()
    index_path = get_index_path(repo)
    if not index_path:
        return

    if not entries:
        with open(index_path, 'w', encoding='utf-8'):
            pass
        return

    lines = []
    for path, sha, mode in entries:
        lines.append(f'{path} {sha} {mode}\n')

    with open(index_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    return None


def update_index(path: str, sha: str, mode: str) -> None:
    entries: List[Tuple[str, str, str]] = read_index()
    updated = False
    for i, (p, old_sha, old_mode) in enumerate(entries):
        if p == path:
            entries[i] = (path, sha, mode)
            updated = True
            break

    if not updated:
        entries.append((path, sha, mode))

    write_index(entries)
