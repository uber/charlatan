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

    def __init__(self, key, model, fixture_manager, fields=None,
                 post_creation=None, id_=None):
        """Create a Fixture object.

        :param str model: model used to instantiate the fixture, e.g.
            "yourlib.toaster:Toaster".
        :param dict fields: args to be provided when instantiating the fixture
        :param fixture_manager: FixtureManager creating the fixture
        :param dict post_creation: assignment to be done after instantiation
        """

        if id_ and fields:
            raise TypeError(
                "Cannot provide both id and fields to create fixture.")

        self.key = key
        self.model_name = model
        self.fields = fields or {}
        self.fixture_manager = fixture_manager
        self.post_creation = post_creation
        if not self.post_creation:
            self.post_creation = {}

        self.database_id = id_

    def get_instance(self, include_relationships=True):
        """Instantiate the fixture using the model and return the instance.

        :param boolean include_relationships: false if relationships should be
            removed.
        """

        object_class = self.get_class()

        if self.database_id:
            # No need to create a new object, just get it from the db
            instance = self.fixture_manager.session.query(object_class).get(self.database_id)

        else:
            # We need to do a copy since we're modifying them.
            fields = copy.deepcopy(self.fields)

            # Does not return anything, does the modification in place (in
            # fields)
            self._process_relationships(fields,
                                        remove=not include_relationships)

            # instantiate the class
            instance = object_class(**fields)

        # Do any extra assignment
        for attr, value in self.post_creation.items():
            if isinstance(value, RelationshipToken):
                value = self.get_relationship(value)

            setattr(instance, attr, value)

        return instance

    def get_class(self):
        """Return class object for this instance."""

        root_models_package = self.fixture_manager.models_package

        # If model_name starts with a lowercase, then it's an absolute
        # import, e.g. "yourlib.toaster:Toaster"
        if self.model_name[0].islower():
            module, klass = self.model_name.split(":")
            return get_class(module, klass)

        # Relative path, e.g. ".toaster:Toaster"
        if self.model_name[0] == ".":
            module, klass = self.model_name.split(":")
            module = root_models_package + module
            return get_class(module, klass)

        # Class alone, e.g. "Toaster". Trying to import from e.g.
        # yourlib.toaster:Toaster
        module = "{models_package}.{model}".format(
            models_package=root_models_package,
            model=self.model_name.lower())
        klass = self.model_name

        return get_class(module, klass)

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

        for name, value in fields.items():
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
                            fields[name][i] = self.get_relationship(nested_value)

    def get_relationship(self, name):
        """Get a relationship and its attribute if necessary."""

        # This function is needed so that this fixture can require other
        # fixtures. If a fixture requires another fixture, it
        # necessarily means that it needs to include other relationships
        # as well.
        get_fixture = functools.partial(self.fixture_manager.get_fixture,
                                        include_relationships=True)

        rel_name = name  # e.g. toaster.color
        attr = None

        # TODO: we support only one level for now
        if "." in name:
            rel_name, attr = name.split(".")

        rel = get_fixture(rel_name)

        if attr:
            return getattr(rel, attr)
        else:
            return rel
