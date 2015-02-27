from charlatan import _compat, utils
from charlatan.fixture import Inheritable


def _sorted_iteritems(dct):
    """Iterate over the items in the dict in a deterministic fashion."""
    for k, v in sorted(_compat.iteritems(dct)):
        yield k, v


class FixtureCollection(Inheritable):

    """A FixtureCollection holds Fixture objects."""

    def __init__(self, key, fixture_manager,
                 model=None,
                 models_package=None,
                 fields=None,
                 post_creation=None,
                 inherit_from=None,
                 depend_on=None,
                 fixtures=None):
        super(FixtureCollection, self).__init__()
        self.key = key
        self.fixture_manager = fixture_manager
        self.fixtures = fixtures or self.container()

        self.key = key

        self.inherit_from = inherit_from
        self._has_updated_from_parent = False

        # Stuff that can be inherited.
        self.fields = fields or {}
        self.model_name = model
        self.models_package = models_package
        self.post_creation = post_creation or {}
        self.depend_on = depend_on

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.key)

    def __iter__(self):
        return self.iterator(self.fixtures)

    def get_instance(self, path=None, overrides=None, builder=None):
        """Get an instance.

        :param str path:
        :param dict overrides:
        :param func builder:
        """
        if not path:
            return self.get_all_instances(overrides=overrides, builder=builder)

        remaining_path = ''
        if isinstance(path, _compat.string_types):
            path = path.split(".")
            first_level = path[0]
            remaining_path = ".".join(path[1:])

        # First try to get the fixture from the cache
        instance = self.fixture_manager.cache.get(first_level)
        if (not overrides
                and instance
                and not isinstance(instance, FixtureCollection)):
            if not remaining_path:
                return instance
            return utils.richgetter(instance, remaining_path)

        # Or just get it
        fixture = self.get(first_level)
        # Then we ask it to return an instance.
        return fixture.get_instance(path=remaining_path,
                                    overrides=overrides,
                                    builder=builder,
                                    )

    def get_all_instances(self, overrides=None, builder=None):
        """Get all instances.

        :param dict overrides:
        :param func builder:

        .. deprecated:: 0.4.0
            Removed format argument.
        """
        returned = []
        for name, fixture in self:
            instance = fixture.get_instance(overrides=overrides,
                                            builder=builder)
            returned.append((name, instance))

        if self.container is dict:
            return dict(returned)
        elif self.container is list:
            return list(map(lambda f: f[1], returned))
        else:
            raise ValueError('Unknown container')

    def extract_relationships(self):
        # Just proxy to fixtures in this collection.
        for _, fixture in self:
            for r in fixture.extract_relationships():
                yield r


class DictFixtureCollection(FixtureCollection):
    iterator = staticmethod(_sorted_iteritems)
    container = dict

    def add(self, name, fixture):
        self.fixtures[str(name)] = fixture

    def get(self, path):
        """Return a single fixture.

        :param str path:
        """
        if path not in self.fixtures:
            raise KeyError("No such fixtures: '%s'" % path)

        return self.fixtures[path]


class ListFixtureCollection(FixtureCollection):
    iterator = enumerate
    container = list

    def add(self, _, fixture):
        self.fixtures.append(fixture)

    def get(self, path):
        """Return a single fixture.

        :param str path:
        """
        return self.fixtures[int(path)]
