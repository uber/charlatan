# flake8: noqa

from charlatan.fixtures_manager import FIXTURES_MANAGER as fixtures_manager
from charlatan.fixtures_manager import FixturesManager
from charlatan.fixtures_manager import FixturesManagerMixin
from charlatan.fixture import Fixture
from charlatan import utils


# Shortcuts
load = fixtures_manager.load
set_hook = fixtures_manager.set_hook
install_all_fixtures = fixtures_manager.install_all_fixtures
