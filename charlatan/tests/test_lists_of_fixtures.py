from __future__ import absolute_import

from charlatan import testing
from charlatan import FixturesManager


class TestListOfFixtures(testing.TestCase):

    def setUp(self):
        self.fm = FixturesManager()
        self.fm.load('./charlatan/tests/data/lists.yaml')

    def test_get_list_by_name(self):
        """Verify that lists of fixtures returns lists"""

        fixtures = self.fm.install_fixture('fixture_list')
        self.assertIsInstance(fixtures, list)

    def test_one_to_many_relationship(self):
        """Verify that relations to lists of fixtures work"""

        fixture = self.fm.install_fixture('related_fixture')
        self.assertEqual(
            fixture['elements'],
            self.fm.install_fixture('fixture_list')
        )

    def test_override(self):
        """Verify that we can override attributes on a list of fixtures."""
        fixtures = self.fm.install_fixture(
            'fixture_list',
            attrs={"field1": 12})

        for fixture in fixtures:
            self.assertEqual(fixture["field1"], 12)
