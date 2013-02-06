import copy
import functools
import importlib

from charlatan.file_format import RelationshipToken


class Fixture(object):
    """Represent a fixture that can be installed."""

    def __init__(self, key, model, fixture_manager, fields=None,
                 post_creation=None, id_=None):
        """Create a Fixture object.

        :param str model: model used to instantiate the fixture
        :param dict fields: args to be provided when instantiating the fixture
        :param fixture_manager: FixtureManager creating the fixture
        :param dict post_creation: assignment to be done after instantiation
        """

        if id_ and fields:
            raise TypeError(
                "Cannot provide both id and fields to create fixture.")

        self.key = key
        self.model = model
        self.fields = fields or {}
        self.fixture_manager = fixture_manager
        self.post_creation = post_creation
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
        if self.post_creation:
            for attr, value in self.post_creation.items():
                setattr(instance, attr, value)

        return instance

    def get_class(self):
        """Return class object for this instance."""

        module = "{models_package}.{model}".format(
            models_package=self.fixture_manager.models_package,
            model=self.model.lower())
        class_string = self.model

        object_module = importlib.import_module(module)
        object_class = getattr(object_module, class_string)

        return object_class

    def _process_relationships(self, fields, remove=False):
        """Create any relationship if needed.

        :param dict fields: fields to be processed
        :param boolean remove: false if relationships should be removed

        For each field that is a relationship or a list of relationships,
        instantiate those relationships and update the fields.

        Does not return anything, modify fields in place.
        """

        # FIXME: no error when trying to do circular relationship
        # FIXME: no error on stange objects

        # This function is needed so that this fixture can require other
        # fixtures. If a fixture requires another fixture, it necessarily means
        # that it needs to include other relationships as well.
        get_relationship = functools.partial(self.fixture_manager.get_fixture,
                                             include_relationships=True)

        for name, value in fields.items():
            # One to one relationship
            if isinstance(value, RelationshipToken):
                if remove:
                    del fields[name]
                else:
                    fields[name] = get_relationship(value)

            # One to many relationship
            elif isinstance(value, (tuple, list)):
                for i, nested_value in enumerate(value):
                    if isinstance(nested_value, RelationshipToken):
                        if remove:
                            del fields[name]
                        else:
                            fields[name][i] = get_relationship(nested_value)
