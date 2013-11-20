from __future__ import absolute_import
import calendar
import datetime

from charlatan import file_format, testing


class TestFileFormat(testing.TestCase):

    def setUp(self):
        self.yaml = file_format.load_file(
            './charlatan/tests/data/special_tags.yaml'
        )

    def test_now_tag(self):
        """Assert !now creates a current datetime"""

        now = datetime.datetime.utcnow()

        reasonable_difference = datetime.timedelta(seconds=2)

        difference = abs(now - self.yaml['current_time'])

        self.assertGreater(reasonable_difference, difference)

    def test_time_offsets(self):
        """Assert that !now +1d gives a day in the future"""

        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        reasonable_difference = datetime.timedelta(seconds=2)

        difference = abs(tomorrow - self.yaml['tomorrow'])

        self.assertGreater(reasonable_difference, difference)

    def test_epoch_now_tag(self):
        """Assert !epoch_now gives integer time"""

        now = calendar.timegm(datetime.datetime.utcnow().utctimetuple())

        reasonable_difference = 2  # seconds

        difference = abs(now - self.yaml['current_epoch_time'])

        self.assertGreater(reasonable_difference, difference)

    def test_rel_tag(self):
        """Assert !rel tag makes the value a relationship token"""

        self.assertIsInstance(
            self.yaml['relationship'], file_format.RelationshipToken
        )
