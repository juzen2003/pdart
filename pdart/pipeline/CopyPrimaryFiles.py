from typing import TYPE_CHECKING
from contextlib import contextmanager
import os.path
import shutil

from multiversioned.Multiversioned import Multiversioned
from pdart.pipeline.Utils import *

from cowfs.COWFS import COWFS
from fs.osfs import OSFS
from fs.tempfs import TempFS
import fs.path

from pdart.pds4.HstFilename import HstFilename
from pdart.pds4.LID import LID

if TYPE_CHECKING:
    from typing import Generator
    from fs.base import FS
    from multiversioned.VersionView import VersionView

def to_segment_dir(name):
    return name + u'$'

def _copy_docs_files(bundle_segment,
                     documents_dir,
                     primary_files_dir):
    # type: (unicode, unicode, unicode) -> None
    assert os.path.isdir(documents_dir)

    with make_osfs(documents_dir) as documents_fs, \
        make_sv_osfs(primary_files_dir) as primary_files_fs:
        new_dir_path = os.path.join(to_segment_dir(bundle_segment),
                                    to_segment_dir('document'))
        primary_files_fs.makedirs(new_dir_path)
        for file in documents_fs.walk.files():
            file_basename = os.path.basename(file)
            new_file_path = os.path.join(new_dir_path, file_basename)
            fs.copy.copy_file(documents_fs, file,
                              primary_files_fs, new_file_path)

    shutil.rmtree(documents_dir)
    assert not os.path.isdir(documents_dir)

def _copy_fits_files(bundle_segment,
                     mast_downloads_dir,
                     primary_files_dir):
    # type: (unicode, unicode, unicode) -> None
    assert os.path.isdir(mast_downloads_dir)

    with make_osfs(mast_downloads_dir) as mast_downloads_fs, \
        make_sv_osfs(primary_files_dir) as primary_files_fs:

        # Walk the mast_downloads_dir for FITS file and file
        # them into the COW filesystem.
        for filepath in mast_downloads_fs.walk.files(filter=['*.fits']):
            parts = fs.path.iteratepath(filepath)
            depth = len(parts)
            assert depth == 3, parts
            _, product, filename = parts
            filename = filename.lower()
            hst_filename = HstFilename(filename)
            coll = 'data_%s_%s' % (hst_filename.instrument_name(),
                                   hst_filename.suffix())
            new_path = fs.path.join(to_segment_dir(bundle_segment),
                                    to_segment_dir(coll),
                                    to_segment_dir(product), filename)
            dirs, filename = fs.path.split(new_path)
            primary_files_fs.makedirs(dirs)
            fs.copy.copy_file(mast_downloads_fs, filepath,
                              primary_files_fs, new_path)

    assert os.path.isdir(primary_files_dir + '-sv'), \
        (primary_files_dir + '-sv')
    # If I made it to here, it should be safe to delete the downloads
    shutil.rmtree(mast_downloads_dir)
    assert not os.path.isdir(mast_downloads_dir)


def copy_primary_files(bundle_segment,
                       documents_dir,
                       mast_downloads_dir,
                       primary_files_dir):
    # type: (unicode, unicode, unicode, unicode) -> None
    assert bundle_segment.startswith('hst_')
    assert bundle_segment[-5:].isdigit()

    print '****_copy_docs_files'
    _copy_docs_files(bundle_segment, documents_dir, primary_files_dir)
    print '****_copy_fits_files'
    _copy_fits_files(bundle_segment, mast_downloads_dir, primary_files_dir)

