import logging
from collections import namedtuple
from functools import partial

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

from genno import Computer, Key
from genno.compat.pyam import computations
from genno.computations import add, load_file

# Skip this entire file if pyam is not installed
pyam = pytest.importorskip("pyam", reason="pyam-iamc not installed")


@pytest.fixture(scope="session")
def scenario():
    """Mock object which resembles ixmp.Scenario."""
    Scenario = namedtuple("Scenario", ["model", "scenario"])
    yield Scenario(model="Canning problem (MESSAGE scheme)", scenario="standard")


# Session scope so that ureg.define() is only called once
@pytest.fixture(scope="session")
def dantzig_computer(test_data_path, scenario, ureg):
    """Computer with minimal contents for below tests."""
    # Add units
    ureg.define("USD = [USD]")
    ureg.define("case = [case]")

    c = Computer()

    # Load files and add to graph
    for name, units in (("ACT", ""), ("var_cost", "USD/case"), ("vom", "USD")):
        # NB need to load the file here in order to identify the dims of each quantity
        qty = load_file(test_data_path / f"dantzig-{name}.csv", name=name, units=units)
        c.add(Key(name, qty.dims), qty, index=True, sums=True)

    # Reduced version of the "total operation & maintenance" calculation in MESSAGEix;
    # for test_concat()
    vom = c.full_key("vom")
    fom = Key("fom", dims=vom.dims)
    c.add(fom, c.get(vom)[0:0], sums=True)
    c.add(Key("tom", dims=vom.dims), add, fom, vom, sums=True)

    # Mock scenario object
    c.add("scenario", scenario)

    yield c


def test_require_compat():
    # New object does not understand "as_pyam" as the name of a computation
    c = Computer()
    assert c._get_comp("as_pyam") is None

    # _require_compat() loads it
    c._require_compat("pyam")
    assert c._get_comp("as_pyam") is not None


def test_as_pyam(dantzig_computer, scenario):
    c = dantzig_computer

    # Quantities for 'ACT' variable at full resolution
    qty = c.get(c.full_key("ACT"))

    # Call as_pyam() with an empty quantity
    p = computations.as_pyam(scenario, qty[0:0], year_time_dim="ya")
    assert isinstance(p, pyam.IamDataFrame)


def test_convert_pyam(dantzig_computer, caplog, tmp_path, test_data_path):
    c = dantzig_computer

    # Key for 'ACT' variable at full resolution
    ACT = c.full_key("ACT")

    # Add a computation that converts ACT to a pyam.IamDataFrame
    c.add(
        "ACT IAMC",
        (
            partial(computations.as_pyam, drop=["yv"], year_time_dim="ya"),
            "scenario",
            ACT,
        ),
    )

    # Result is an IamDataFrame
    idf1 = c.get("ACT IAMC")
    assert isinstance(idf1, pyam.IamDataFrame)

    # …of expected length
    assert len(idf1) == 8

    # …in which variables are not renamed
    assert idf1["variable"].unique() == "ACT"

    # Warning was logged because of extra columns
    assert (
        "genno.compat.pyam.computations",
        logging.WARNING,
        "Extra columns ['h', 'm', 't'] when converting 'ACT' to IAMC format",
    ) in caplog.record_tuples

    # Repeat, using the convert_pyam() convenience function
    def add_tm(df, name="Activity"):
        """Callback for collapsing ACT columns."""
        df["variable"] = f"{name}|" + df["t"] + "|" + df["m"]
        return df.drop(["t", "m"], axis=1)

    # Use the convenience function to add the node
    keys = c.convert_pyam(ACT, "ya", collapse=add_tm)

    # Keys of added node(s) are returned
    assert len(keys) == 1
    key2, *_ = keys
    assert key2 == ACT.name + ":iamc"

    caplog.clear()

    # Result
    idf2 = c.get(key2)
    df2 = idf2.as_pandas()

    # Extra columns have been removed:
    # - m and t by the collapse callback.
    # - h automatically, because 'ya' was used for the year index.
    assert not any(c in df2.columns for c in ["h", "m", "t"])

    # Variable names were formatted by the callback
    reg_var = pd.DataFrame(
        [
            ["san-diego", "Activity|canning_plant|production"],
            ["san-diego", "Activity|transport_from_san-diego|to_chicago"],
            ["san-diego", "Activity|transport_from_san-diego|to_new-york"],
            ["san-diego", "Activity|transport_from_san-diego|to_topeka"],
            ["seattle", "Activity|canning_plant|production"],
            ["seattle", "Activity|transport_from_seattle|to_chicago"],
            ["seattle", "Activity|transport_from_seattle|to_new-york"],
            ["seattle", "Activity|transport_from_seattle|to_topeka"],
        ],
        columns=["region", "variable"],
    )
    assert_frame_equal(df2[["region", "variable"]], reg_var)

    # pyam.computations.write_file() is used, calling pyam.IamDataFrame.to_csv()
    path = tmp_path / "activity.csv"
    c.write(key2, path)

    # File contents are as expected
    assert test_data_path.joinpath("pyam-write.csv").read_text() == path.read_text()

    # Use a name map to replace variable names
    c.add("activity variables", {"Activity|canning_plant|production": "Foo"})
    key3 = c.convert_pyam(
        ACT, "ya", replace_vars="activity variables", collapse=add_tm
    ).pop()
    df3 = c.get(key3).as_pandas()

    # Values are the same; different names
    exp = df2[df2.variable == "Activity|canning_plant|production"][
        "value"
    ].reset_index()
    assert all(exp == df3[df3.variable == "Foo"]["value"].reset_index())

    # Now convert variable cost
    cb = partial(add_tm, name="Variable cost")
    key4 = c.convert_pyam("var_cost", "ya", collapse=cb).pop()
    df4 = c.get(key4).as_pandas().drop(["model", "scenario"], axis=1)

    # Results have the expected units
    assert all(df4["unit"] == "USD / case")

    # Also change units
    key5 = c.convert_pyam("var_cost", "ya", collapse=cb, unit="centiUSD / case").pop()
    df5 = c.get(key5).as_pandas().drop(["model", "scenario"], axis=1)

    # Results have the expected units
    assert all(df5["unit"] == "centiUSD / case")
    assert_series_equal(df4["value"], df5["value"] / 100.0)


def test_concat(dantzig_computer):
    """pyam.computations.concat() passes through to base concat()."""
    c = dantzig_computer

    key = c.add(
        "test", computations.concat, "fom:nl-t-ya", "vom:nl-t-ya", "tom:nl-t-ya"
    )
    c.get(key)
