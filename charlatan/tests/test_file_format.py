from __future__ import absolute_import
from sys import version_info
import datetime

from freezegun import freeze_time
from yaml import add_constructor
from yaml.constructor import SafeConstructor
import pytest
import pytz
import unittest

from charlatan import testing
from charlatan import file_format
from charlatan.utils import datetime_to_epoch_in_ms
from charlatan.utils import datetime_to_epoch_timestamp


def test_non_yaml_file():
    """Verify that we can't open a non-YAML file."""
    with pytest.raises(ValueError):
        file_format.load_file("./charlatan/tests/data/test.json")


@freeze_time("2014-12-31 11:00:00")
class TestFileFormat(testing.TestCase):

    def setUp(self):
        self.current_time = datetime.datetime.utcnow().replace(
            tzinfo=pytz.utc)
        self.yaml = file_format.load_file(
            './charlatan/tests/data/special_tags.yaml'
        )

    def test_now_tag(self):
        """Assert !now creates a current datetime."""
        self.assertEqual(self.current_time, self.yaml['current_time']())

    def test_now_naive_tag(self):
        """Assert !now_naive creates a current naive datetime."""
        assert datetime.datetime.utcnow() == self.yaml['current_naive_time']()

    def test_time_offsets(self):
        """Assert that !now +1d gives a day in the future."""
        tomorrow = self.current_time + datetime.timedelta(days=1)
        self.assertEqual(tomorrow, self.yaml['tomorrow']())

    def test_epoch_now_tag(self):
        """Assert !epoch_now gives integer time."""
        current_epoch_time = datetime_to_epoch_timestamp(self.current_time)
        self.assertEqual(current_epoch_time, self.yaml['current_epoch_time']())

    def test_epoch_now_tag_with_offset(self):
        """Assert !epoch_now accepts an offset."""
        tomorrow_datetime = self.current_time + datetime.timedelta(days=1)
        tomorrow = datetime_to_epoch_timestamp(tomorrow_datetime)

        self.assertEqual(tomorrow, self.yaml['tomorrow_epoch_time']())

    def test_epoch_now_in_ms_tag(self):
        """Assert !epoch_now_in_ms_tag gives integer time."""
        current_epoch_time_in_ms = datetime_to_epoch_in_ms(self.current_time)
        self.assertEqual(current_epoch_time_in_ms,
                         self.yaml['current_epoch_time_in_ms']())

    def test_epoch_now_in_ms_tag_with_offset(self):
        """Assert !epoch_now_in_ms_tag gives integer time."""
        tomorrow_datetime = self.current_time + datetime.timedelta(days=1)
        tomorrow = datetime_to_epoch_in_ms(tomorrow_datetime)
        self.assertEqual(tomorrow, self.yaml['tomorrow_epoch_time_in_ms']())

    def test_rel_tag(self):
        """Assert !rel tag makes the value a relationship token."""
        self.assertIsInstance(
            self.yaml['relationship'], file_format.RelationshipToken)


class TestUnicodeLoad(testing.TestCase):

    def setUp(self):
        # preserve the original constructor for strings
        self.str_constructor = SafeConstructor.yaml_constructors[
            u'tag:yaml.org,2002:str'
        ]
        self.yaml = file_format.load_file(
            './charlatan/tests/data/strings.yaml',
            use_unicode=True,
        )

    def tearDown(self):
        # reset the constructor
        add_constructor(u'tag:yaml.org,2002:str', self.str_constructor)

    @unittest.skipIf(version_info[0] == 3, 'Unicode is undefined in Python 3')
    def test_strings_are_unicode(self):
        """Assert all strings are loaded as unicode."""
        for key, val in self.yaml.items():
            self.assertTrue(isinstance(key, unicode))  # noqa
            self.assertTrue(isinstance(val, unicode))  # noqa


class TestStringLoad(testing.TestCase):

    def setUp(self):
        self.yaml = file_format.load_file(
            './charlatan/tests/data/strings.yaml',
        )

    @unittest.skipIf(version_info[0] == 3, 'Iteration has changed in Python 3')
    def test_strings_are_strings(self):
        """Assert all strings are loaded as strings."""
        for key, val in self.yaml.items():
            self.assertTrue(isinstance(key, str))
            self.assertTrue(isinstance(val, str))

    @unittest.skipIf(version_info[0] == 2, 'Iteration has changed in Python 3')
    def test_strings_are_strings_python3(self):
        """Assert all strings are loaded as strings."""
        for key, val in list(self.yaml.items()):
            self.assertTrue(isinstance(key, str))
            self.assertTrue(isinstance(val, str))
