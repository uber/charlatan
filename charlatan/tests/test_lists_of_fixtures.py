from __future__ import absolute_import

from charlatan import testing
from charlatan import FixturesManager


class TestListOfFixtures(testing.TestCase):

    def setUp(self):
        self.fm = FixturesManager()
        self.fm.load('./charlatan/tests/data/lists.yaml')

    def test_get_list_by_name(self):
        """Assert lists of fixtures returns lists"""

        fixtures = self.fm.install_fixture('fixture_list')

        self.assertIsInstance(fixtures, list)

    def test_one_to_many_relationship(self):
        """Assert relations to lists of fixtures work"""

        fixture = self.fm.install_fixture('related_fixture')

        self.assertEqual(
            fixture['elements'],
            self.fm.install_fixture('fixture_list')
        )

    def test_lists_still_work(self):
        """Assert that installing a list as a fixture does not error"""

        self.fm.install_fixture('list_fixture')
