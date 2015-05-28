from charlatan import testing
from charlatan import FixturesManager
from charlatan.tests.fixtures.models import Session, Base, engine
from charlatan.tests.fixtures.models import Toaster, Color


class TestSqlalchemyFixtures(testing.TestCase):

    def setUp(self):
        self.session = Session()
        self.manager = FixturesManager(db_session=self.session)
        self.manager.load("./charlatan/tests/data/relationships.yaml")

        Base.metadata.create_all(engine)

    def tearDown(self):
        Base.metadata.drop_all(engine)
        self.session.close()

    def test_double_install(self):
        """Verify that there's no double install."""
        self.manager.install_fixture("model")
        self.manager.install_fixture("color")

        self.assertEqual(self.session.query(Toaster).count(), 1)
        self.assertEqual(self.session.query(Color).count(), 1)

    def test_getting_from_database(self):
        """Verify that we can get from the database."""
        installed = Toaster(id=1)
        self.session.add(installed)
        self.session.commit()

        toaster = self.manager.install_fixture("from_database")
        self.assertEqual(toaster.id, 1)

    def test_installing_collection(self):
        """Verify that a collection of fixtures is in the database."""
        self.manager.install_fixture("model_list")

        self.assertEqual(self.session.query(Toaster).count(), 2)

    def test_inheritance_and_relationship(self):
        """Verify that inheritance works with relationships."""
        model, model_1 = self.manager.install_fixtures(('model', 'model_1'))

        self.assertTrue(isinstance(model.color, Color))
        self.assertTrue(isinstance(model_1.color, Color))

    def test_explicit_foreign_key(self):
        """Verify that we can get a db-computed foreign key explicitely."""
        model = self.manager.install_fixture('model_with_explicit_fk')
        assert model.color_id is not None

    def test_uninstall_deletes_fixtures(self):
        """Verify uninstalling a fixture drops it from the database."""
        self.manager.install_fixture("color")

        # sanity check
        self.assertEqual(self.session.query(Color).count(), 1)

        self.manager.uninstall_fixture("color")

        self.assertEqual(self.session.query(Color).count(), 0)
