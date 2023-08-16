"""Compatibility with :mod:`xarray`."""
from typing import (
    Any,
    Dict,
    Generic,
    Hashable,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

import numpy as np
import pandas as pd
import xarray
from xarray.core.types import InterpOptions

from genno.core.types import Dims

T = TypeVar("T", covariant=True)


class DataArrayLike(Generic[T]):
    """Class with :class:`.xarray.DataArray` -like API.

    This class is used to set signatures and types for methods and attributes on the
    generic :class:`.Quantity` class. :class:`.SparseDataArray` inherits from both this
    class and :class:`~xarray.DataArray`, and thus DataArray supplies implementations of
    these methods. In :class:`.AttrSeries`, the methods are implemented directly.
    """

    # To silence a warning in xarray
    __slots__: Tuple[str, ...] = tuple()

    # Type hints for mypy in downstream applications
    def __len__(self) -> int:
        return NotImplemented

    # @abstractmethod  # NB this suppresses a mypy "empty-body" error
    def __mul__(self, other):  # TODO set the return type
        ...

    def __pow__(self, other):  # TODO set the return type
        ...

    def __radd__(self, other):
        ...

    def __rmul__(self, other):
        ...

    def __rsub__(self, other):
        ...

    def __rtruediv__(self, other):
        ...

    # @abstractmethod  # NB this suppresses a mypy "empty-body" error
    def __truediv__(self, other):  # TODO set the return type
        ...

    @property
    def attrs(self) -> Dict[Any, Any]:
        return NotImplemented

    @property
    # @abstractmethod
    def coords(
        self,
    ) -> xarray.core.coordinates.DataArrayCoordinates:
        return NotImplemented

    @property
    # @abstractmethod
    def dims(self) -> Tuple[Hashable, ...]:
        return NotImplemented

    def assign_coords(
        self,
        coords: Optional[Mapping[Any, Any]] = None,
        **coords_kwargs: Any,
    ):
        ...  # pragma: no cover

    def bfill(
        self,
        dim: Hashable,
        limit: Optional[int] = None,
    ):  # TODO set the return type
        ...

    def copy(
        self,
        deep: bool = True,
        data: Any = None,
    ):  # TODO set the return type
        ...

    def cumprod(
        self,
        dim: Dims = None,
        *,
        skipna: Optional[bool] = None,
        keep_attrs: Optional[bool] = None,
        **kwargs: Any,
    ):  # TODO set the return type
        ...

    def drop_vars(
        self,
        names: Union[Hashable, Iterable[Hashable]],
        *,
        errors="raise",
    ):
        ...

    def expand_dims(
        self,
        dim=None,
        axis=None,
        **dim_kwargs: Any,
    ):  # TODO set the return type
        ...

    def ffill(
        self,
        dim: Hashable,
        limit: Optional[int] = None,
    ):  # TODO set the return type
        return NotImplemented

    def groupby(
        self,
        group,
        squeeze: bool = True,
        restore_coord_dims: bool = False,
    ):
        ...

    def interp(
        self,
        coords: Optional[Mapping[Any, Any]] = None,
        method: InterpOptions = "linear",
        assume_sorted: bool = False,
        kwargs: Optional[Mapping[str, Any]] = None,
        **coords_kwargs: Any,
    ):
        ...

    def item(self, *args):
        ...  # pragma: no cover

    def rename(
        self,
        new_name_or_name_dict: Union[Hashable, Mapping[Any, Hashable]] = None,
        **names: Hashable,
    ):
        ...

    def round(self, *args, **kwargs):
        ...

    def sel(
        self,
        indexers: Optional[Mapping[Any, Any]] = None,
        method: Optional[str] = None,
        tolerance=None,
        drop: bool = False,
        **indexers_kwargs: Any,
    ) -> T:
        return NotImplemented

    def shift(
        self,
        shifts: Optional[Mapping[Any, int]] = None,
        fill_value: Any = None,
        **shifts_kwargs: int,
    ):
        ...

    def sum(
        self,
        dim: Dims = None,
        # Signature from xarray.DataArray
        *,
        skipna: Optional[bool] = None,
        min_count: Optional[int] = None,
        keep_attrs: Optional[bool] = None,
        **kwargs: Any,
    ):
        ...

    def to_dataframe(
        self,
        name: Optional[Hashable] = None,
        dim_order: Optional[Sequence[Hashable]] = None,
    ) -> pd.DataFrame:
        ...

    def to_numpy(self) -> np.ndarray:
        return NotImplemented

    def to_series(self) -> pd.Series:
        """Like :meth:`xarray.DataArray.to_series`."""
        # Provided only for type-checking in other packages. AttrSeries implements;
        # SparseDataArray uses the xr.DataArray method.
        return NotImplemented
