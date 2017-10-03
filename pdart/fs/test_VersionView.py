import unittest

from fs.memoryfs import MemoryFS
from fs.path import join

from pdart.fs.MultiversionBundleFS import MultiversionBundleFS
from pdart.fs.SubdirVersions import write_subdir_versions_to_directory
# from pdart.fs.SubdirVersions import write_subdir_versions
from pdart.fs.VersionView import VersionView, VersionView2
from pdart.fs.VersionedFS import ROOT
from pdart.pds4.LIDVID import LIDVID

_BUNDLE_ID = u'hst_00000'
_COLLECTION_ID = u'data_xxx_raw'
_PRODUCT_ID = u'u2q9xx01j_raw'

_LIDVID_B0 = LIDVID('urn:nasa:pds:hst_00000::0')
_LIDVID_B1 = LIDVID('urn:nasa:pds:hst_00000::1')
_LIDVID_B2 = LIDVID('urn:nasa:pds:hst_00000::2')
_LIDVID_B3 = LIDVID('urn:nasa:pds:hst_00000::3')

_LIDVID_C0 = LIDVID('urn:nasa:pds:hst_00000:data_xxx_raw::0')
_LIDVID_C1 = LIDVID('urn:nasa:pds:hst_00000:data_xxx_raw::1')
_LIDVID_C2 = LIDVID('urn:nasa:pds:hst_00000:data_xxx_raw::2')

_LIDVID_P0 = LIDVID('urn:nasa:pds:hst_00000:data_xxx_raw:u2q9xx01j_raw::0')
_LIDVID_P1 = LIDVID('urn:nasa:pds:hst_00000:data_xxx_raw:u2q9xx01j_raw::1')


class TestVersionView2(unittest.TestCase):
    def setUp(self):
        memory_fs = MemoryFS()
        self.versioned_fs = MultiversionBundleFS(memory_fs)
        self.versioned_fs.make_lidvid_directories(_LIDVID_B0)
        self.versioned_fs.make_lidvid_directories(_LIDVID_B1)
        self.versioned_fs.make_lidvid_directories(_LIDVID_B2)
        self.versioned_fs.make_lidvid_directories(_LIDVID_B3)

        self.versioned_fs.make_lidvid_directories(_LIDVID_C0)
        self.versioned_fs.make_lidvid_directories(_LIDVID_C1)
        self.versioned_fs.add_subcomponent(_LIDVID_B3, _LIDVID_C2)

        self.versioned_fs.make_lidvid_directories(_LIDVID_P0)
        self.versioned_fs.add_subcomponent(_LIDVID_C2, _LIDVID_P1)

        self.version_view = VersionView2(_LIDVID_B3,
                                         self.versioned_fs)

    @unittest.skip('fails on purpose; for use while testing')
    def test_init(self):
        self.versioned_fs.tree()
        self.assertFalse(True)

    def test_creation(self):
        # type: () -> None
        self.assertEqual(self.version_view._bundle_id, _BUNDLE_ID)
        self.assertEqual(self.version_view._version_id, u'3')
        with self.assertRaises(Exception):
            VersionView2(LIDVID('urn:nasa:pds:hst_00000::666'),
                         self.versioned_fs)


class TestVersionView(unittest.TestCase):
    def setUp(self):
        self.versioned_fs = MemoryFS()
        self.versioned_fs.makedirs(join(ROOT, _BUNDLE_ID, u'v$0'))
        write_subdir_versions_to_directory(self.versioned_fs,
                                           join(ROOT, _BUNDLE_ID, u'v$0'), {})

        self.versioned_fs.makedirs(join(ROOT, _BUNDLE_ID, u'v$1'))
        write_subdir_versions_to_directory(self.versioned_fs,
                                           join(ROOT, _BUNDLE_ID, u'v$1'), {})

        self.versioned_fs.makedirs(join(ROOT, _BUNDLE_ID, u'v$2'))

        self.versioned_fs.makedirs(join(ROOT, _BUNDLE_ID, u'v$3'))
        write_subdir_versions_to_directory(self.versioned_fs,
                                           join(ROOT, _BUNDLE_ID, u'v$3'),
                                           {_COLLECTION_ID: u'2'})

        self.versioned_fs.makedirs(
            join(ROOT, _BUNDLE_ID, _COLLECTION_ID, u'v$0'))
        write_subdir_versions_to_directory(
            self.versioned_fs,
            join(ROOT, _BUNDLE_ID, _COLLECTION_ID, u'v$0'),
            {})

        self.versioned_fs.makedirs(
            join(ROOT, _BUNDLE_ID, _COLLECTION_ID, u'v$1'))
        write_subdir_versions_to_directory(
            self.versioned_fs,
            join(ROOT, _BUNDLE_ID, _COLLECTION_ID, u'v$1'),
            {})

        self.versioned_fs.makedirs(
            join(ROOT, _BUNDLE_ID, _COLLECTION_ID, u'v$2'))
        write_subdir_versions_to_directory(
            self.versioned_fs,
            join(ROOT, _BUNDLE_ID, _COLLECTION_ID, u'v$2'),
            {_PRODUCT_ID: u'1'})

        self.versioned_fs.makedirs(
            join(ROOT, _BUNDLE_ID, _COLLECTION_ID, _PRODUCT_ID, u'v$0'))

        self.versioned_fs.makedirs(
            join(ROOT, _BUNDLE_ID, _COLLECTION_ID, _PRODUCT_ID, u'v$1'))

        self.version_view = VersionView(u'urn:nasa:pds:hst_00000::3',
                                        self.versioned_fs)

    def test_creation(self):
        # type: () -> None
        self.assertEqual(self.version_view._bundle_id, _BUNDLE_ID)
        self.assertEqual(self.version_view._version_id, u'3')
        with self.assertRaises(Exception):
            VersionView(u'urn:nasa:pds:hst_00000::666', self.versioned_fs)

    def test_root(self):
        # type: () -> None
        self.assertTrue(self.version_view.exists(ROOT))
        self.assertTrue(self.version_view.isdir(ROOT))
        self.assertEqual([_BUNDLE_ID], self.version_view.listdir(ROOT))

    def test_bundle_dir(self):
        # type: () -> None
        BUNDLE_DIR = join(ROOT, _BUNDLE_ID)
        self.assertTrue(self.version_view.exists(BUNDLE_DIR))
        self.assertTrue(self.version_view.isdir(BUNDLE_DIR))
        self.assertEqual([_COLLECTION_ID],
                         self.version_view.listdir(BUNDLE_DIR))

        # test that collections appear
        self.assertTrue(self.version_view.exists(
            join(ROOT, _BUNDLE_ID, _COLLECTION_ID)))

        # test that files don't appear when wrong version
        self.versioned_fs.touch(join(ROOT, _BUNDLE_ID, u'v$1', u'bundle.xml'))
        self.assertFalse(self.version_view.exists(
            join(ROOT, _BUNDLE_ID, u'bundle.xml')))

        # test that files do appear when right version
        self.versioned_fs.touch(join(ROOT, _BUNDLE_ID, u'v$3', u'bundle.xml'))
        self.assertTrue(self.version_view.exists(
            join(ROOT, _BUNDLE_ID, u'bundle.xml')))

    def test_collection_dir(self):
        # type: () -> None
        COLLECTION_DIR = join(ROOT, _BUNDLE_ID, _COLLECTION_ID)
        self.assertTrue(self.version_view.exists(COLLECTION_DIR))
        self.assertTrue(self.version_view.isdir(COLLECTION_DIR))
        self.assertEqual([_PRODUCT_ID],
                         self.version_view.listdir(COLLECTION_DIR))

        # test that files don't appear when wrong version
        self.versioned_fs.touch(join(COLLECTION_DIR, u'v$1',
                                     u'collection.xml'))
        self.assertFalse(self.version_view.exists(join(COLLECTION_DIR,
                                                       u'collection.xml')))
        # test that files do appear when right version
        self.versioned_fs.touch(join(COLLECTION_DIR, u'v$2',
                                     u'collection.xml'))
        print '****', self.version_view.listdir(COLLECTION_DIR)
        print '****', self.version_view.getinfo(join(COLLECTION_DIR,
                                                     u'collection.xml'))
        self.assertTrue(self.version_view.exists(
            join(COLLECTION_DIR, u'collection.xml')))

    def test_product_dir(self):
        # type: () -> None
        PRODUCT_DIR = join(ROOT, _BUNDLE_ID, _COLLECTION_ID, _PRODUCT_ID)
        self.assertTrue(self.version_view.exists(PRODUCT_DIR))
        self.assertTrue(self.version_view.isdir(PRODUCT_DIR))
        self.assertEqual([], self.version_view.listdir(PRODUCT_DIR))

        # test that files don't appear when wrong version
        self.versioned_fs.touch(join(PRODUCT_DIR, u'v$0',
                                     u'product.xml'))
        self.assertFalse(self.version_view.exists(join(PRODUCT_DIR,
                                                       u'product.xml')))

        # test that files do appear when right version
        self.versioned_fs.touch(join(PRODUCT_DIR, u'v$1',
                                     u'product.xml'))
        self.assertTrue(self.version_view.exists(
            join(PRODUCT_DIR, u'product.xml')))

    def test_legacy_bundle_dir(self):
        BUNDLE_DIR = join(ROOT, _BUNDLE_ID, u'v$3')
        self.assertEqual(BUNDLE_DIR, self.version_view._legacy_bundle_dir())

    def test_legacy_collection_dir(self):
        COLLECTION_DIR = join(ROOT, _BUNDLE_ID, _COLLECTION_ID, u'v$2')
        legacy_dir = self.version_view._legacy_collection_dir(_COLLECTION_ID)
        self.assertEqual(COLLECTION_DIR, legacy_dir)

    def test_legacy_product_dir(self):
        PRODUCT_DIR = join(ROOT,
                           _BUNDLE_ID, _COLLECTION_ID,
                           _PRODUCT_ID, u'v$1')
        self.assertEqual(PRODUCT_DIR,
                         self.version_view._legacy_product_dir(_COLLECTION_ID,
                                                               _PRODUCT_ID))


@unittest.skip('takes a long time')
def test_version_view_on_archive():
    """
    Run through all the bundles in the archive, view them as versioned
    filesystems, and try to verify them , then copy them to another
    (in-memory) filesystem.  See whether anything breaks.
    """
    import fs.copy
    from fs.memoryfs import MemoryFS
    from fs.osfs import OSFS
    from pdart.fs.InitialVersionedView import InitialVersionedView
    from pdart.pds4.Archives import get_any_archive

    archive = get_any_archive()
    for bundle in archive.bundles():
        print bundle
        with OSFS(bundle.absolute_filepath()) as osfs:
            ivv = InitialVersionedView(bundle.lid.bundle_id, osfs)
            vv = VersionView(str(bundle.lid) + '::1', ivv)
            with MemoryFS() as memoryfs:
                fs.copy.copy_fs(vv, memoryfs)
