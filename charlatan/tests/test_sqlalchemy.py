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
        self.manager.install_fixture("relationship_alone")

        self.assertEqual(self.session.query(Toaster).count(), 1)
        self.assertEqual(self.session.query(Color).count(), 1)

    def test_getting_from_database(self):
        """Verify that we can get from the database."""
        installed = Toaster(id=1)
        self.session.add(installed)
        self.session.commit()

        toaster = self.manager.install_fixture("from_database")
        self.assertEqual(toaster.id, 1)
