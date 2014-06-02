from __future__ import print_function

from charlatan import _compat
from charlatan.depgraph import DepGraph
from charlatan.file_format import load_file
from charlatan.fixture import Fixture
from charlatan.fixture_collection import ListFixtureCollection
from charlatan.fixture_collection import DictFixtureCollection

ALLOWED_HOOKS = ("before_save", "after_save", "before_install",
                 "after_install")
ROOT_COLLECTION = "root"


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


def make_list(obj):
    """Return list of objects if necessary."""
    if isinstance(obj, _compat.string_types):
        return (obj, )
    return obj


class FixturesManager(object):

    """
    Manage Fixture objects.

    :param Session db_session: sqlalchemy Session object

    .. versionadded:: 0.3.0
        ``db_session`` argument was added.

    """

    def __init__(self, db_session=None, use_unicode=False):
        self.hooks = {}
        self.session = db_session
        self.installed_keys = []
        self.use_unicode = use_unicode

    def load(self, filename, models_package=""):
        """Pre-load the fixtures.

        :param str filename: file that holds the fixture data
        :param str models_package: package holding the models definition

        Note that this does not effectively instantiate anything. It just does
        some pre-instantiation work, like prepending the root model package
        and doing some basic sanity check.

        .. versionchanged:: 0.3.0
            ``db_session`` argument was removed and put in the object's
            constructor arguments.

        """

        self.filename = filename
        self.models_package = models_package

        # Load the data
        fixtures, self.depgraph = self._load_fixtures(self.filename)
        self.fixture_collection = DictFixtureCollection(
            ROOT_COLLECTION,
            fixture_manager=self,
            fixtures=fixtures)

        # Initiate the cache
        self.clean_cache()

    def _load_fixtures(self, filename):
        """Pre-load the fixtures.

        :param str filename: file that holds the fixture data
        """

        content = load_file(filename, self.use_unicode)

        fixtures = {}
        for k, v in _compat.iteritems(content):

            if "objects" in v:
                # It's a collection of fictures.
                fixtures[k] = self._handle_collection(
                    namespace=k,
                    definition=v,
                    objects=v["objects"],
                )

            # Named fixtures
            else:
                if "id" in v:
                    # Renaming id because it's a Python builtin function
                    v["id_"] = v["id"]
                    del v["id"]

                fixtures[k] = Fixture(key=k, fixture_manager=self, **v)

        d = DepGraph()
        for fixture in fixtures.values():
            for dependency, _ in fixture.extract_relationships():
                d.add_edge(dependency, fixture.key)

        # This does nothing except raise an error if there's a cycle
        d.topo_sort()
        return fixtures, d

    def _handle_collection(self, namespace, definition, objects):
        """Handle a collection of fixtures.

        :param dict definition: definition of the collection
        :param dict_or_list objects: fixtures in the collection

        """

        if isinstance(objects, list):
            klass = ListFixtureCollection
        else:
            klass = DictFixtureCollection

        collection = klass(
            key=namespace,
            fixture_manager=self,
            model=definition.get('model'),
            fields=definition.get('fields'),
            post_creation=definition.get('post_creation'),
            inherit_from=definition.get('inherit_from'),
            depend_on=definition.get('depend_on'),
        )

        for name, new_fields in collection.iterator(objects):
            qualified_name = "%s.%s" % (namespace, name)

            fixture = Fixture(
                key=qualified_name,
                fixture_manager=self,
                # Automatically inherit from the collection
                inherit_from=namespace,
                fields=new_fields,
                # The rest (model, default fields, etc.) is
                # automatically inherited from the collection.
            )
            collection.add(name, fixture)

        return collection

    def clean_cache(self):
        """Clean the cache."""
        self.cache = {}
        self.installed_keys = []

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

    def delete_instance(self, instance):
        """Delete a fixture instance.

        If it's a SQLAlchemy model, it will be deleted from the session and the
        session will be committed.

        Otherwise, :meth:`delete_instance` will be run first. If the instance
        does not have it, :meth:`delete` will be run. If the instance does not
        have it, nothing will happen.

        Before and after the process, the :func:`before_delete` and
        :func:`after_delete` hook are run.

        """

        self._get_hook("before_delete")(instance)

        if self.session and is_sqlalchemy_model(instance):
            self.session.delete(instance)
            self.session.commit()

        else:
            try:
                getattr(instance, "delete_instance")()
            except AttributeError:
                getattr(instance, "delete", lambda: None)()

        self._get_hook("after_delete")(instance)

    def install_fixture(self, fixture_key, do_not_save=False,
                        include_relationships=True, attrs=None):

        """Install a fixture.

        :param str fixture_key:
        :param bool do_not_save: True if fixture should not be saved.
        :param bool include_relationships: False if relationships should be
            removed.
        :param dict attrs: override fields

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
        instances = []
        for f in make_list(fixture_keys):
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
            self.keys(),
            do_not_save=do_not_save,
            include_relationships=include_relationships)

    def uninstall_fixture(self, fixture_key, do_not_delete=False):
        """Uninstall a fixture.

        :param str fixture_key:
        :param bool do_not_delete: True if fixture should not be deleted.

        :rtype: :data:`fixture_instance` or None if no instance was uninstalled
        with the given key
        """

        try:
            self._get_hook("before_uninstall")()
            instance = self.cache.get(fixture_key)
            if instance:
                self.cache.pop(fixture_key, None)
                self.installed_keys.remove(fixture_key)

                # delete the instance
                if not do_not_delete:
                    self.delete_instance(instance)

        except Exception as exc:
            self._get_hook("after_uninstall")(exc)
            raise

        else:
            self._get_hook("after_uninstall")(None)
            return instance

    def uninstall_fixtures(self, fixture_keys, do_not_delete=False):
        """Uninstall a list of installed fixtures.

        If a given fixture was not previously installed, nothing happens and
        its instance is not part of the returned list.

        :param fixture_keys: fixtures to be uninstalled
        :type fixture_keys: str or list of strs
        :param bool do_not_delete: True if fixture should not be deleted.

        :rtype: list of :data:`fixture_instance`
        """
        instances = []
        for fixture_key in make_list(fixture_keys):
            instance = self.uninstall_fixture(fixture_key, do_not_delete)
            if instance:
                instances.append(instance)

        return instances

    def uninstall_all_fixtures(self, do_not_delete=False):
        """Uninstall all installed fixtures.

        :param bool do_not_delete: True if fixture should not be deleted.

        :rtype: list of :data:`fixture_instance`
        """
        installed_fixtures = list(self.installed_keys)
        installed_fixtures.reverse()
        return self.uninstall_fixtures(installed_fixtures)

    def keys(self):
        """Return all fixture keys."""
        return self.fixture_collection.fixtures.keys()

    def get_fixture(self, fixture_key, include_relationships=True, attrs=None):
        """Return a fixture instance (but do not save it).

        :param str fixture_key:
        :param bool include_relationships: False if relationships should be
            removed.
        :param dict attrs: override fields

        :rtype: instantiated but unsaved fixture
        """
        # initialize all parents in topological order
        parents = []
        for fixture in self.depgraph.ancestors_of(fixture_key):
            parents.append(
                self.get_fixture(
                    fixture,
                    include_relationships=include_relationships,
                )
            )

        # Fixture are cached so that setting up relationships is not too
        # expensive. We don't get the cached version if attrs are
        # overriden.
        returned = None
        if not attrs:
            returned = self.cache.get(fixture_key)

        if not returned:
            returned = self.fixture_collection.get_instance(
                fixture_key,
                include_relationships=include_relationships,
                fields=attrs,
            )

            self.cache[fixture_key] = returned
            self.installed_keys.append(fixture_key)

        return returned

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

        if hookname not in ALLOWED_HOOKS:
            raise KeyError("'%s' is not an allowed hook." % hookname)

        self.hooks[hookname] = func
