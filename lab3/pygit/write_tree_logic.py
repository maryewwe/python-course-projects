from typing import Dict, List, Tuple, Generator
from lab3.constants import BLOB_MODE, TREE_MODE
from lab3.pygit.index import read_index
from collections import defaultdict
from lab3.pygit.objects import TreeEntry, Tree, hash_object


def group_by_directory() -> Dict[str, List[Tuple[str, str, str]]]:
    """
    Функция, которая считывает записи из индекса и на их основе создает
    группы: словарь, где для каждой поддиректории
    """
    entries: List[Tuple[str, str, str]] = read_index()
    grouped: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)

    for path, sha, mode in entries:
        if "/" in path:
            dir_path, _ = path.rsplit("/", 1)
        else:
            dir_path, _ = "", path

        grouped[dir_path].append((path, sha, mode))

    return grouped


def recursive_walk(groups: Dict[str, List[Tuple[str, str, str]]],
                   current_dir: str = "") -> Generator[str, None, None]:
    """
    Генератор, который выдаёт строки с путями директорий
    снизу вверх: сначала самые глубокие поддиректории,
    в конце — корневая директория. Рекурсивно обходит структуру директорий
    и возвращает пути директорий.
    """
    if current_dir:
        prefix = current_dir + '/'
    else:
        prefix = ''
    subdirs = set()
    for dir_path in groups.keys():
        if dir_path.startswith(prefix) and dir_path != current_dir:
            rest = dir_path[len(prefix):]
            if "/" not in rest:
                subdirs.add(dir_path)

    for sub in sorted(subdirs):
        for entry in recursive_walk(groups, sub):
            yield entry

    yield current_dir


def build_file_entries(groups: Dict[str, List[Tuple[str, str, str]]],
                       dir_path: str) -> List[TreeEntry]:
    """
    Функция, которая собирает TreeEntry записи для файлов
    внутри директории dir_path
    """
    entries: List[TreeEntry] = []
    for full_path, sha, mode in groups.get(dir_path, []):
        if "/" in full_path:
            _, name = full_path.rsplit("/", 1)
        else:
            name = full_path
        entries.append(TreeEntry(mode=BLOB_MODE, path=name, sha=sha))
    return entries


def find_child_dirs(groups: Dict[str, List[Tuple[str, str, str]]],
                    dir_path: str) -> List[str]:
    """ Функция, которая находит непосредственные
    поддиректории для dir_path (директории, которые на одну ступень в
    иерархии ниже) """
    if dir_path:
        prefix = dir_path + '/'
    else:
        prefix = ''
    child_dirs: set[str] = set()
    for other_dir in groups.keys():
        if other_dir.startswith(prefix) and other_dir != dir_path:
            rest = other_dir[len(prefix):]
            if "/" not in rest:
                child_dirs.add(other_dir)
    return sorted(child_dirs)


def add_child_trees(entries_tree: List[TreeEntry],
                    child_dirs: List[str],
                    dir_tree_sha: Dict[str, str]) -> None:
    """ Добавляет в entries_tree ссылки на поддеревья из dir_tree_sha """
    for child_dir in child_dirs:
        if child_dir:
            name = child_dir.split("/")[-1]
        else:
            name = ''
        child_tree_sha = dir_tree_sha[child_dir]
        entries_tree.append(TreeEntry(mode=TREE_MODE, path=name,
                                      sha=child_tree_sha))


def write_tree() -> str:
    """
    Строит и сохраняет tree-объекты на основе записей в индексе
    и возвращает SHA корневого tree.
    """
    groups = group_by_directory()
    dir_tree_sha: Dict[str, str] = {}

    for dir_path in recursive_walk(groups, ""):
        entries_tree = build_file_entries(groups, dir_path)

        child_dirs = find_child_dirs(groups, dir_path)
        add_child_trees(entries_tree, child_dirs, dir_tree_sha)

        if not entries_tree and dir_path != "":
            continue

        entries_tree.sort(key=lambda x: x.path)
        tree_object = Tree(entries_tree)
        tree_sha = hash_object(tree_object.serialize(), "tree")
        dir_tree_sha[dir_path] = tree_sha

    return dir_tree_sha[""]
