from unittest import TestCase

from ..utils import (
    ok,
    fail,
)


class UtilsTestCase(TestCase):
    def test_ok(self):
        self.assertEqual(
            u"[ \x1b[32mOK\x1b[39m ] This is good",
            ok("This is good")
        )

    def test_fail(self):
        self.assertEqual(
            u"[ \x1b[31mFAIL\x1b[39m ] This is not good",
            fail("This is not good")
        )
