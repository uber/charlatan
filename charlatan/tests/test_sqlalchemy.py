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

    def test_double_install(self):
        """Verify that there's no double install."""
        self.manager.install_fixture("model")
        self.manager.install_fixture("relationship_alone")

        self.assertEqual(self.session.query(Toaster).count(), 1)
        self.assertEqual(self.session.query(Color).count(), 1)
