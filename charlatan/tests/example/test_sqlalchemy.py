from charlatan import testing
from charlatan import FixturesManager
from charlatan.tests.fixtures.models import Session, Base, engine
from charlatan.tests.fixtures.models import Toaster

session = Session()
manager = FixturesManager(db_session=session)
manager.load("./charlatan/tests/example/data/sqlalchemy.yaml")


class TestSqlalchemyFixtures(testing.TestCase):

    def setUp(self):
        self.manager = manager

        # There's a lot of different patterns to setup and teardown the
        # database. This is the simplest possibility.
        Base.metadata.create_all(engine)

    def tearDown(self):
        Base.metadata.drop_all(engine)
        session.close()

    def test_double_install(self):
        """Verify that there's no double install."""
        self.manager.install_fixture('toaster')

        toaster = session.query(Toaster).one()
        assert toaster.color.name == 'red'
