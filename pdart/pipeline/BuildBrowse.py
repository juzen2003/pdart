import os
import traceback
from typing import List, Set

import fs.path
import picmaker

from pdart.astroquery.Astroquery import ACCEPTED_SUFFIXES
from pdart.db.BundleDB import (
    BundleDB,
    _BUNDLE_DB_NAME,
    create_bundle_db_from_os_filepath,
)
from pdart.fs.cowfs.COWFS import COWFS
from pdart.pds4.LID import LID
from pdart.pds4.LIDVID import LIDVID
from pdart.pds4.VID import VID
from pdart.pipeline.Stage import MarkedStage
from pdart.pipeline.Utils import make_osfs, make_sv_deltas, make_version_view

_INITIAL_VID: VID = VID("1.0")

_NON_IMAGE_SUFFIXES: Set[str] = {"ASN", "SHM"}


_BROWSE_SUFFIXES: List[str] = [
    suffix for suffix in ACCEPTED_SUFFIXES if suffix not in _NON_IMAGE_SUFFIXES
]


def _create_initial_lidvid_from_parts(parts: List[str]) -> str:
    lid = LID.create_from_parts(parts)
    lidvid = LIDVID.create_from_lid_and_vid(lid, _INITIAL_VID)
    return str(lidvid)


def _extend_initial_lidvid(lidvid: str, segment: str) -> str:
    lid = LIDVID(lidvid).lid().extend_lid(segment)
    new_lidvid = LIDVID.create_from_lid_and_vid(lid, _INITIAL_VID)
    return str(new_lidvid)


def _build_browse_collection(
    db: BundleDB,
    browse_deltas: COWFS,
    bundle_segment: str,
    collection_segment: str,
    bundle_path: str,
) -> None:
    bundle_lidvid = _create_initial_lidvid_from_parts([bundle_segment])
    data_collection_lidvid = _create_initial_lidvid_from_parts(
        [bundle_segment, collection_segment]
    )
    browse_collection_lid = LIDVID(data_collection_lidvid).lid().to_browse_lid()
    collection_path = f"{bundle_path}{collection_segment}$/"
    browse_collection_segment = browse_collection_lid.collection_id
    browse_collection_path = "{bundle_path}{browse_collection_segment}$/"

    browse_deltas.makedirs(browse_collection_path, recreate=True)
    browse_collection_lidvid = LIDVID.create_from_lid_and_vid(
        browse_collection_lid, _INITIAL_VID
    )
    db.create_other_collection(str(browse_collection_lidvid), bundle_lidvid)
    product_segments = [
        str(prod[:-1]) for prod in browse_deltas.listdir(collection_path) if "$" in prod
    ]
    for product_segment in product_segments:
        product_path = f"{collection_path}{product_segment}$/"
        browse_product_path = f"{browse_collection_path}{product_segment}$/"
        browse_product_lidvid = _extend_initial_lidvid(
            str(browse_collection_lidvid), product_segment
        )
        fits_product_lidvid = _extend_initial_lidvid(
            data_collection_lidvid, product_segment
        )

        browse_deltas.makedirs(browse_product_path, recreate=True)
        db.create_browse_product(
            browse_product_lidvid, fits_product_lidvid, str(browse_collection_lidvid)
        )
        for fits_file in browse_deltas.listdir(product_path):
            fits_filepath = fs.path.join(product_path, fits_file)
            fits_os_filepath = browse_deltas.getsyspath(fits_filepath)

            browse_file = fs.path.splitext(fits_file)[0] + ".jpg"
            browse_filepath = fs.path.join(browse_product_path, browse_file)

            # In a COWFS, a directory does not have a
            # syspath, only files.  So we write a stub
            # file into the directory, find its syspath
            # and its directory's syspath.  Then we remove
            # the stub file.
            browse_deltas.touch(browse_filepath)
            browse_product_os_filepath = browse_deltas.getsyspath(browse_filepath)
            browse_deltas.remove(browse_filepath)

            browse_product_os_dirpath = fs.path.dirname(browse_product_os_filepath)

            # Picmaker expects a list of strings.  If you give it
            # str, it'll index into it and complain about '/'
            # not being a file.  So don't do that!
            try:
                picmaker.ImagesToPics(
                    [str(fits_os_filepath)],
                    browse_product_os_dirpath,
                    filter="None",
                    percentiles=(1, 99),
                )
            except IndexError as e:
                tb = traceback.format_exc()
                message = f"File {fits_file}: {e}\n{tb}"
                raise Exception(message)

            browse_os_filepath = fs.path.join(browse_product_os_dirpath, browse_file)
            size = os.stat(browse_os_filepath).st_size
            db.create_browse_file(
                browse_os_filepath, browse_file, browse_product_lidvid, size
            )


class BuildBrowse(MarkedStage):
    def _run(self) -> None:
        working_dir: str = self.working_dir()
        archive_dir: str = self.archive_dir()
        archive_primary_deltas_dir: str = self.archive_primary_deltas_dir()
        archive_browse_deltas_dir: str = self.archive_browse_deltas_dir()

        db_filepath = os.path.join(working_dir, _BUNDLE_DB_NAME)
        db = create_bundle_db_from_os_filepath(db_filepath)

        with make_osfs(archive_dir) as archive_osfs, make_version_view(
            archive_osfs, self._bundle_segment
        ) as version_view, make_sv_deltas(
            version_view, archive_primary_deltas_dir
        ) as sv_deltas, make_sv_deltas(
            sv_deltas, archive_browse_deltas_dir
        ) as browse_deltas:
            bundle_path = f"/{self._bundle_segment}$/"
            collection_segments = [
                str(coll[:-1])
                for coll in browse_deltas.listdir(bundle_path)
                if "$" in coll
            ]
            for collection_segment in collection_segments:
                parts = collection_segment.upper().split("_")
                if (
                    len(parts) == 3
                    and parts[0] == "data"
                    and parts[2] in _BROWSE_SUFFIXES
                ):
                    _build_browse_collection(
                        db,
                        browse_deltas,
                        self._bundle_segment,
                        collection_segment,
                        bundle_path,
                    )
