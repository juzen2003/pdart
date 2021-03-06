from typing import Any, Iterable, Iterator, Optional, Sized
from astropy.io.fits.column import ColDefs

class BinTableHDU(Sized):
    columns: ColDefs
    data: Any
    def __len__(self) -> int: ...

class HDUList(Iterable[Any], Sized):
    def close(
        self,
        output_verify: str = "exception",
        verbose: bool = False,
        closed: bool = True,
    ) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Any]: ...

def fitsopen(
    name: str,
    mode: str = "readonly",
    memmap: Optional[bool] = None,
    save_backup: Optional[bool] = False,
    cache: Optional[bool] = True,
    lazy_load_hdus: Optional[bool] = None,
    **kwargs: Any
) -> HDUList: ...
