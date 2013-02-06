import yaml

from charlatan.file_format import configure_yaml
from charlatan.fixture import Fixture


# TODO: refactor so that the Mixin and the class are less coupled and
# more DRY
# TODO: have more hooks
# TODO: have more consistent hooks (function params and names)
# TODO: complain if not loaded
# TODO: fixture should be the general cases, not install_fixture*s*
# TODO: check if the row still exists instead of requiring clean cache


ALLOWED_HOOKS = ("before_save", "after_save", "before_install", "after_install")


def load_file(filename):
    """Load fixtures definition from file.

    :param str filename:
    """

    with open(filename) as f:
        content = f.read()

    if filename.endswith(".yaml"):
        # Load the custom YAML tags
        configure_yaml()
        content = yaml.load(content)
    else:
        raise KeyError("Unsupported filetype: '%s'" % filename)

    return content


class FixturesManager(object):

    """Manage Fixture objects."""

    def __init__(self):
        self.hooks = {}

    def load(self, filename, db_session, models_package):
        """Pre-load the fixtures.

        :param str filename: file that holds the fixture data
        :param Session session: sqlalchemy Session object
        :param str models_package: package holding the models definition

        Note that this does not effectively instantiate anything. It just does
        some pre-instantiation work, like prepending the root model package
        and doing some basic sanity check.
        """

        self.filename = filename
        self.models_package = models_package
        self.session = db_session

        # Load the data
        self.fixtures = self._load_fixtures(self.filename)

        # Initiate the cache
        self.clean_cache()

    def _load_fixtures(self, filename):
        """Pre-load the fixtures.

        :param str filename: file that holds the fixture data
        """

        content = load_file(filename)

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
        self.cache = {}

    def install_fixture(self, fixture_key, do_not_save=False,
                        include_relationships=True):
        """Install a fixture."""

        instance = self.get_fixture(fixture_key,
                                    include_relationships=include_relationships)

        # Save the instances
        if not do_not_save:
            self._get_hook("before_install")(instance)
            self.session.add(instance)
            self.session.commit()
            self._get_hook("after_install")(instance)

        return instance

    def install_fixtures(self, fixtures_keys, do_not_save=False,
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

        instances = []
        for f in fixtures_keys:
            instances.append(self.install_fixture(
                f,
                do_not_save=do_not_save,
                include_relationships=include_relationships))

        return instances

    def install_all(self, do_not_save=False, include_relationships=True):
        """Install all fixtures.

        :param boolean do_not_save: true if fixture should not be saved
        :param boolean include_relationships: false if relationships should be
            removed.

        :rtype: list of (:data:`fixture_key`, :data:`fixture_instance`) tuples.
        """

        return self.install_fixtures(self.fixtures.keys(),
                                     do_not_save=do_not_save,
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

    def get_fixtures(self, fixtures_key):
        """Return a list of fixtures instances."""
        return [self.get_fixture(f) for f in fixtures_key]

    def _get_hook(self, hook_name):
        """Return a hook."""

        if hook_name in self.hooks:
            return self.hooks[hook_name]

        return lambda *args: None

    def set_hook(self, hookname, func):
        """Add a hook.

        :param str hookname:
        :param function func:
        """

        if not hookname in ALLOWED_HOOKS:
            raise KeyError("'%s' is not an allowed hook." % hookname)

        self.hooks[hookname] = func


FIXTURES_MANAGER = FixturesManager()


class FixturesManagerMixin(object):

    """Class from which test cases should inherit to use fixtures."""

    def get_fixture(self, fixture_key):
        return FIXTURES_MANAGER.get_fixture(fixture_key)

    def get_fixtures(self, fixtures_key):
        return FIXTURES_MANAGER.get_fixtures(fixtures_key)

    def install_fixture(self, fixture_key, do_not_save=False):
        instance = FIXTURES_MANAGER.install_fixture(fixture_key,
                                                    do_not_save=do_not_save)
        setattr(self, fixture_key, instance)
        return instance

    def install_fixtures(self, fixtures_key, do_not_save=False):

        # Let's be forgiving
        if isinstance(fixtures_key, basestring):
            fixtures_key = (fixtures_key, )

        for f in fixtures_key:
            self.install_fixture(f, do_not_save=do_not_save)

    def install_all_fixtures(self, do_not_save=False):
        self.install_fixtures(FIXTURES_MANAGER.fixtures.keys(),
                              do_not_save=do_not_save)

    def clean_fixtures_cache(self):
        FIXTURES_MANAGER.clean_cache()
