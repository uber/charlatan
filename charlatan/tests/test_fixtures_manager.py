from __future__ import absolute_import

from charlatan import testing, FixturesManager


class TestFixturesManager(testing.TestCase):

    def setUp(self):
        self.fixtures_manager = FixturesManager()
        self.fixtures_manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')

    def test_install_fixture(self):
        """install_fixture should return the fixture"""

        fixture = self.fixtures_manager.install_fixture('simple_dict')

        self.assertEqual(fixture, {
            'field1': 'lolin',
            'field2': 2,
        })
