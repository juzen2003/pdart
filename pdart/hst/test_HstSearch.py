from pdart.hst.HstSearch import *


def test_make_url():
    """Just a smoketest to force parsing of HstSearch."""
    assert make_url() is not None
