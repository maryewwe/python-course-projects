import os
import hashlib
import zlib
from abc import ABC, abstractmethod
from typing import Type, TypeVar, List, Iterator, Tuple
from dataclasses import dataclass
from lab3.constants import PYGIT_DIRECTORY


T = TypeVar('T', bound='GitObject')


class GitObject(ABC):
    """
    Абстрактный базовый класс для pygit.
    Он устанавливает, что любой pygit объект должен иметь методы
    serialize и deserialize
    """
    @abstractmethod
    def serialize(self) -> bytes:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls: Type[T], data: bytes) -> T:
        raise NotImplementedError


class Blob(GitObject):
    """ Класс, представляющий объект blob """
    def __init__(self, data: bytes):
        self.data = data

    def serialize(self) -> bytes:
        """ Сериализация Blob - это его содержимое """
        return self.data

    @classmethod
    def deserialize(cls, data: bytes) -> "Blob":
        """ Из байтов, прочитанных из файла, возвращает новый объект Blob """
        return cls(data)


@dataclass
class TreeEntry:
    """
    Мини-класс для удобного хранения данных
    (использую вместо кортежа)
    """
    mode: str
    path: str
    sha: str


class Tree(GitObject):
    """
    Класс, представляющий объект tree
    """
    def __init__(self, entries: List[TreeEntry] | None = None):
        if entries is None:
            entries = []
        self.entries = entries

    def serialize(self) -> bytes:
        """
        Сериализация объекта tree - это конкатенация (склейка)
        записей вида '<mode> <name>\0'
        """
        body = b""
        for entry in self.entries:
            header = f'{entry.mode} {entry.path}'.encode('utf-8') + b'\x00'
            sha_bytes = bytes.fromhex(entry.sha)

            if len(sha_bytes) != 20:
                raise ValueError('SHA-1 должен быть 20 байт')
            body += header + sha_bytes
        return body

    @classmethod
    def deserialize(cls, data: bytes) -> "Tree":
        """
        Из байтовых данных возвращает Tree с заполненными записями
        TreeEntry
        """
        entries: List[TreeEntry] = []
        idx = 0
        while idx < len(data):
            end = data.index(b"\x00", idx)
            header = data[idx:end].decode('utf-8')
            mode, path = header.split(' ', 1)
            sha_start = end + 1
            sha_end = sha_start + 20
            sha_bytes = data[sha_start:sha_end]
            sha_hex = sha_bytes.hex()
            entries.append(TreeEntry(mode=mode, path=path, sha=sha_hex))
            idx = sha_end
        return cls(entries)


class Commit(GitObject):
    """ Класс, представляющий объект commit """
    def __init__(self, tree_hash: str | None, parent_hash: str | None,
                 author: str | None,  message: str):
        self.tree_hash = tree_hash
        self.parent_hash = parent_hash
        self.author = author
        self.message = message

    def serialize(self) -> bytes:
        """
        Преобразует коммит в байтовое представление формата git.
        Формирует текст вида:
        'tree <sha> \n parent <sha>\n author <sha>\n message<sha>\n'
        и кодирует его в UTF-8.
        """
        lines = list()
        lines.append(f'tree {self.tree_hash}')
        if self.parent_hash is not None:
            lines.append(f'parent {self.parent_hash}')
        lines.append(f'author {self.author}')

        header_text = "\n".join(lines)
        full_text = header_text + "\n\n" + self.message
        return full_text.encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes) -> "Commit":
        text = data.decode("utf-8")
        header_text, message = text.split("\n\n", 1)

        tree_hash = None
        parent_hash = None
        author = None

        for line in header_text.splitlines():
            if line.startswith("tree "):
                tree_hash = line[len("tree "):].strip()
            elif line.startswith("parent "):
                parent_hash = line[len("parent "):].strip()
            elif line.startswith("author "):
                author = line[len("author "):].strip()

        if tree_hash is None or author is None:
            raise ValueError("Неполные данные коммита")

        return cls(
            tree_hash=tree_hash,
            parent_hash=parent_hash,
            author=author,
            message=message,
        )


class CommitHistoryIterator(Iterator[Tuple[str, Commit]]):

    def __init__(self, start_sha: str | None):
        self.current_sha = start_sha

    def __iter__(self) -> "CommitHistoryIterator":
        """ Возвращает сам объект-итератор """
        return self

    def __next__(self) -> Tuple[str, Commit]:
        """ Возвращает предыдущий коммит (родительский коммит для текущего) """
        if self.current_sha is None:
            raise StopIteration
        sha = self.current_sha
        obj = read_object(sha)
        if not isinstance(obj, Commit):
            raise ValueError(f"Объект {sha} не является commit")

        commit: Commit = obj
        self.current_sha = commit.parent_hash
        return sha, commit


def hash_object(data: bytes, obj_type: str) -> str:
    """
    Хеширует данные и сохраняет Git-объект в .pygit/objects.
    Добавляет заголовок '<type> <size>\0', считает SHA-1,
    сжимает с помощью zlib и записывает объект в каталог
    .pygit/objects/sha-1[:2]/sha-1[2:], если он ещё не существует.
    """
    if obj_type not in ('blob', 'tree', 'commit'):
        raise ValueError(f'Неизвестный тип объекта {obj_type}')
    header = f'{obj_type} {len(data)}'.encode('utf-8') + b'\x00'
    for_hash = header + data
    sha1 = hashlib.sha1(for_hash).hexdigest()
    repository_root = os.getcwd()
    objects_dir = os.path.join(repository_root, PYGIT_DIRECTORY, 'objects')
    subdir = sha1[:2]
    file = sha1[2:]
    object_dir = os.path.join(objects_dir, subdir)
    object_path = os.path.join(object_dir, file)
    if not os.path.exists(object_dir):
        os.makedirs(object_dir)
    if not os.path.exists(object_path):
        compressed = zlib.compress(for_hash)

        with open(object_path, "wb") as f:
            f.write(compressed)

    return sha1


def read_object(sha: str) -> GitObject:
    """
     По SHA строит путь к файлу, разжимает содержимое, разбирает заголовок
    (тип и размер), а затем десериализует тело в Blob, Tree или Commit
    """
    repo = os.getcwd()
    object_path = os.path.join(repo, PYGIT_DIRECTORY,
                               'objects', sha[:2], sha[2:])

    with open(object_path, 'rb') as f:
        compressed = f.read()

    raw = zlib.decompress(compressed)
    header, body = raw.split(b'\x00', 1)
    header_text = header.decode('utf-8')
    object_type, _ = header_text.split(' ', 1)

    if object_type == 'blob':
        return Blob.deserialize(body)
    elif object_type == 'tree':
        return Tree.deserialize(body)
    elif object_type == 'commit':
        return Commit.deserialize(body)
    else:
        raise ValueError('Нужен объект blob, tree или commit')
