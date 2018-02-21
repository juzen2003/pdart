"""
Functionality to read and write subdir-version dictionaries.  A
subdir-version dictionary has keys corresponding to subdirectory
names, and values corresponding to VIDs.
"""
import re

from fs.path import join
from typing import TYPE_CHECKING

from pdart.fs.VersionedFS import SUBDIR_VERSIONS_FILENAME

if TYPE_CHECKING:
    from fs.base import FS
    from typing import Dict

_versionRE = re.compile('^[0-9\.]+$')  # int


def parse_subdir_versions(txt):
    # type: (unicode) -> Dict[str, str]
    """
    Given the (Unicode) contents of a subdir-version file, parse it
    and return a subdir-version dictionary.
    """
    d = {}
    for n, line in enumerate(txt.split('\n')):
        line = line.strip()
        if line:
            fields = line.split(' ')
            assert len(fields) is 2, "line #%d = %r" % (n, line)
            # TODO assert format of each field
            assert _versionRE.match(str(fields[1]))
            d[str(fields[0])] = str(fields[1])
    return d


def str_subdir_versions(d):
    # type: (Dict[str, str]) -> unicode
    """
    Given a subdir-version dictionary, un-parse it into a (Unicode)
    string to be stored in a subdir-version file.
    """
    for v in d.itervalues():
        assert _versionRE.match(str(v))
    return u''.join(['%s %s\n' % (k, v) for k, v in sorted(d.items())])


def read_subdir_versions_from_directory(fs, dir):
    # type: (FS, unicode) -> Dict[str, str]
    """
    Given the path to a directory, return the subdir-version
    dictionary that lives in it.
    """
    SUBDIR_VERSIONS_FILEPATH = join(dir, SUBDIR_VERSIONS_FILENAME)
    return parse_subdir_versions(fs.gettext(SUBDIR_VERSIONS_FILEPATH,
                                            encoding='ascii'))


def read_subdir_versions_from_path(fs, path):
    # type: (FS, unicode) -> Dict[str, str]
    """
    Given the path to a subdir-version file, parse and return its
    contents into a subdir-version dictionary.
    """
    return parse_subdir_versions(fs.gettext(path,
                                            encoding='ascii'))


def write_subdir_versions_to_directory(fs, dir, d):
    # type: (FS, unicode, Dict[str, str]) -> None
    """
    Given the path to a directory, un-parse and write the contents of
    the given subdir-versions dictionary into a subdir-versions file
    in the directory.
    """
    SUBDIR_VERSIONS_FILEPATH = join(dir, SUBDIR_VERSIONS_FILENAME)
    fs.settext(SUBDIR_VERSIONS_FILEPATH,
               str_subdir_versions(d),
               encoding='ascii')


def write_subdir_versions_to_path(fs, path, d):
    # type: (FS, unicode, Dict[str, str]) -> None
    """
    Given the path to a subdir-versions file, un-parse and write the
    contents of the given subdir-versions dictionary into it.
    """
    fs.settext(path,
               str_subdir_versions(d),
               encoding='ascii')
