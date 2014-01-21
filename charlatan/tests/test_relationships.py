from charlatan import testcase, testing, FixturesManager


class TestRelationhips(testing.TestCase, testcase.FixturesManagerMixin):

    def setUp(self):
        self.fixtures_manager = FixturesManager()
        self.fixtures_manager.load(
            './charlatan/tests/data/relationships.yaml')
        self.init_fixtures()

    def test_get_attr_from_rel(self):
        """Verify we can get an attribute from a relationship."""
        fixture = self.get_fixture("toaster_colors")
        self.assertEqual(fixture, ['red'])
