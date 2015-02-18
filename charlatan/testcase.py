from charlatan.utils import copy_docstring_from
from charlatan import FixturesManager
from charlatan.fixtures_manager import make_list


class FixturesManagerMixin(object):

    """Class from which test cases should inherit to use fixtures.

    .. versionchanged:: 0.3.12
        ``FixturesManagerMixin`` does not install class attributes
        ``fixtures`` anymore.

    .. versionchanged:: 0.3.0
        ``use_fixtures_manager`` method renamed ``init_fixtures.``

    .. versionchanged:: 0.3.0
        Extensive change to the function signatures.

    """

    def init_fixtures(self):
        """Initialize the fixtures.

        This function *must* be called before doing anything else.
        """
        self.fixtures_manager.clean_cache()

    @copy_docstring_from(FixturesManager)
    def install_fixture(self, fixture_key, overrides=None):
        fixture = self.fixtures_manager.install_fixture(fixture_key, overrides)
        setattr(self, fixture_key, fixture)
        return fixture

    @copy_docstring_from(FixturesManager)
    def install_fixtures(self, fixtures):
        installed = []
        for fixture in make_list(fixtures):
            installed.append(
                self.install_fixture(fixture)
            )

        return installed

    @copy_docstring_from(FixturesManager)
    def install_all_fixtures(self):
        return self.install_fixtures(self.fixtures_manager.keys())

    @copy_docstring_from(FixturesManager)
    def get_fixture(self, fixture_key, overrides=None):
        return self.fixtures_manager.get_fixture(fixture_key, overrides)

    @copy_docstring_from(FixturesManager)
    def get_fixtures(self, fixtures):
        return self.fixtures_manager.get_fixtures(fixtures)

    @copy_docstring_from(FixturesManager)
    def uninstall_fixture(self, fixture_key):
        self.fixtures_manager.uninstall_fixture(fixture_key)

    @copy_docstring_from(FixturesManager)
    def uninstall_fixtures(self, fixtures):
        for fixture in make_list(fixtures):
            self.uninstall_fixture(fixture)

    @copy_docstring_from(FixturesManager)
    def uninstall_all_fixtures(self):
        # copy and reverse the list in order to remove objects with
        # relationships first
        installed_fixtures = list(self.fixtures_manager.installed_keys)
        installed_fixtures.reverse()
        return self.uninstall_fixtures(installed_fixtures)
