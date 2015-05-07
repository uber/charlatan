from __future__ import absolute_import

from charlatan import testcase, testing, FixturesManager


class TestRelationshipsWithoutModels(testing.TestCase,
                                     testcase.FixturesManagerMixin):

    def setUp(self):
        self.fixtures_manager = FixturesManager()
        self.fixtures_manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')
        self.install_fixtures([
            'dict_with_nest', 'simple_dict', 'list_of_relationships'])
        self.init_fixtures()

    def test_dictionaries_nest(self):
        self.assertEqual(self.dict_with_nest['simple_dict'], self.simple_dict)

    def test_relationships_list(self):
        self.assertEqual([self.dict_with_nest, self.simple_dict],
                         self.list_of_relationships)

    def test_nested_list_of_relationships(self):
        nested_list_of_relationships = self.install_fixture(
            'nested_list_of_relationships')

        self.assertEqual(nested_list_of_relationships, {
            'dicts': [
                [self.dict_with_nest],
                [self.simple_dict],
            ]
        })

    def test_relationships_dict_attribute(self):
        parent = self.install_fixture('parent_dict.object1')
        child = self.install_fixture('child_dict.object1')

        self.assertEquals(child['field1'], parent['field1'])
