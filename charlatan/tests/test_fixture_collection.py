import pytest

from charlatan import FixturesManager


@pytest.fixture(scope="module")
def collection():
    """Return FixtureCollection."""

    manager = FixturesManager()
    manager.load("docs/examples/collection.yaml")
    return manager.fixture_collection.get("toasters")[0]


def test_repr(collection):
    """Verify the repr."""
    assert repr(collection) == "<DictFixtureCollection 'toasters'>"


def test_cant_get_invalid_format(collection):
    """Verify that we can't get an invalid format."""

    with pytest.raises(ValueError):
        collection.get_all_instances(format="invalid")


def test_cant_get_missing_fixture(collection):
    """Verify that we can't get a missing fixture."""

    with pytest.raises(KeyError):
        collection.get("missing")
