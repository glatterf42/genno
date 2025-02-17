import pytest

from genno import Key, Quantity
from genno.core.graph import Graph


class TestGraph:
    @pytest.fixture
    def g(self):
        g = Graph()
        g["foo:c-b-a"] = 1
        yield g

    def test_contains0(self, g) -> None:
        """__contains__ handles incompatible types, returning False."""
        q = Quantity()
        assert (q in g) is False

    def test_contains1(self, g) -> None:
        """__contains__ handles compatible types."""
        # Compare to a key originally str and unsorted
        assert ("foo:c-b-a" in g) is True
        assert (Key("foo:c-b-a") in g) is True
        assert (Key("foo:a-b-c") in g) is True

        # Compare to a key originally Key and sorted
        g[Key("bar:x-y-z")] = None
        assert ("bar:x-y-z" in g) is True
        assert ("bar:z-x-y" in g) is True
        assert (Key("bar:x-y-z") in g) is True
        assert (Key("bar:z-x-y") in g) is True

    def test_delitem(self, g) -> None:
        assert Key("foo", "cba") == g.full_key("foo")
        del g["foo:c-b-a"]
        assert None is g.full_key("foo")

    def test_infer(self, g) -> None:
        g["foo:x-y-z:bar"] = 2
        g["config"] = dict(baz="qux")

        # Correct result for str or Key argument
        assert "foo:c-b-a" == g.infer("foo")
        assert "foo:c-b-a" == g.infer(Key("foo"))

        # Correct result for str or Key argument with tag
        assert "foo:x-y-z:bar" == g.infer("foo::bar")
        assert "foo:x-y-z:bar" == g.infer(Key("foo", tag="bar"))

        # String passes through
        for k in ("config", "baz"):
            result = g.infer(k)
            assert isinstance(result, str) and k == result

    def test_pop(self, g) -> None:
        assert Key("foo", "cba") == g.full_key("foo")
        assert 1 == g.pop("foo:c-b-a")
        assert None is g.full_key("foo")

    def test_setitem(self, g) -> None:
        g[Key("baz", "cba")] = 2

        assert Key("baz", "cba") == g.unsorted_key(Key("baz", "cab"))

    def test_update(self, g) -> None:
        g.update([("foo:y-x", 1), ("bar:m-n", 2)])
        assert Key("bar", "mn") == g.full_key("bar")

        g.update(baz=3)
        assert Key("baz") == g.unsorted_key("baz")
