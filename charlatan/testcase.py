class FixturesMixin(object):

    """Class from which test cases should inherit to use fixtures."""

    def use_fixtures_manager(self, fixtures_manager):
        """Set the fixture manager.

        This function *must* be called before doing anything else.
        """

        self.__fixtures_manager = fixtures_manager
        self.__fixtures_manager.clean_cache()

        if hasattr(self, "fixtures"):
            self.install_fixtures(self.fixtures)

    def install_fixtures(self, fixtures, do_not_save=False):
        """Install required fixtures.

        :param fixtures: fixtures key
        :type fixtures: list of strings

        If :data:`fixtures` is not provided, the method will look for a class
        property named :attr:`fixtures`.
        """

        if fixtures:
            # Be forgiving
            if not isinstance(fixtures, (list, tuple)):
                fixtures = (fixtures, )
            fixtures_to_install = fixtures

        else:
            fixtures_to_install = self.fixtures

        installed = self.__fixtures_manager.install_fixtures(
            fixtures_to_install,
            do_not_save=do_not_save)

        # Adding fixtures to the class
        for fixture_name, fixture in zip(fixtures_to_install, installed):
            setattr(self, fixture_name, fixture)

        # Return list of fixture instances
        return installed

    def install_fixture(self, fixture_name):
        """Install a fixture and return it."""
        return self.install_fixtures(fixture_name)[0]

    def create_all_fixtures(self):
        """Create all available fixtures but do not save them."""

        # Adding fixtures to the class
        for f in self.__fixtures_manager.install_all(do_not_save=True):
            setattr(self, f[0], f[1])

    def get_fixture(self, fixture_name):
        """Return a fixture instance (but do not save it).

        :param str fixture_name: fixture key
        """
        return self.__fixtures_manager.get_fixture(fixture_name)
