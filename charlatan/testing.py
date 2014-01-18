from __future__ import absolute_import
import unittest


class TestCase(unittest.TestCase):

    def __call__(self, result=None):
        """Run a test without having to call super in setUp and tearDown"""

        self._pre_setup()

        unittest.TestCase.__call__(self, result)

        self._post_teardown()

    def _pre_setup(self):
        pass

    def _post_teardown(self):
        pass

    def assertCountEqual(self, *args, **kwargs):
        # Raaa Python 3
        try:
            return unittest.TestCase.assertCountEqual(self, *args, **kwargs)
        except AttributeError:
            return self.assertItemsEqual(*args, **kwargs)
