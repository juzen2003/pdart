import time

import julian
from requests.exceptions import ConnectionError

from astropy.table import Table
from astropy.table.row import Row
from typing import Any, Callable, Dict, List, Optional, Tuple

Julian = float


def filter_table(row_predicate, table):
    # type: (Callable[[Row], bool], Table) -> Table
    to_delete = [n for (n, row) in enumerate(table) if not row_predicate(row)]
    copy = table.copy()
    copy.remove_rows(to_delete)
    return copy


def ymd_to_mjd(y, m, d):
    # type: (int, int, int) -> Julian
    days = julian.day_from_ymd(y, m, d)
    return julian.mjd_from_day(days)


def ymd_tuple_to_mjd(ymd):
    # type: (Tuple[int, int, int]) -> Julian
    y, m, d = ymd
    return ymd_to_mjd(y, m, d)


def ymdhms_format_from_mjd(mjd):
    # type: (float) -> str
    (d, s) = julian.day_sec_from_mjd(mjd)
    return julian.ymdhms_format_from_day_sec(d, s)


def get_table_with_retries(mast_call, max_retries):
    # type: (Callable[[], Table], int) -> Table
    retry = 0
    table = None
    while table is None and retry <= max_retries:
        try:
            table = mast_call()
        except ConnectionError as e:
            retry = retry + 1
            print(f"retry #{retry}: {e}")
            time.sleep(1)
    assert table is not None
    return table


############################################################


def now_mjd():
    # type: () -> float
    return julian.mjd_from_time(time.time())


def mjd_range_to_now(last_check_mjd):
    # type: (float) -> List[float]
    return [last_check_mjd, now_mjd()]


def table_to_list_of_dicts(table):
    # type: (Table) -> List[Dict[str, Any]]
    """
    A utility function: the tables returned by astroquery are too
    large to be human-readable.
    """
    table_len = len(table)

    def mk_dict(i):
        # type: (int) -> Dict[str, Any]
        return {key: table[key][i] for key in table.colnames}

    return [mk_dict(i) for i in range(table_len)]
