import os
import sys
from lab3.pygit.find_root import find_repo_root
from lab3.pygit.write_tree_logic import write_tree
from typing import List, Dict, Optional, Callable
from lab3.constants import PYGIT_DIRECTORY, BLOB_MODE
from lab3.pygit.index import update_index
from lab3.pygit.objects import Blob, Commit, hash_object, CommitHistoryIterator
from lab3.pygit.commit_logic import read_current_commit, get_ref_path


CommandFunc = Callable[[List[str]], None]
COMMANDS: Dict[str, CommandFunc] = {}


def command(name: str) -> Callable[[CommandFunc], CommandFunc]:
    """ Декоратор: регистрирует функцию как обработчик команды name """
    def decorator(func: CommandFunc) -> CommandFunc:
        COMMANDS[name] = func
        return func
    return decorator


@command('init')
def init(args: Optional[List[str]] = None) -> None:
    if args is None:
        args = []
    if len(args) > 1:
        print('Введите только один путь для репозитория')
        return
    if args:
        path = args[0]
    else:
        path = '.'
    init_repository(path)


@command('add')
def add(args: List[str]) -> None:
    if not args:
        print('Укажите файл для добавления')
        return

    if len(args) > 1:
        print('Добавляйте 1 файл, пожалуйста')
        return

    filename = args[0]
    add_file(filename)


@command('commit')
def commit(args: List[str]) -> None:
    if len(args) < 2 or args[0] != "-m":
        print('Неверный формат. Попробуйте: pygit commit -m "сообщение"')
        return
    message = args[1]
    make_commit(message)


@command('log')
def log(args: List[str]) -> None:
    cmd_log()


@command('write-tree')
def cmd_write_tree(args: List[str]) -> None:
    print(write_tree())


def init_repository(path: str = '.') -> None:
    """ Инициализация нового pygit-репозитория в указанной директории """
    repository_root = os.path.abspath(path)
    pygit_dir = os.path.join(repository_root, PYGIT_DIRECTORY)
    objects_dir = os.path.join(pygit_dir, 'objects')
    refs_heads_dir = os.path.join(pygit_dir, 'refs', 'heads')
    head_file = os.path.join(pygit_dir, 'HEAD')

    if os.path.exists(pygit_dir):
        print(f'В {repository_root} уже есть репозиторий {PYGIT_DIRECTORY}')
        return None

    os.makedirs(objects_dir, exist_ok=True)
    os.makedirs(refs_heads_dir, exist_ok=True)

    with open(head_file, 'w', encoding='utf-8') as file:
        file.write("ref: refs/heads/main\n")

    print(f'Инициализирован пустой репозиторий в {repository_root}')
    return None


def add_file(filename: str) -> None:
    repo = os.getcwd()
    root_repo = find_repo_root(repo)
    if root_repo is None:
        return None
    file_path = os.path.join(repo, filename)
    with open(file_path, 'rb') as f:
        data = f.read()

    blob = Blob(data)
    sha = hash_object(blob.serialize(), 'blob')

    index_path = os.path.relpath(file_path, root_repo)
    update_index(index_path, sha, BLOB_MODE)
    print('Индекс обновлен')


def make_commit(message: str = '', author: str = 'mary@itmo') -> None:

    parent_tree = write_tree()
    parent_sha = read_current_commit()
    commit_object = Commit(
        tree_hash=parent_tree, parent_hash=parent_sha,
        author=author, message=message
    )
    commit_sha = hash_object(commit_object.serialize(), 'commit')
    print(f'Коммит создан: {commit_sha}')

    ref_path = get_ref_path()
    if ref_path is None:
        return None
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, 'w', encoding='utf-8') as f:
        f.write(commit_sha + '\n')


def cmd_log() -> None:
    head_sha = read_current_commit()
    if head_sha is None:
        print('Вы еще не сделали ни одного коммита')
        return
    commit_iter = CommitHistoryIterator(head_sha)

    for sha, commit in commit_iter:
        print(f'commit {sha}, автор: {commit.author}\n')


def main() -> None:
    if len(sys.argv) < 2:
        print("Укажите одну из команд: init, add, commit, log")
        return

    cmd_name = sys.argv[1]
    args = sys.argv[2:]

    handler = COMMANDS.get(cmd_name)
    if handler is None:
        print(f'Неизвестная команда: {cmd_name}')
        return

    handler(args)


if __name__ == "__main__":
    main()
