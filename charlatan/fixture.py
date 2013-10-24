import copy
import functools
import importlib

from charlatan.file_format import RelationshipToken


def get_class(module, klass):
    """Return a class object.

    :param str module: module path
    :param str klass: class name
    """

    try:
        object_module = importlib.import_module(module)
        cls = getattr(object_module, klass)
    except ImportError:
        raise ImportError("Unable to import %s:%s" % (module, klass))

    return cls


class Fixture(object):
    """Represent a fixture that can be installed."""

    def __init__(self, key, fixture_manager,
                 model=None, fields=None,
                 inherit_from=None,
                 post_creation=None, id_=None,
                 depend_on=frozenset()):
        """Create a Fixture object.

        :param str model: model used to instantiate the fixture, e.g.
            "yourlib.toaster:Toaster". If empty, the fields will be used as is.
        :param dict fields: args to be provided when instantiating the fixture
        :param fixture_manager: FixtureManager creating the fixture
        :param dict post_creation: assignment to be done after instantiation
        :param str inherit_from: model to inherit from
        :param list depend_on: A list of relationships to depend on

        """

        if id_ and fields:
            raise TypeError(
                "Cannot provide both id and fields to create fixture.")

        self.key = key
        self.fixture_manager = fixture_manager

        self.database_id = id_
        self.inherit_from = inherit_from
        self._has_updated_from_parent = False

        # Stuff that can be inherited.
        self.model_name = model
        self.fields = fields or {}
        self.post_creation = post_creation or {}
        self.depend_on = depend_on

    def update_with_parent(self):
        """Update the object in place using its chain of inheritance."""

        if self._has_updated_from_parent or not self.inherit_from:
            # Nothing to do
            return

        parent = self.fixture_manager.fixtures[self.inherit_from]
        # Recursive to make sure everything is updated.
        parent.update_with_parent()

        can_be_inherited = ["model_name", "fields", "post_creation", "depend_on"]
        for key in can_be_inherited:
            value = getattr(self, key)
            new_value = None
            if not value:
                # We take the parent.
                new_value = getattr(parent, key)

            elif isinstance(value, basestring):
                continue  # The children value takes precedence.

            elif hasattr(value, "update"):  # Most probably a dict
                new_value = copy.deepcopy(getattr(parent, key))
                new_value.update(value)

            if new_value:
                setattr(self, key, new_value)

    def get_instance(self, include_relationships=True):
        """Instantiate the fixture using the model and return the instance.

        :param boolean include_relationships: false if relationships should be
            removed.
        """

        self.update_with_parent()

        if self.database_id:
            object_class = self.get_class()
            # No need to create a new object, just get it from the db
            instance = (
                self.fixture_manager.session.query(object_class)
                .get(self.database_id)
            )

        else:
            # We need to do a copy since we're modifying them.
            fields = copy.deepcopy(self.fields)
            # Get the class to instantiate
            object_class = self.get_class()

            # Does not return anything, does the modification in place (in
            # fields)
            self._process_relationships(fields,
                                        remove=not include_relationships)

            if object_class:
                instance = object_class(**fields)
            else:
                # Return the fields as is. This allows to enter dicts
                # and lists directly.
                instance = fields

        # Do any extra assignment
        for attr, value in self.post_creation.items():
            if isinstance(value, RelationshipToken):
                value = self.get_relationship(value)

            setattr(instance, attr, value)

        return instance

    def get_class(self):
        """Return class object for this instance."""

        root_models_package = self.fixture_manager.models_package

        if not self.model_name:
            return

        # Relative path, e.g. ".toaster:Toaster"
        if ":" in self.model_name and self.model_name[0] == ".":
            module, klass = self.model_name.split(":")
            module = root_models_package + module
            return get_class(module, klass)

        # Absolute import, e.g. "yourlib.toaster:Toaster"
        if ":" in self.model_name:
            module, klass = self.model_name.split(":")
            return get_class(module, klass)

        # Class alone, e.g. "Toaster".
        # Trying to import from e.g.  yourlib.toaster:Toaster
        module = "{models_package}.{model}".format(
            models_package=root_models_package,
            model=self.model_name.lower())
        klass = self.model_name

        return get_class(module, klass)

    @staticmethod
    def extract_rel_name(name):
        """Helper function to extract the relationship and attr from an argument to !rel"""

        rel_name = name  # e.g. toaster.color
        attr = None

        # TODO: we support only one level for now
        if "." in name:
            rel_name, attr = name.split(".")
        return rel_name, attr

    def extract_relationships(self):
        """Iterator of all relationships and dependencies for this fixture"""

        # TODO: make this DRYer since it's mostly copied from _process_relationships

        for dep in self.depend_on:
            yield dep, None

        # For dictionaries, iterate over key, value and for lists iterate over
        # index, item
        if hasattr(self.fields, 'iteritems'):
            field_iterator = self.fields.iteritems()
        else:
            field_iterator = enumerate(self.fields)

        for name, value in field_iterator:
            # One to one relationship
            if isinstance(value, RelationshipToken):
                yield self.extract_rel_name(value)
            # One to many relationship
            elif isinstance(value, (tuple, list)):
                for i, nested_value in enumerate(value):
                    if isinstance(nested_value, RelationshipToken):
                        yield self.extract_rel_name(nested_value)

    def _process_relationships(self, fields, remove=False):
        """Create any relationship if needed.

        :param dict fields: fields to be processed
        :param boolean remove: true if relationships should be removed

        For each field that is a relationship or a list of relationships,
        instantiate those relationships and update the fields.

        Does not return anything, modify fields in place.
        """

        # FIXME: no error when trying to do circular relationship
        # FIXME: no error on stange objects

        # For dictionaries, iterate over key, value and for lists iterate over
        # inex, item
        if hasattr(fields, 'iteritems'):
            field_iterator = fields.iteritems()
        else:
            field_iterator = enumerate(fields)

        for name, value in field_iterator:
            # One to one relationship
            if isinstance(value, RelationshipToken):
                if remove:
                    del fields[name]
                else:
                    fields[name] = self.get_relationship(value)

            # One to many relationship
            elif isinstance(value, (tuple, list)):
                for i, nested_value in enumerate(value):
                    if isinstance(nested_value, RelationshipToken):
                        if remove:
                            del fields[name]
                        else:
                            fields[name][i] = (
                                self.get_relationship(nested_value)
                            )

    def get_relationship(self, name):
        """Get a relationship and its attribute if necessary."""

        # This function is needed so that this fixture can require other
        # fixtures. If a fixture requires another fixture, it
        # necessarily means that it needs to include other relationships
        # as well.
        get_fixture = functools.partial(self.fixture_manager.get_fixture,
                                        include_relationships=True)

        rel_name, attr = self.extract_rel_name(name)
        rel = get_fixture(rel_name)

        if attr:
            return getattr(rel, attr)
        else:
            return rel
