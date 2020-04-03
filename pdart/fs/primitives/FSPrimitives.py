import abc

import fs.errors
from typing import cast, Dict

import io


class Node(object, metaclass=abc.ABCMeta):
    def __init__(self, prims: "FSPrimitives", path: str) -> None:
        self.prims = prims
        self.path = path

    @abc.abstractmethod
    def is_file(self) -> bool:
        pass

    def is_dir(self) -> bool:
        return not self.is_file()

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, Node):
            raise NotImplemented
        return self.path == rhs.path

    def __ne__(self, other):
        return not self == other


class Dir(Node):
    def __init__(self, prims: "FSPrimitives", path: str) -> None:
        Node.__init__(self, prims, path)

    def is_file(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "Dir(%r, %r)" % (self.prims, self.path)


class File(Node):
    def __init__(self, prims: "FSPrimitives", path: str) -> None:
        Node.__init__(self, prims, path)

    def is_file(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "File(%r, %r)" % (self.prims, self.path)


class FSPrimitives(object, metaclass=abc.ABCMeta):
    """
    We model a filesystem with a very simple model that we can reason
    about.  The filesystem is like a tree with two kinds of nodes:
    files and dirs.  The file contains some way to change its
    contents, a handle, and dirs contain a map from strings to other
    nodes.  That's it.

    The root of the filesystem is constrained to be a dir.

    There are only a handful of primitive operations that we need to
    check.

    The laws a filesystem must uphold are few.  See the tests.
    """

    @abc.abstractmethod
    def root_node(self) -> Dir:
        pass

    def is_dir(self, node: Node) -> bool:
        return not self.is_file(node)

    @abc.abstractmethod
    def is_file(self, node: Node) -> bool:
        pass

    def get_children(self, node: Node) -> Dict[str, Node]:
        if self.is_file(node):
            raise fs.errors.DirectoryExpected(node.path)
        return self.get_dir_children(cast(Dir, node))

    @abc.abstractmethod
    def get_dir_children(self, node: Dir) -> Dict[str, Node]:
        pass

    def get_dir_child(self, parent_node: Dir, filename: str) -> Node:
        children = self.get_children(parent_node)
        return children[filename]

    def get_handle(self, node: Node, mode: str) -> io.IOBase:
        if self.is_dir(node):
            raise fs.errors.FileExpected(node.path)
        return self.get_file_handle(cast(File, node), mode)

    @abc.abstractmethod
    def get_file_handle(self, node: File, mode: str) -> io.IOBase:
        pass

    @abc.abstractmethod
    def add_child_dir(self, parent_node: Dir, filename: str) -> Dir:
        pass

    @abc.abstractmethod
    def add_child_file(self, parent_node: Dir, filename: str) -> File:
        pass

    @abc.abstractmethod
    def remove_child(self, parent_node: Dir, filename: str) -> None:
        pass
