import operator
import weakref

import yaml

from charlatan.file_format import configure_yaml
from charlatan.fixture import Fixture


class FixturesManager(object):
    """Manage Fixture objects."""

    def __init__(self, filename, session, models_package):
        """Create the fixtures manager.

        :param str filename: file that holds the fixture data
        :param Session session: sqlalchemy Session object
        :param str models_package: package holding the models definition
        """

        self.filename = filename

        self.models_package = models_package
        self.session = session

        # Load the data
        self.fixtures = self._load_file()

        # Initiate the cache
        self.clean_cache()

    def _load_file(self):
        """Load the file containing fixtures."""

        with open(self.filename) as f:
            content = f.read()

        # Load the custom YAML tags
        configure_yaml()

        if self.filename.endswith(".yaml"):
            content = yaml.load(content)
        else:
            raise KeyError("Unsupported filetype: '%s'" % self.filename)

        return self._load_fixtures(content)

    def _load_fixtures(self, content):
        """Pre-load the fixtures.

        Note that this does not effectively instantiate anything. It just does
        some pre-instantiation work, like prepending the root model package
        and doing some basic sanity check.
        """

        fixtures = {}
        for k, v in content.items():

            # Unnamed fixtures
            if "objects" in v:

                # v["objects"] is a list of fixture fields dict
                for i, fields in enumerate(v["objects"]):
                    key = k + "_" + str(i)
                    fixtures[key] = Fixture(key=key, fixture_manager=self,
                                            model=v["model"], fields=fields)

            # Named fixtures
            else:
                if "id" in v:
                    # Renaming id because it's a Python builtin function
                    v["id_"] = v["id"]
                    del v["id"]

                if not "model" in v:
                    raise KeyError("Model is not defined for fixture '%s'" % k)

                fixtures[k] = Fixture(key=k, fixture_manager=self, **v)

        return fixtures

    def clean_cache(self):
        """Clean the cache."""
        self.cache = weakref.WeakValueDictionary()

    def install(self, fixtures_keys, do_not_save=False,
                include_relationships=True):
        """Install a list of fixtures.

        :param fixture_keys: fixtures to be installed
        :type fixture_keys: str or list of strs
        :param boolean do_not_save: true if fixture should not be saved
        :param boolean include_relationships: false if relationships should be
            removed.

        :rtype: list of (:data:`fixture_key`, :data:`fixture_instance`) tuples.
        """

        if isinstance(fixtures_keys, basestring):
            fixtures_keys = (fixtures_keys, )

        # Creates a list of (fixture_key, fixture_instance) tuples
        instances = []
        for fixture_key in fixtures_keys:
            fixture = self.get_fixture(fixture_key,
                                       include_relationships=include_relationships)
            instances.append((fixture_key, fixture))

        # Save the instances
        if not do_not_save:
            self.session.add_all(map(operator.itemgetter(1), instances))
            self.session.commit()

        return instances

    def install_all(self, do_not_save=False, include_relationships=True):
        """Install all fixtures.

        :param boolean do_not_save: true if fixture should not be saved
        :param boolean include_relationships: false if relationships should be
            removed.

        :rtype: list of (:data:`fixture_key`, :data:`fixture_instance`) tuples.
        """

        return self.install(self.fixtures.keys(), do_not_save=True,
                            include_relationships=include_relationships)

    def get_fixture(self, fixture_key, include_relationships=True):
        """Return a fixture instance (but do not save it).

        :param boolean include_relationships: false if relationships should be
            removed.

        :rtype: instantiated fixture
        """

        if not fixture_key in self.fixtures:
            raise KeyError("No such fixtures: '%s'" % fixture_key)

        # Fixture are cached so that setting up relationships is not too
        # expensive.
        if not self.cache.get(fixture_key):
            instance = self.fixtures[fixture_key].get_instance(
                include_relationships=include_relationships)
            self.cache[fixture_key] = instance
            return instance

        else:
            return self.cache[fixture_key]
