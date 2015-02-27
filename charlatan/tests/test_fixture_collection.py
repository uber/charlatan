import pytest

from charlatan import FixturesManager


def get_collection(collection):
    """Return FixtureCollection.

    :param str collection: name of collection to import
    """
    manager = FixturesManager()
    manager.load("docs/examples/collection.yaml")
    return manager.collection.get(collection)


@pytest.fixture(scope="module")
def collection():
    """Return FixtureCollection."""
    return get_collection("toasters")


def test_repr(collection):
    """Verify the repr."""
    assert repr(collection) == "<DictFixtureCollection 'toasters'>"


def test_cant_get_missing_fixture(collection):
    """Verify that we can't get a missing fixture."""
    with pytest.raises(KeyError):
        collection.get("missing")
