from charlatan import _compat
from charlatan.fixture import Inheritable

LIST_FORMAT = "as_list"
DICT_FORMAT = "as_dict"


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
        if not path or path in (DICT_FORMAT, LIST_FORMAT):
            return self.get_all_instances(overrides=overrides,
                                          format=path,
                                          builder=builder,
                                          )

        # First get the fixture
        fixture, remaining_path = self.get(path)
        # Then we ask it to return an instance.
        return fixture.get_instance(path=remaining_path,
                                    overrides=overrides,
                                    builder=builder,
                                    )

    def get_all_instances(self, overrides=None, format=None, builder=None):
        """Get all instance.

        :param dict overrides:
        :param str format:
        :param func builder:
        """
        if not format:
            format = self.default_format

        if format == LIST_FORMAT:
            returned = []
        elif format == DICT_FORMAT:
            returned = {}
        else:
            raise ValueError("Unknown format: %r" % format)

        for name, fixture in self:
            instance = fixture.get_instance(overrides=overrides,
                                            builder=builder)

            if format == LIST_FORMAT:
                returned.append(instance)
            else:
                returned[name] = instance

        return returned

    def extract_relationships(self):
        # Just proxy to fixtures in this collection.
        for _, fixture in self:
            for r in fixture.extract_relationships():
                yield r


class DictFixtureCollection(FixtureCollection):
    default_format = DICT_FORMAT
    iterator = staticmethod(_sorted_iteritems)
    container = dict

    def add(self, name, fixture):
        self.fixtures[str(name)] = fixture

    def get(self, path):
        """Return a single fixture.

        :param str path:
        """
        # Note: this can't be used with 'as_list' etc.

        if isinstance(path, _compat.string_types):
            path = path.split(".")

        if not path[0] in self.fixtures:
            raise KeyError("No such fixtures: '%s'" % path[0])

        return self.fixtures[path[0]], ".".join(path[1:])


class ListFixtureCollection(FixtureCollection):
    default_format = LIST_FORMAT
    iterator = enumerate
    container = list

    def add(self, _, fixture):
        self.fixtures.append(fixture)

    def get(self, path):
        """Return a single fixture.

        :param str path:
        """
        path = path.split(".")
        return self.fixtures[int(path[0])], ".".join(path[1:])
