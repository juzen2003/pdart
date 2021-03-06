"""
Functionality to create a label for a data product containing a single
FITS file.
"""
from typing import Any, Dict, Generator, List, Optional, Tuple, cast
import os.path
from sqlalchemy.orm.exc import NoResultFound

from pdart.db.BundleDB import BundleDB
from pdart.db.SqlAlchTables import File, OtherCollection
from pdart.labels.FileContents import get_file_contents
from pdart.labels.Lookup import (
    CARD_SET,
    DictLookup,
    Lookup,
    MultiDictLookup,
    make_hdu_lookups,
)
from pdart.labels.FitsProductLabelXml import (
    make_label,
    mk_Investigation_Area_lidvid,
    mk_Investigation_Area_name,
)
from pdart.labels.HstParameters import (
    get_hst_parameters,
    get_start_stop_date_times,
)
from pdart.labels.LabelError import LabelError
from pdart.labels.ObservingSystem import (
    instrument_host_lid,
    observing_system,
    observing_system_lid,
)
from pdart.labels.Suffixes import RAW_SUFFIXES, SHM_SUFFIXES
from pdart.labels.TargetIdentification import get_target, get_target_info
from pdart.labels.TimeCoordinates import get_time_coordinates
from pdart.labels.Utils import lidvid_to_lid, lidvid_to_vid
from pdart.pds4.LID import LID
from pdart.pds4.LIDVID import LIDVID
from pdart.pds4.VID import VID
from pdart.xml.Pretty import pretty_and_verify


def _directory_siblings(
    working_dir: str, bundle_db: BundleDB, product_lidvid: str
) -> List[str]:
    # Look in the mastDownload directory and search for the file with
    # the product_lidvid's basename.  Then return all its siblings'
    # basenames.
    for dirpath, dirnames, filenames in os.walk(
        os.path.join(working_dir, "mastDownload")
    ):
        basename = bundle_db.get_product_file(product_lidvid).basename
        if basename in filenames:
            return sorted(filenames)
    return []


def _raw_sibling_file(siblings: List[str]) -> Tuple[str, str]:
    for suffix in RAW_SUFFIXES:
        sib_file = _sibling_file(siblings, suffix)
        if sib_file:
            return (suffix, sib_file)
    assert False, f"siblings={siblings}; RAW_SUFFIXES={RAW_SUFFIXES}"


def _shm_sibling_file(siblings: List[str]) -> Tuple[str, str]:
    for suffix in SHM_SUFFIXES:
        sib_file = _sibling_file(siblings, suffix)
        if sib_file:
            return (suffix, sib_file)
    assert False


def _sibling_file(siblings: List[str], suffix: str) -> Optional[str]:
    # Given a list of siblings, return the first one that ends with
    # "_<suffix>.fits".
    ending = f"_{suffix.lower()}.fits"
    for basename in siblings:
        if basename.lower().endswith(ending):
            return basename
    return None


def _munge_lidvid(product_lidvid: str, suffix: str, new_basename: str) -> str:
    bundle_id, collection_id, product_id = LIDVID(product_lidvid).lid().parts()

    # TODO This is a hack
    new_collection_id = collection_id[:-3] + suffix.lower()
    # TODO This is a hack
    new_product_id = new_basename[0:9]

    new_lid = LID.create_from_parts([bundle_id, new_collection_id, new_product_id])
    # TODO This is a hack.  Fix it.
    vid = VID("1.0")
    new_lidvid = LIDVID.create_from_lid_and_vid(new_lid, vid)
    return str(new_lidvid)


def _find_RAWish_lookups(
    bundle_db: BundleDB, product_lidvid: str, file_basename: str, siblings: List[str]
) -> List[Lookup]:
    # TODO Fix this
    def _find_RAWish_suffix_and_basename() -> Tuple[str, str]:
        return _raw_sibling_file(siblings)

    suffix, RAWish_basename = _find_RAWish_suffix_and_basename()
    RAWish_product_lidvid = _munge_lidvid(product_lidvid, suffix, RAWish_basename)

    def _find_RAWish_card_dicts() -> CARD_SET:
        card_dicts = bundle_db.get_card_dictionaries(
            RAWish_product_lidvid, RAWish_basename
        )
        return card_dicts

    try:
        card_dicts = _find_RAWish_card_dicts()
    except NoResultFound as e:
        # TODO Remove this instrumentation
        print(
            f"""**** _find_RAWish_lookups(
    product_lidvid={product_lidvid},
    file_basename={file_basename},
    siblings={siblings}
    )
raised exception = {e} ****
"""
        )
        raise
    return make_hdu_lookups(RAWish_basename, card_dicts)


def _find_SHMish_lookup(
    bundle_db: BundleDB, product_lidvid: str, file_basename: str, siblings: List[str]
) -> Lookup:
    # TODO Fix this
    def _find_SHMish_suffix_and_basename() -> Tuple[str, str]:
        return _shm_sibling_file(siblings)

    suffix, SHMish_basename = _find_SHMish_suffix_and_basename()
    SHMish_product_lidvid = _munge_lidvid(product_lidvid, suffix, SHMish_basename)

    def _find_SHMish_card_dicts() -> CARD_SET:
        card_dicts = bundle_db.get_card_dictionaries(
            SHMish_product_lidvid, SHMish_basename
        )
        return card_dicts

    card_dicts = _find_SHMish_card_dicts()
    return DictLookup(SHMish_basename, card_dicts)


def make_fits_product_label(
    working_dir: str,
    bundle_db: BundleDB,
    product_lidvid: str,
    file_basename: str,
    verify: bool,
) -> bytes:
    try:
        product = bundle_db.get_product(product_lidvid)
        collection_lidvid = product.collection_lidvid

        collection = bundle_db.get_collection(collection_lidvid)
        assert isinstance(collection, OtherCollection)
        instrument = collection.instrument
        suffix = collection.suffix
        bundle_lidvid = collection.bundle_lidvid

        card_dicts = bundle_db.get_card_dictionaries(product_lidvid, file_basename)
        lookup = DictLookup(file_basename, card_dicts)
        siblings = _directory_siblings(working_dir, bundle_db, product_lidvid)
        hdu_lookups = _find_RAWish_lookups(
            bundle_db, product_lidvid, file_basename, siblings
        )
        shm_lookup = _find_SHMish_lookup(
            bundle_db, product_lidvid, file_basename, siblings
        )

        # TODO This is a hack.  I need to have get_start_stop_date_times
        # to include an exposure time.
        start_date_time, stop_date_time = get_start_stop_date_times(
            hdu_lookups, shm_lookup
        )
        start_stop_times = {
            "start_date_time": start_date_time,
            "stop_date_time": stop_date_time,
            "exposure_duration": "0.1",  # TODO A totally bogus value
        }

        hst_parameters = get_hst_parameters(hdu_lookups, shm_lookup)
        bundle = bundle_db.get_bundle()
        assert bundle.lidvid == bundle_lidvid
        proposal_id = bundle.proposal_id

        investigation_area_lidvid = mk_Investigation_Area_lidvid(proposal_id)
        bundle_db.create_context_product(investigation_area_lidvid)
        bundle_db.create_context_product(instrument_host_lid())
        bundle_db.create_context_product(observing_system_lid(instrument))
        target_info = get_target_info(shm_lookup)
        bundle_db.create_context_product(target_info["lid"])

        label = (
            make_label(
                {
                    "lid": lidvid_to_lid(product_lidvid),
                    "vid": lidvid_to_vid(product_lidvid),
                    "proposal_id": str(proposal_id),
                    "suffix": suffix,
                    "file_name": file_basename,
                    "file_contents": get_file_contents(
                        bundle_db, card_dicts, instrument, product_lidvid
                    ),
                    "Investigation_Area_name": mk_Investigation_Area_name(proposal_id),
                    "investigation_lidvid": investigation_area_lidvid,
                    "Observing_System": observing_system(instrument),
                    "Time_Coordinates": get_time_coordinates(start_stop_times),
                    "Target_Identification": get_target(target_info),
                    "HST": hst_parameters,
                }
            )
            .toxml()
            .encode()
        )
    except Exception as e:
        raise LabelError(
            product_lidvid, file_basename, (lookup, hdu_lookups[0], shm_lookup)
        ) from e

    return pretty_and_verify(label, verify)
