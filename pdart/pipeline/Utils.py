import os.path
from contextlib import contextmanager
from typing import Generator

from fs.osfs import OSFS

from pdart.fs.cowfs.COWFS import COWFS
from pdart.fs.multiversioned.Multiversioned import Multiversioned
from pdart.fs.multiversioned.VersionView import VersionView
from pdart.fs.versioned.Versioned import (
    MultiversionedCOWFS,
    MultiversionedOSFS,
    SingleVersionedCOWFS,
    SingleVersionedOSFS,
)
from pdart.pds4.LID import LID
from pdart.pipeline.FSTypes import *


def show_tree(tag: str, fs: FS) -> None:
    line = f"---- {tag} "
    tag_len = len(tag)
    line += (60 - tag_len) * "-"
    print(line)
    fs.tree()


@contextmanager
def make_osfs(dir: str) -> Generator[OSFS, None, None]:
    if not os.path.isdir(dir):
        os.makedirs(dir)
    fs = OSFS(dir)
    yield fs
    fs.close()


@contextmanager
def make_mv_osfs(dir: str) -> Generator[OSFS, None, None]:
    fs = MultiversionedOSFS.create_suffixed(dir)
    yield fs
    fs.close()


@contextmanager
def make_sv_osfs(dir: str) -> Generator[OSFS, None, None]:
    fs = SingleVersionedOSFS.create_suffixed(dir)
    yield fs
    fs.close()


@contextmanager
def make_sv_deltas(base_fs: FS, cow_dirpath: str) -> Generator[COWFS, None, None]:
    fs = SingleVersionedCOWFS.create_cowfs_suffixed(base_fs, cow_dirpath, True)
    cat_base_fs = categorize_filesystem(base_fs)
    cat_fs = categorize_filesystem(fs)
    if (
        cat_base_fs != EMPTY_FS_TYPE
        and cat_fs != EMPTY_FS_TYPE
        and cat_fs != cat_base_fs
    ):
        print(f"{cat_base_fs}, {cat_fs}")
        show_tree("base_fs", base_fs)
        show_tree("fs", fs)
        assert False
    yield fs
    fs.close()


@contextmanager
def make_mv_deltas(base_fs: FS, cow_dirpath: str) -> Generator[COWFS, None, None]:
    fs = MultiversionedCOWFS.create_cowfs_suffixed(base_fs, cow_dirpath, True)
    cat_base_fs = categorize_filesystem(base_fs)
    cat_fs = categorize_filesystem(fs)
    if (
        cat_base_fs != EMPTY_FS_TYPE
        and cat_fs != EMPTY_FS_TYPE
        and cat_fs != cat_base_fs
    ):
        print(f"{cat_base_fs}, {cat_fs}")
        show_tree("base_fs", base_fs)
        show_tree("fs", fs)
        assert False
    yield fs
    fs.close()


@contextmanager
def make_version_view(
    archive_osfs: OSFS, bundle_segment: str
) -> Generator[VersionView, None, None]:
    assert categorize_filesystem(archive_osfs) in [
        EMPTY_FS_TYPE,
        MULTIVERSIONED_FS_TYPE,
    ], categorize_filesystem(archive_osfs)
    mv = Multiversioned(archive_osfs)
    lid = LID("urn:nasa:pds:" + str(bundle_segment))
    res = mv.create_version_view(lid)
    assert categorize_filesystem(res) in [
        EMPTY_FS_TYPE,
        SINGLE_VERSIONED_FS_TYPE,
    ], categorize_filesystem(res)

    yield res
    res.close()
