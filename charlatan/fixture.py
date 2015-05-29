import copy
import importlib

from charlatan import _compat
from charlatan.file_format import RelationshipToken
from charlatan.utils import safe_iteritems, richgetter, deep_update

CAN_BE_INHERITED = frozenset(
    ["model_name", "models_package", "fields", "post_creation", "depend_on"])


def get_class(module, klass):
    """Return a class object.

    :param str module: module path
    :param str klass: class name
    """
    try:
        object_module = importlib.import_module(module)
        cls = getattr(object_module, klass)
    except (ImportError, TypeError) as e:
        raise ImportError("Unable to import %s:%s. %r" % (module, klass, e))

    return cls


class Inheritable(object):

    def __init__(self, *args, **kwargs):
        # This is to make sure we don't redo the inheritance twice, for
        # performance reason.
        self._has_inherited_from_parent = False
        self.inherit_from = None
        self.deep_inherit = None
        self.fixture_manager = None

    def inherit_from_parent(self):
        """Inherit the attributes from parent, modifying itself."""
        if self._has_inherited_from_parent or not self.inherit_from:
            # Nothing to do
            return

        for name, value in self.get_parent_values():
            setattr(self, name, value)

    def get_parent_values(self):
        """Return parent values."""
        parent = self.fixture_manager.collection.get(self.inherit_from)
        # Recursive to make sure everything is updated.
        parent.inherit_from_parent()

        for key in CAN_BE_INHERITED:
            children_value = getattr(self, key)
            parent_value = getattr(parent, key)
            new_value = None
            if not children_value:
                # If I don't have a value, then we try from the parent
                # no matter what.
                new_value = copy.deepcopy(parent_value)

            elif isinstance(children_value, _compat.string_types):
                # The children value is something, then it takes
                # precedence no matter what.
                continue

            elif hasattr(children_value, "update"):
                # If it's a dict, then we try inheriting from the
                # parent.
                new_value = copy.deepcopy(parent_value)
                if self.deep_inherit:
                    deep_update(new_value, children_value)
                else:
                    new_value.update(children_value)

            if new_value:
                yield key, new_value


class Fixture(Inheritable):

    """Represent a fixture that can be installed."""

    def __init__(self, key, fixture_manager,
                 model=None, fields=None,
                 inherit_from=None,
                 deep_inherit=False,
                 post_creation=None, id_=None,
                 models_package='',
                 depend_on=frozenset()):
        """Create a Fixture object.

        :param str model: model used to instantiate the fixture, e.g.
            "yourlib.toaster:Toaster". If empty, the fields will be used as is.
        :param str models_package: default models package for relative imports
        :param dict fields: args to be provided when instantiating the fixture
        :param fixture_manager: FixturesManager creating the fixture
        :param dict post_creation: assignment to be done after instantiation
        :param str inherit_from: model to inherit from
        :param bool deep_inherit: if True, fields will support nested updates
        :param list depend_on: A list of relationships to depend on

        .. versionadded:: 0.4.5
            ``deep_inherit`` argument added.

        .. versionadded:: 0.4.0
            ``models_package`` argument added.

        """
        super(Fixture, self).__init__()

        if id_ and fields:
            raise ValueError(
                "Cannot provide both id and fields to create fixture.")

        self.key = key
        self.fixture_manager = fixture_manager

        self.database_id = id_
        self.inherit_from = inherit_from
        self.deep_inherit = deep_inherit

        # Stuff that can be inherited.
        self.model_name = model
        self.models_package = models_package
        self.fields = fields or {}
        self.post_creation = post_creation or {}
        self.depend_on = depend_on

    def __repr__(self):
        return "<Fixture '%s'>" % self.key

    def get_instance(self, path=None, overrides=None, builder=None):
        """Instantiate the fixture using the model and return the instance.

        :param str path: remaining path to return
        :param dict overrides: overriding fields
        :param func builder: function that is used to get the fixture

        .. deprecated:: 0.4.0
            ``fields`` argument renamed ``overrides``.

        .. versionadded:: 0.4.0
            ``builder`` argument added.

        .. deprecated:: 0.3.7
            ``include_relationships`` argument removed.

        """
        self.inherit_from_parent()  # Does the modification in place.

        if self.database_id:
            object_class = self.get_class()
            # No need to create a new object, just get it from the db
            instance = (
                self.fixture_manager.session.query(object_class)
                .get(self.database_id)
            )

        else:
            # We need to do a copy since we're modifying them.
            params = copy.deepcopy(self.fields)
            if overrides:
                params.update(overrides)

            for key, value in safe_iteritems(params):
                if callable(value):
                    params[key] = value()

            # Get the class
            object_class = self.get_class()

            # Does not return anything, does the modification in place (in
            # fields).
            self._process_relationships(params)

            if object_class:
                instance = builder(self.fixture_manager, object_class, params)
            else:
                # Return the fields as is. This allows to enter dicts
                # and lists directly.
                instance = params

        # Do any extra assignment
        for attr, value in self.post_creation.items():
            if isinstance(value, RelationshipToken):
                value = self.get_relationship(value)

            setattr(instance, attr, value)

        if path:
            return richgetter(instance, path)
        else:
            return instance

    def get_class(self):
        """Return class object for this instance."""
        if not self.model_name:
            return

        # Relative path, e.g. ".toaster:Toaster"
        if ":" in self.model_name and self.model_name[0] == ".":
            module, klass = self.model_name.split(":")
            module = self.models_package + module
            return get_class(module, klass)

        # Absolute import, e.g. "yourlib.toaster:Toaster"
        if ":" in self.model_name:
            module, klass = self.model_name.split(":")
            return get_class(module, klass)

        # Class alone, e.g. "Toaster".
        # Trying to import from e.g.  yourlib.toaster:Toaster
        module = "{models_package}.{model}".format(
            models_package=self.models_package,
            model=self.model_name.lower())
        klass = self.model_name

        try:
            return get_class(module, klass)
        except ImportError:
            # Then try to import from yourlib:Toaster
            return get_class(self.models_package, klass)

    @staticmethod
    def extract_rel_name(name):
        """Return the relationship and attr from an argument to !rel."""
        rel_name = name  # e.g. toaster.color
        attr = None

        # TODO: we support only one level for now
        if "." in name:
            path = name.split(".")
            rel_name, attr = path[0], path[1]
        return rel_name, attr

    def extract_relationships(self):
        """Return all dependencies.

        :rtype generator:

        Yields ``(depends_on, attr_name)``.

        """
        # TODO: make this DRYer since it's mostly copied from
        # _process_relationships

        for dep in self.depend_on:
            yield dep, None

        for name, value in safe_iteritems(self.fields):
            # One to one relationship
            if isinstance(value, RelationshipToken):
                yield self.extract_rel_name(value)

            # One to many relationship
            elif isinstance(value, (tuple, list)):
                for i, nested_value in enumerate(value):
                    if isinstance(nested_value, RelationshipToken):
                        yield self.extract_rel_name(nested_value)

    def _process_field_relationships(self, field_value):
        """Create any relationship for a field if needed.

        :param mixed field_value: field value to be processed

        For each field that is a relationship or a list of relationships,
        instantiate those relationships and update the fields.

        Returns new field value and modifies lists in place.
        """
        # One to one relationship
        if isinstance(field_value, RelationshipToken):
            return self.get_relationship(field_value)

        # One to many relationship
        elif isinstance(field_value, (tuple, list)):
            for i, nested_value in enumerate(field_value):
                field_value[i] = self._process_field_relationships(
                    nested_value)

        return field_value

    def _process_relationships(self, fields):
        """Create any relationship if needed.

        :param dict fields: fields to be processed

        For each field that is a relationship or a list of relationships,
        instantiate those relationships and update the fields.

        Does not return anything, modify fields in place.
        """
        # For dictionaries, iterate over key, value and for lists iterate over
        # index, item
        if hasattr(fields, 'items'):
            field_iterator = _compat.iteritems(fields)
        else:
            field_iterator = enumerate(fields)

        for name, value in field_iterator:
            fields[name] = self._process_field_relationships(value)

    def get_relationship(self, name):
        """Get a relationship and its attribute if necessary."""
        # This function is needed so that this fixture can require other
        # fixtures. If a fixture requires another fixture, it
        # necessarily means that it needs to include other relationships
        # as well.
        return self.fixture_manager.get_fixture(name)
