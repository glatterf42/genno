"""Types for hinting.

This module and its contents should usually be imported within an :py:`if TYPE_CHECKING`
block.
"""
# pragma: exclude file

from collections.abc import Hashable, Sequence
from typing import TYPE_CHECKING, Union

from pint import Unit
from xarray.core.types import Dims, InterpOptions, ScalarOrArray

from .core.key import KeyLike
from .core.quantity import AnyQuantity

if TYPE_CHECKING:
    # TODO Remove this block once Python 3.10 is the lowest supported version
    from typing import TypeAlias

__all__ = [
    "AnyQuantity",
    "Dims",
    "IndexLabel",
    "InterpOptions",
    "KeyLike",
    "ScalarOrArray",
    "Unit",
]

# Mirror the definition from pandas-stubs
IndexLabel: "TypeAlias" = Union[Hashable, Sequence[Hashable]]
