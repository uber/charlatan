from __future__ import absolute_import

from charlatan import testcase
from charlatan import testing
from charlatan import FixturesManager


fixtures_manager = FixturesManager()
fixtures_manager.load(
    './charlatan/tests/data/relationships_without_models.yaml')


class TestTestCase(testing.TestCase, testcase.FixturesManagerMixin):

    fixtures = (
        'simple_dict',
        'dict_with_nest',)

    def _pre_setup(self):
        self.fixtures_manager = fixtures_manager
        self.init_fixtures()

    def _post_teardown(self):
        self.uninstall_all_fixtures()

    def test_init_fixtures(self):
        """init_fixtures should install 2 fixtures."""
        self.uninstall_all_fixtures()

        self.init_fixtures()
        self.assertEqual(len(self.fixtures_manager.installed_keys), 2)

    def test_install_fixture(self):
        """install_fixture should return the installed fixture."""
        self.uninstall_all_fixtures()

        simple_dict = self.install_fixture('simple_dict')
        self.assertEqual(simple_dict['field1'], 'lolin')
        self.assertEqual(simple_dict['field2'], 2)

    def test_install_fixtures(self):
        """install_fixtures should return the list of installed fixtures."""
        self.uninstall_all_fixtures()

        fixtures = self.install_fixtures(('simple_dict', 'dict_with_nest'))
        self.assertEqual(len(fixtures), 2)

    def test_install_all_fixtures(self):
        """Verify it installs all fixtures of the yaml file."""
        self.uninstall_all_fixtures()

        fixtures = self.install_all_fixtures()
        self.assertEqual(len(fixtures), 3)

    def test_uninstall_fixture(self):
        """uninstall_fixture should return the uninstalled fixture."""
        simple_dict = self.uninstall_fixture('simple_dict')
        self.assertEqual(simple_dict['field1'], 'lolin')
        self.assertEqual(simple_dict['field2'], 2)

        dict_with_nest = self.uninstall_fixture('dict_with_nest')
        self.assertEqual(dict_with_nest['field1'], 'asdlkf')
        self.assertEqual(dict_with_nest['field2'], 4)

        fixtures = self.uninstall_all_fixtures()
        self.assertEqual(len(fixtures), 0)

    def test_uninstall_fixtures(self):
        """Verify it returns the list of uninstalled fixtures."""
        fixtures = self.uninstall_fixtures(('simple_dict', 'dict_with_nest'))
        self.assertEqual(len(fixtures), 2)

        fixtures = self.uninstall_fixtures(('simple_dict', 'dict_with_nest'))
        self.assertEqual(len(fixtures), 0)

    def test_uninstall_all_fixtures(self):
        """uninstall_all_fixtures should uninstall all the installed fixtures.

        The _pre_setup method install the 2 fixtures defined in self.fixtures:
        'simple_dict' and 'dict_with_nest'.
        """
        fixtures = self.uninstall_all_fixtures()
        self.assertEqual(len(fixtures), 2)

        fixtures = self.uninstall_all_fixtures()
        self.assertEqual(len(fixtures), 0)

    def test_get_fixture(self):
        """get_fixture should return the fixture."""
        simple_dict = self.get_fixture('simple_dict')
        self.assertEqual(simple_dict['field1'], 'lolin')
        self.assertEqual(simple_dict['field2'], 2)

        dict_with_nest = self.get_fixture('dict_with_nest')
        self.assertEqual(dict_with_nest['field1'], 'asdlkf')
        self.assertEqual(dict_with_nest['field2'], 4)

    def test_get_fixtures(self):
        """get_fixtures should return the list of fixtures."""
        fixtures = self.get_fixtures(('simple_dict', 'dict_with_nest'))
        self.assertEqual(len(fixtures), 2)

        simple_dict = fixtures[0]
        self.assertEqual(simple_dict['field1'], 'lolin')
        self.assertEqual(simple_dict['field2'], 2)

        dict_with_nest = fixtures[1]
        self.assertEqual(dict_with_nest['field1'], 'asdlkf')
        self.assertEqual(dict_with_nest['field2'], 4)
