import os
import os.path

from astropy.table.row import Row

from pdart.astroquery.Astroquery import MastSlice, ProductSet, filter_table
from pdart.pipeline.Stage import MarkedStage


class CheckDownloads(MarkedStage):
    def _do_downloads(
        self, working_dir: str, mast_downloads_dir: str, proposal_id: int
    ) -> None:
        # first pass, <working_dir> shouldn't exist; second pass
        # <working_dir>/mastDownload should not exist.
        assert not os.path.isdir(mast_downloads_dir)

        # TODO These dates are wrong.  Do I need to do some optimization
        # here?
        slice = MastSlice((1900, 1, 1), (2025, 1, 1), proposal_id)
        proposal_ids = slice.get_proposal_ids()
        assert proposal_id in proposal_ids, f"{proposal_id} in {proposal_ids}"
        product_set = slice.to_product_set(proposal_id)
        if not os.path.isdir(working_dir):
            os.makedirs(working_dir)

        # TODO I should also download the documents here.
        product_set.download(working_dir)

        # TODO This might fail if there are no files.  Which might not be
        # a bad thing.
        assert os.path.isdir(mast_downloads_dir)

    def _run(self) -> None:
        working_dir: str = self.working_dir()
        mast_downloads_dir: str = self.mast_downloads_dir()

        if not os.path.isdir(mast_downloads_dir):
            self._do_downloads(working_dir, mast_downloads_dir, self._proposal_id)
