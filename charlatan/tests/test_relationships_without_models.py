from __future__ import absolute_import

from charlatan import testcase, testing, FixturesManager


class TestRelationshipsWithoutModels(testing.TestCase, testcase.FixturesMixin):

    fixtures = ('dict_with_nest', 'simple_dict', 'list_of_relationships',)

    def setUp(self):
        fm = FixturesManager()
        fm.load('./charlatan/tests/data/relationships_without_models.yaml')

        self.use_fixtures_manager(fm)

    def test_dictionaries_nest(self):
        self.assertEqual(self.dict_with_nest['simple_dict'], self.simple_dict)

    def test_relationships_list(self):
        self.assertEqual([self.dict_with_nest, self.simple_dict],
                         self.list_of_relationships)
