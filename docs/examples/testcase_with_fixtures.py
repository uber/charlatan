import unittest

from toaster.models import db_session

import charlatan

charlatan.load("./tests/data/fixtures.yaml",
               models_package="toaster.models",
               db_session=db_session)


class TestToaster(unittest.TestCase, charlatan.FixturesManagerMixin):

    def setUp(self):
        self.clean_fixtures_cache()
        self.install_fixtures(("toaster", "user"))

    def test_toaster(self):
        """Verify that toaster can toast."""

        self.toaster.toast()

    def test_user_with_toaster(self):
        """Verify that user can use toaster."""

        self.toast1 = self.get_fixture("toast1")
        self.user.use(self.toaster, self.toast1)

    def test_user_with_toaster_and_toasts(self):
        """Verify that user can use toaster and toasts."""

        self.toast1 = self.get_fixture("toast1")
        self.install_fixture("toast2")

        self.user.use(self.toaster, self.toast1, self.toast2)
