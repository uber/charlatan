from __future__ import absolute_import
import datetime

from freezegun import freeze_time

from charlatan import file_format, testing
from charlatan.utils import datetime_to_epoch_timestamp


@freeze_time("2014-12-31 11:00:00")
class TestFileFormat(testing.TestCase):

    def setUp(self):
        self.current_time = datetime.datetime.utcnow()
        self.yaml = file_format.load_file(
            './charlatan/tests/data/special_tags.yaml'
        )

    def test_now_tag(self):
        """Assert !now creates a current datetime"""
        self.assertEqual(self.current_time, self.yaml['current_time']())

    def test_time_offsets(self):
        """Assert that !now +1d gives a day in the future"""
        tomorrow = self.current_time + datetime.timedelta(days=1)
        self.assertEqual(tomorrow, self.yaml['tomorrow']())

    def test_epoch_now_tag(self):
        """Assert !epoch_now gives integer time"""
        current_epoch_time = datetime_to_epoch_timestamp(self.current_time)
        self.assertEqual(current_epoch_time, self.yaml['current_epoch_time']())

    def test_epoch_now_tag_with_offset(self):
        """Assert !epoch_now accepts an offset"""
        tomorrow_datetime = self.current_time + datetime.timedelta(days=1)
        tomorrow = datetime_to_epoch_timestamp(tomorrow_datetime)

        self.assertEqual(tomorrow, self.yaml['tomorrow_epoch_time']())

    def test_rel_tag(self):
        """Assert !rel tag makes the value a relationship token"""
        self.assertIsInstance(
            self.yaml['relationship'], file_format.RelationshipToken
        )
