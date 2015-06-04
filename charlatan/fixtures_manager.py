from __future__ import print_function
from glob import glob
from itertools import chain
import functools
import os

from charlatan import _compat
from charlatan import builder
from charlatan.depgraph import DepGraph
from charlatan.file_format import load_file
from charlatan.fixture import Fixture
from charlatan import fixture_collection

ALLOWED_HOOKS = ("before_save", "after_save", "before_install",
                 "after_install")
ROOT_COLLECTION = "root"


def make_list(obj):
    """Return list of objects if necessary."""
    if isinstance(obj, _compat.string_types):
        return (obj, )
    return obj


class FixturesManager(object):

    """
    Manage Fixture objects.

    :param Session db_session: sqlalchemy Session object
    :param bool use_unicode:
    :param func get_builder:
    :param func delete_builder:

    .. versionadded:: 0.4.0
        ``get_builder`` and ``delete_builder`` arguments were added.

    .. deprecated:: 0.4.0
        ``delete_instance``, ``save_instance`` methods were deleted in favor
        of using builders.

    .. versionadded:: 0.3.0
        ``db_session`` argument was added.
    """

    DictFixtureCollection = fixture_collection.DictFixtureCollection
    ListFixtureCollection = fixture_collection.ListFixtureCollection

    default_get_builder = builder.InstantiateAndSave()
    default_delete_builder = builder.DeleteAndCommit()

    def __init__(self, db_session=None, use_unicode=False,
                 get_builder=None, delete_builder=None,
                 ):
        self.hooks = {}
        self.session = db_session
        self.installed_keys = []
        self.use_unicode = use_unicode
        self.get_builder = get_builder or self.default_get_builder
        self.delete_builder = delete_builder or self.default_delete_builder
        self.filenames = []
        self.collection = self.DictFixtureCollection(
            ROOT_COLLECTION,
            fixture_manager=self,
        )

    def load(self, filenames, models_package=""):
        """Pre-load the fixtures. Does not install anything.

        :param list_or_str filename: file or list of files that holds the
                                     fixture data
        :param str models_package: package holding the models definition

        .. deprecated:: 0.3.0
            ``db_session`` argument was removed and put in the object's
            constructor arguments.

        .. versionchanged:: 0.3.7
            ``filename`` argument was changed to ``filenames``, which can be
            list or string.

        """
        self.filenames.append(filenames)

        self.depgraph = self._load_fixtures(filenames,
                                            models_package=models_package)
        self.clean_cache()

    def _get_namespace_from_filename(self, filename):
        """Get a collection namespace from a fixtures filename.

        :param str filename: filename to extract namespace from
        """
        segments = os.path.basename(filename).split(".")
        if len(segments) > 2:
            raise ValueError("Fixtures filename stem may not contain periods")

        return segments[0]

    def _load_fixtures(self, filenames, models_package=''):
        """Pre-load the fixtures.

        :param list or str filenames: files that hold the fixture data
        :param str models_package:
        """
        if isinstance(filenames, _compat.string_types):
            globbed_filenames = glob(filenames)
        else:
            globbed_filenames = list(
                chain.from_iterable(glob(f) for f in filenames)
            )

        if not globbed_filenames:
            raise IOError('File "%s" not found' % filenames)

        if len(globbed_filenames) == 1:
            content = load_file(globbed_filenames[0], self.use_unicode)
        else:
            content = {}

            for filename in globbed_filenames:
                namespace = self._get_namespace_from_filename(filename)
                content[namespace] = {
                    "objects": load_file(filename, self.use_unicode)
                }

        if content:
            for k, v in _compat.iteritems(content):

                if "objects" in v:
                    # It's a collection of fictures.
                    collection = self._handle_collection(
                        namespace=k,
                        definition=v,
                        objects=v["objects"],
                        models_package=models_package,
                    )
                    self.collection.add(k, collection)

                # Named fixtures
                else:
                    if "id" in v:
                        # Renaming id because it's a Python builtin function
                        v["id_"] = v["id"]
                        del v["id"]

                    fixture = Fixture(
                        key=k,
                        fixture_manager=self,
                        models_package=models_package,
                        **v)
                    self.collection.add(k, fixture)

        graph = self._check_cycle(self.collection)
        return graph

    def _check_cycle(self, collection):
        """Raise an exception if there's a relationship cycle."""
        d = DepGraph()
        for _, fixture in collection:
            for dependency, _ in fixture.extract_relationships():
                d.add_edge(dependency, fixture.key)

        # This does nothing except raise an error if there's a cycle
        d.topo_sort()
        return d

    def _handle_collection(self, namespace, definition, objects,
                           models_package=''):
        """Handle a collection of fixtures.

        :param dict definition: definition of the collection
        :param dict_or_list objects: fixtures in the collection
        :param str models_package:

        """
        if isinstance(objects, list):
            klass = self.ListFixtureCollection
        else:
            klass = self.DictFixtureCollection

        collection = klass(
            key=namespace,
            fixture_manager=self,
            model=definition.get('model'),
            models_package=definition.get('models_package'),
            fields=definition.get('fields'),
            post_creation=definition.get('post_creation'),
            inherit_from=definition.get('inherit_from'),
            depend_on=definition.get('depend_on'),
        )

        for name, new_fields in collection.iterator(objects):
            qualified_name = "%s.%s" % (namespace, name)

            if "objects" in new_fields:
                # A nested collection, either because we're dealing with a file
                # collection or a sub-collection.
                fixture = self._handle_collection(
                    namespace=qualified_name,
                    definition=new_fields,
                    objects=new_fields["objects"]
                )
            else:
                model = new_fields.pop("model", None)
                # In the case of a file collection we'll be dealing with
                # PyYAML's output from that file, which means that individual
                # fixtures in this collection have the "fields" field.
                fields = new_fields.pop("fields", new_fields)
                inherit_from = namespace if model is None else None

                fixture = Fixture(
                    key=qualified_name,
                    fixture_manager=self,
                    # Automatically inherit from the collection
                    inherit_from=inherit_from,
                    fields=fields,
                    model=model,
                    models_package=models_package,
                    # The rest (default fields, etc.) is
                    # automatically inherited from the collection.
                )
            collection.add(name, fixture)

        return collection

    def clean_cache(self):
        """Clean the cache."""
        self.cache = {}
        self.installed_keys = []

    def delete_fixture(self, fixture_key, builder=None):
        """Delete a fixture instance.

        :param str fixture_key:
        :param func builder:

        Before and after the process, the :func:`before_delete` and
        :func:`after_delete` hook are run.

        .. versionadded:: 0.4.0
            ``builder`` argument was added.

        .. deprecated:: 0.4.0
            ``delete_instance`` method renamed to ``delete_fixture`` for
            consistency reason.
        """
        builder = builder or self.delete_builder
        self.get_hook("before_delete")(fixture_key)

        instance = self.cache.get(fixture_key)
        if instance:
            self.cache.pop(fixture_key, None)
            self.installed_keys.remove(fixture_key)
            builder(self, instance)

        self.get_hook("after_delete")(fixture_key)

    def install_fixture(self, fixture_key, overrides=None):
        """Install a fixture.

        :param str fixture_key:
        :param dict overrides: override fields

        :rtype: :data:`fixture_instance`

        .. deprecated:: 0.4.0
            ``do_not_save`` argument was removed.
            ``attrs`` argument renamed ``overrides``.

        .. deprecated:: 0.3.7
            ``include_relationships`` argument was removed.

        """
        builder = functools.partial(self.get_builder,
                                    save=True,
                                    session=self.session)
        self.get_hook("before_install")()

        try:
            instance = self.get_fixture(fixture_key, overrides=overrides,
                                        builder=builder)
        except Exception as exc:
            self.get_hook("after_install")(exc)
            raise

        else:
            self.get_hook("after_install")(None)
            return instance

    def install_fixtures(self, fixture_keys):
        """Install a list of fixtures.

        :param fixture_keys: fixtures to be installed
        :type fixture_keys: str or list of strs
        :rtype: list of :data:`fixture_instance`

        .. deprecated:: 0.4.0
            ``do_not_save`` argument was removed.

        .. deprecated:: 0.3.7
            ``include_relationships`` argument was removed.

        """
        instances = []
        for f in make_list(fixture_keys):
            instances.append(self.install_fixture(f))
        return instances

    def install_all_fixtures(self):
        """Install all fixtures.

        :rtype: list of :data:`fixture_instance`

        .. deprecated:: 0.4.0
            ``do_not_save`` argument was removed.

        .. deprecated:: 0.3.7
            ``include_relationships`` argument was removed.

        """
        return self.install_fixtures(self.keys())

    def uninstall_fixture(self, fixture_key):
        """Uninstall a fixture.

        :param str fixture_key:
        :rtype: ``None``

        .. deprecated:: 0.4.0
            ``do_not_delete`` argument was removed. This function does not
            return anything.
        """
        builder = functools.partial(self.delete_builder,
                                    commit=True,
                                    session=self.session)
        return self.delete_fixture(fixture_key, builder)

    def uninstall_fixtures(self, fixture_keys):
        """Uninstall a list of installed fixtures.

        :param fixture_keys: fixtures to be uninstalled
        :type fixture_keys: str or list of strs
        :rtype: ``None``

        .. deprecated:: 0.4.0
            ``do_not_delete`` argument was removed. This function does not
            return anything.
        """
        for fixture_key in make_list(fixture_keys):
            self.uninstall_fixture(fixture_key)

    def uninstall_all_fixtures(self):
        """Uninstall all installed fixtures.

        :rtype: ``None``

        .. deprecated:: 0.4.0
            ``do_not_delete`` argument was removed. This function does not
            return anything.
        """
        installed_fixtures = list(self.installed_keys)
        installed_fixtures.reverse()
        self.uninstall_fixtures(installed_fixtures)

    def keys(self):
        """Return all fixture keys."""
        return self.collection.fixtures.keys()

    def get_fixture(self, fixture_key, overrides=None, builder=None):
        """Return a fixture instance (but do not save it).

        :param str fixture_key:
        :param dict overrides: override fields
        :param func builder: build builder.
        :rtype: instantiated but unsaved fixture

        .. versionadded:: 0.4.0
            ``builder`` argument was added.
            ``attrs`` argument renamed ``overrides``.

        .. deprecated:: 0.4.0
            ``do_not_save`` argument was removed.

        .. deprecated:: 0.3.7
            ``include_relationships`` argument was removed.
        """
        builder = builder or self.get_builder
        # initialize all parents in topological order
        parents = []
        for fixture in self.depgraph.ancestors_of(fixture_key):
            parents.append(self.get_fixture(fixture, builder=builder))

        # Fixture are cached so that setting up relationships is not too
        # expensive. We don't get the cached version if overrides are
        # overriden.
        returned = None
        if not overrides:
            returned = self.cache.get(fixture_key)

        if not returned:
            returned = self.collection.get_instance(
                fixture_key, overrides=overrides, builder=builder)

            self.cache[fixture_key] = returned
            self.installed_keys.append(fixture_key)

        return returned

    def get_fixtures(self, fixture_keys, builder=None):
        """Get fixtures from iterable.

        :param iterable fixture_keys:
        :rtype: list of instantiated but unsaved fixtures

        .. versionadded:: 0.4.0
            ``builder`` argument was added.

        .. deprecated:: 0.3.7
            ``include_relationships`` argument was removed.
        """
        builder = builder or self.get_builder
        fixtures = []
        for f in fixture_keys:
            fixtures.append(self.get_fixture(f))
        return fixtures

    def get_all_fixtures(self, builder=None):
        """Get all fixtures.

        :param iterable fixture_keys:
        :rtype: list of instantiated but unsaved fixtures

        .. versionadded:: 0.4.0
            ``builder`` argument was added.

        .. deprecated:: 0.3.7
            ``include_relationships`` argument was removed.
        """
        builder = builder or self.get_builder
        return self.get_fixtures(self.keys(), builder=builder)

    def get_hook(self, hook_name):
        """Return a hook.

        :param str hook_name: e.g. ``before_delete``.
        """
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
