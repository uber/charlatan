import pytest

from charlatan import FixturesManager
from charlatan.tests.fixtures.simple_models import User


def get_collection(collection):
    """Return FixtureCollection.

    :param str collection: name of collection to import
    """

    manager = FixturesManager()
    manager.load("docs/examples/collection.yaml")
    return manager.fixture_collection.get(collection)[0]


@pytest.fixture(scope="module")
def collection():
    """Return FixtureCollection."""

    return get_collection("toasters")


@pytest.fixture(scope="module")
def heterogeneous_collection():
    """Return heterogeneous FixtureCollection."""

    return get_collection("overridden_toasters")


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


def test_collection_members_can_override_model(heterogeneous_collection):
    """Verify that we can override the inherited model for a collection
    member.
    """

    user = heterogeneous_collection.get_instance(
        "user"
    )
    assert isinstance(user, User)
