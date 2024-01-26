from types import ModuleType
from typing import Dict, Hashable, Iterable, List, Mapping, Optional, Tuple, Union

from genno import Quantity

try:
    import sdmx
except ModuleNotFoundError:  # pragma: no cover
    HAS_SDMX = False
else:
    HAS_SDMX = True


__all__ = [
    "codelist_to_groups",
    "dataset_to_quantity",
    "quantity_to_dataset",
]


def codelist_to_groups(
    codes: Union["sdmx.model.common.Codelist", Iterable["sdmx.model.common.Code"]],
    dim: Optional[str] = None,
) -> Mapping[str, Mapping[str, List[str]]]:
    """Convert `codes` into a mapping from parent items to their children.

    The returned value is suitable for use with :func:`~.operator.aggregate`.

    Parameters
    ----------
    codes
        Either a :class:`sdmx.Codelist <sdmx.model.common.Codelist>` object or any
        iterable of :class:`sdmx.Code <sdmx.model.common.Code>`.
    dim : str, optional
        Dimension to aggregate. If `codes` is a code list and `dim` is not given, the
        ID of the code list is used; otherwise `dim` must be supplied.
    """
    from sdmx.model.common import Codelist

    if isinstance(codes, Codelist):
        items: Iterable["sdmx.model.common.Code"] = codes.items.values()
        dim = dim or codes.id
    else:
        items = codes

    if dim is None:
        raise ValueError("Must provide a dimension ID for aggregation")

    groups = dict()
    for code in filter(lambda c: len(c.child), items):
        groups[code.id] = list(map(str, code.child))

    return {dim: groups}


def _od(
    value: Union[str, "sdmx.model.common.DimensionComponent", None],
    structure: "sdmx.model.common.BaseDataStructureDefinition",
) -> Optional["sdmx.model.common.DimensionComponent"]:
    if isinstance(value, sdmx.model.common.Dimension) or value is None:
        return value
    elif value is not None:
        return structure.dimensions.get(value)


def _urn(obj: "sdmx.model.common.MaintainableArtefact") -> str:
    if result := obj.urn:  # pragma: no cover
        return result
    else:
        return sdmx.urn.make(obj)


def _version_mod(
    version: Union["sdmx.format.Version", str, None],
) -> Tuple["sdmx.format.Version", ModuleType]:
    """Handle `version` argument."""
    from sdmx.format import Version

    # Ensure a Version enum member
    if not isinstance(version, Version):
        version = Version[version or "2.1"]

    # Retrieve information model module
    im = {Version["2.1"]: sdmx.model.v21, Version["3.0.0"]: sdmx.model.v30}[version]

    return version, im


def dataset_to_quantity(ds: "sdmx.model.common.BaseDataSet") -> Quantity:
    """Convert :class:`DataSet <sdmx.model.common.BaseDataSet>` to :class:`.Quantity.

    Returns
    -------
    Quantity
        The quantity may have the attributes:

        - "dataflow_urn": :attr:`urn <sdmx.model.common.MaintainableArtefact.urn>` of
          the :class:`Dataflow` referenced by the :attr:`described_by
          <sdmx.model.common.DataSet.described_by>` attribute of `ds`, if any.
        - "structure_urn": :attr:`urn <sdmx.model.common.MaintainableArtefact.urn>` of
          the :class:`DataStructureDefinition
          <sdmx.model.common.BaseDataStructureDefinition>` referenced by the
          :attr:`structured_by <sdmx.model.common.DataSet.structured_by>` attribute of
          `ds`, if any.
    """
    # Assemble attributes
    attrs: Dict[str, str] = {}
    if ds.described_by:  # pragma: no cover
        attrs.update(dataflow_urn=_urn(ds.described_by))
    if ds.structured_by:
        attrs.update(structure_urn=_urn(ds.structured_by))

    return Quantity(sdmx.to_pandas(ds), attrs=attrs)


def quantity_to_dataset(
    qty: Quantity,
    structure: "sdmx.model.common.BaseDataStructureDefinition",
    *,
    observation_dimension: Optional[str] = None,
    version: Union["sdmx.format.Version", str, None] = None,
) -> "sdmx.model.common.BaseDataSet":
    """Convert :class:`.Quantity to :class:`DataSet <sdmx.model.common.BaseDataSet>`.

    The resulting data set is structure-specific and flat (not grouped into Series).
    """
    # Handle `version` argument, identify classes
    _, m = _version_mod(version)
    DataSet = m.get_class("StructureSpecificDataSet")
    Observation = m.get_class("Observation")
    Key = sdmx.model.common.Key
    SeriesKey = sdmx.model.common.SeriesKey

    # Narrow type
    # NB This is necessary because BaseDataStructureDefinition.measures is not defined
    # TODO Remove once addressed upstream
    assert isinstance(
        structure,
        (
            sdmx.model.v21.DataStructureDefinition,
            sdmx.model.v30.DataStructureDefinition,
        ),
    )

    try:
        # URN of DSD stored on `qty` matches `structure`
        assert qty.attrs["structure_urn"] == _urn(structure)
    except KeyError:
        pass  # No such attribute

    # Dimensions; should be equivalent to the IDs of structure.dimensions
    dims = qty.dims

    # Create data set
    ds = DataSet(structured_by=structure)
    measure = structure.measures[0]

    if od := _od(observation_dimension, structure):
        # Index of `observation_dimension`
        od_index = dims.index(od.id)
        # Group data / construct SeriesKey all *except* the observation_dimension
        series_dims = list(dims[:od_index] + dims[od_index + 1 :])
        grouped: Iterable = qty.to_series().groupby(series_dims)
        # For as_obs()
        obs_dims: Tuple[Hashable, ...] = (od.id,)
        key_slice = slice(od_index, od_index + 1)
    else:
        # Pseudo-groupby object
        grouped = [(None, qty.to_series())]
        obs_dims, key_slice = dims, slice(None)

    def as_obs(key, value):
        """Convert a single pd.Series element to an sdmx Observation."""
        return Observation(
            # Select some or all elements of the SeriesGroupBy key
            dimension=structure.make_key(Key, dict(zip(obs_dims, key[key_slice]))),
            value_for=measure,
            value=value,
        )

    for series_key, data in grouped:
        if series_key:
            sk = structure.make_key(SeriesKey, dict(zip(series_dims, series_key)))
        else:
            sk = None

        # - Convert each item to an sdmx Observation.
        # - Add to `ds`, associating with sk
        ds.add_obs([as_obs(key, value) for key, value in data.items()], series_key=sk)

    return ds


def quantity_to_message(
    qty: Quantity, structure: "sdmx.model.v21.DataStructureDefinition", **kwargs
) -> "sdmx.message.DataMessage":
    """Convert :class:`.Quantity to :class:`DataMessage <sdmx.message.DataMessage>`."""
    kwargs.update(
        version=_version_mod(kwargs.get("version"))[0],
        observation_dimension=_od(kwargs.get("observation_dimension"), structure),
    )

    ds = quantity_to_dataset(
        qty,
        structure,
        observation_dimension=kwargs["observation_dimension"],
        version=kwargs["version"],
    )

    return sdmx.message.DataMessage(data=[ds], **kwargs)
