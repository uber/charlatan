from __future__ import absolute_import

from charlatan import testing
from charlatan import FixturesManager


class TestListOfFixtures(testing.TestCase):

    def setUp(self):
        self.fm = FixturesManager()
        self.fm.load('./charlatan/tests/data/lists.yaml')

    def test_get_list_by_name(self):
        """A list of fixtures can be retrieved by name"""

        fixtures = self.fm.install_fixture('fixture_list')

        self.assertIsInstance(fixtures, list)

    def test_one_to_many_relationship(self):
        fixture = self.fm.install_fixture('related_fixture')

        self.assertEqual(
            fixture['elements'],
            self.fm.install_fixture('fixture_list')
        )

    def test_lists_still_work(self):
        """Gut check to make sure normal lists can still be made"""

        self.fm.install_fixture('list_fixture')
