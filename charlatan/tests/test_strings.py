from __future__ import absolute_import
from sys import version_info

import unittest
from yaml import add_constructor
from yaml.constructor import SafeConstructor

from charlatan import file_format, testing


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
        """Assert all strings are loaded as unicode"""
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
        """Assert all strings are loaded as strings"""
        for key, val in self.yaml.items():
            self.assertTrue(isinstance(key, str))
            self.assertTrue(isinstance(val, str))

    @unittest.skipIf(version_info[0] == 2, 'Iteration has changed in Python 3')
    def test_strings_are_strings_python3(self):
        """Assert all strings are loaded as strings"""
        for key, val in list(self.yaml.items()):
            self.assertTrue(isinstance(key, str))
            self.assertTrue(isinstance(val, str))
