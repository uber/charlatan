from charlatan.fixture import Fixture
from charlatan.utils import copy_docstring_from
from charlatan.file_format import load_file
from charlatan.depgraph import DepGraph


# TODO: refactor so that the Mixin and the class are less coupled and
# more DRY
# TODO: have more hooks
# TODO: have more consistent hooks (function params and names)
# TODO: complain if not loaded
# TODO: fixture should be the general cases, not install_fixture*s*
# TODO: check if the row still exists instead of requiring clean cache


ALLOWED_HOOKS = ("before_save", "after_save", "before_install",
                 "after_install")


def is_sqlalchemy_model(instance):
    """Return True if instance is an SQLAlchemy model instance."""

    from sqlalchemy.orm.util import class_mapper
    from sqlalchemy.orm.exc import UnmappedClassError

    try:
        class_mapper(instance.__class__)

    except UnmappedClassError:
        return False

    else:
        return True


class FixturesManager(object):

    """Manage Fixture objects."""

    def __init__(self):
        self.hooks = {}

    def load(self, filename, db_session=None, models_package=None):
        """Pre-load the fixtures.

        :param str filename: file that holds the fixture data
        :param Session db_session: sqlalchemy Session object
        :param str models_package: package holding the models definition

        Note that this does not effectively instantiate anything. It just does
        some pre-instantiation work, like prepending the root model package
        and doing some basic sanity check.
        """

        self.filename = filename
        self.models_package = models_package
        self.session = db_session

        # Load the data
        self.fixtures, self.depgraph = self._load_fixtures(self.filename)

        # Initiate the cache
        self.clean_cache()

    def _load_fixtures(self, filename):
        """Pre-load the fixtures.

        :param str filename: file that holds the fixture data
        """

        content = load_file(filename)

        fixtures = {}
        for k, v in content.items():

            # List of fixtures
            if "objects" in v:

                fixture_list = []
                # v["objects"] is a list of fixture fields dict
                for i, fields in enumerate(v["objects"]):
                    key = k + "_" + str(i)
                    fixture = Fixture(key=key, fixture_manager=self,
                                      model=v.get("model"), fields=fields)

                    fixtures[key] = fixture
                    fixture_list.append(fixture)

                fixtures[k] = fixture_list

            # Named fixtures
            else:
                if "id" in v:
                    # Renaming id because it's a Python builtin function
                    v["id_"] = v["id"]
                    del v["id"]

                fixtures[k] = Fixture(key=k, fixture_manager=self, **v)

        d = DepGraph()

        def add_to_graph(fixture):
            """Closure for adding fixtures to the dependency graph"""
            for dependency, _ in fixture.extract_relationships():
                d.add_edge(dependency, fixture.key)

        for fixture in fixtures.values():
            if isinstance(fixture, list):
                for fix in fixture:
                    add_to_graph(fix)
            else:
                add_to_graph(fixture)

        # this does nothing except raise an error if there's a cycle
        d.topo_sort()
        return fixtures, d

    def clean_cache(self):
        """Clean the cache."""
        self.cache = {}

    def save_instance(self, instance):
        """Save a fixture instance.

        If it's a SQLAlchemy model, it will be added to the session and
        the session will be committed.

        Otherwise, a :meth:`save` method will be run if the instance has
        one. If it does not have one, nothing will happen.

        Before and after the process, the :func:`before_save` and
        :func:`after_save` hook are run.

        """

        self._get_hook("before_save")(instance)

        if self.session and is_sqlalchemy_model(instance):
            self.session.add(instance)
            self.session.commit()

        else:
            getattr(instance, "save", lambda: None)()

        self._get_hook("after_save")(instance)

    def install_fixture(self, fixture_key, do_not_save=False,
                        include_relationships=True, attrs=None):

        """Install a fixture.

        :param str fixture_key:
        :param bool do_not_save: True if fixture should not be saved.
        :param bool include_relationships: False if relationships should be
            removed.

        :rtype: :data:`fixture_instance`
        """

        try:
            self._get_hook("before_install")()
            instance = self.get_fixture(
                fixture_key,
                include_relationships=include_relationships,
                attrs=attrs)

            # Save the instance
            if not do_not_save:
                self.save_instance(instance)

        except Exception as exc:
            self._get_hook("after_install")(exc)
            raise

        else:
            self._get_hook("after_install")(None)
            return instance

    def install_fixtures(self, fixture_keys, do_not_save=False,
                         include_relationships=True):
        """Install a list of fixtures.

        :param fixture_keys: fixtures to be installed
        :type fixture_keys: str or list of strs
        :param bool do_not_save: True if fixture should not be saved.
        :param bool include_relationships: False if relationships should be
            removed.

        :rtype: list of :data:`fixture_instance`
        """

        if isinstance(fixture_keys, basestring):
            fixture_keys = (fixture_keys, )

        instances = []
        for f in fixture_keys:
            instances.append(self.install_fixture(
                f,
                do_not_save=do_not_save,
                include_relationships=include_relationships))

        return instances

    def install_all_fixtures(self, do_not_save=False,
                             include_relationships=True):
        """Install all fixtures.

        :param bool do_not_save: True if fixture should not be saved.
        :param bool include_relationships: False if relationships should be
            removed.

        :rtype: list of :data:`fixture_instance`
        """

        return self.install_fixtures(
            self.fixtures.keys(),
            do_not_save=do_not_save,
            include_relationships=include_relationships)

    def get_fixture(self, fixture_key, include_relationships=True, attrs={}):
        """Return a fixture instance (but do not save it).

        :param str fixture_key:
        :param bool include_relationships: False if relationships should be
            removed.

        :rtype: instantiated but unsaved fixture
        """
        # initialize all parents in topological order
        parents = []
        for fixture in self.depgraph.ancestors_of(fixture_key):
            parents.append(
                self.get_fixture(
                    fixture,
                    include_relationships=include_relationships
                )
            )

        if not fixture_key in self.fixtures:
            raise KeyError("No such fixtures: '%s'" % fixture_key)

        # Fixture are cached so that setting up relationships is not too
        # expensive.
        instance = self.cache.get(fixture_key)
        if not instance:
            fixture = self.fixtures[fixture_key]

            fixture_is_list = isinstance(fixture, list)

            if fixture_is_list:
                instance = [
                    self.get_fixture(f.key, include_relationships, attrs)
                    for f in fixture
                ]
            else:
                instance = fixture.get_instance(
                    include_relationships=include_relationships
                )

            self.cache[fixture_key] = instance

        # If any arguments are passed in, set them before returning. But do not
        # set them on a list of fixtures (they are already set on all elements)
        if attrs and not fixture_is_list:
            for attr, value in attrs.items():
                setattr(instance, attr, value)

        return instance

    def get_fixtures(self, fixture_keys, include_relationships=True):
        """Return a list of fixtures instances.

        :param iterable fixture_keys:
        :param bool include_relationships: False if relationships should be
            removed.

        :rtype: list of instantiated but unsaved fixtures
        """
        fixtures = []
        for f in fixture_keys:
            fixtures.append(
                self.get_fixture(
                    f,
                    include_relationships=include_relationships))
        return fixtures

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

    @copy_docstring_from(FixturesManager)
    def get_fixture(self, fixture_key, include_relationships=True):
        return FIXTURES_MANAGER.get_fixture(
            fixture_key,
            include_relationships=include_relationships)

    @copy_docstring_from(FixturesManager)
    def get_fixtures(self, fixture_keys, include_relationships=True):
        return FIXTURES_MANAGER.get_fixtures(fixture_keys)

    @copy_docstring_from(FixturesManager)
    def install_fixture(self, fixture_key, do_not_save=False,
                        include_relationships=True, attrs=None):

        instance = FIXTURES_MANAGER.install_fixture(
            fixture_key,
            do_not_save=do_not_save,
            include_relationships=include_relationships,
            attrs=attrs)

        setattr(self, fixture_key, instance)
        return instance

    @copy_docstring_from(FixturesManager)
    def install_fixtures(self, fixture_keys, do_not_save=False,
                         include_relationships=True):

        # Let's be forgiving
        if isinstance(fixture_keys, basestring):
            fixture_keys = (fixture_keys, )

        for f in fixture_keys:
            self.install_fixture(f,
                                 do_not_save=do_not_save,
                                 include_relationships=include_relationships)

    @copy_docstring_from(FixturesManager)
    def install_all_fixtures(self, do_not_save=False,
                             include_relationships=True):
        self.install_fixtures(FIXTURES_MANAGER.fixtures.keys(),
                              do_not_save=do_not_save,
                              include_relationships=include_relationships)

    def clean_fixtures_cache(self):
        """Clean the cache."""
        FIXTURES_MANAGER.clean_cache()
