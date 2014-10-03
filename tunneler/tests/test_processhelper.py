from unittest import TestCase

from ..process import ProcessHelper


class ProcessHelperTestCase(TestCase):
    def setUp(self):
        self.process_helper = ProcessHelper()

    def test_process_line_to_tunnel_ok(self):
        line = '-N -L2323:localhost:4545 hiyou@aserver.aplace.net'
        expected = (2323, 4545, 'hiyou', 'aserver.aplace.net')

        self.assertEqual(
            self.process_helper.extract_tunnel_info(line),
            expected
        )

    def test_process_line_to_tunnel_not_ok(self):
        line = '-N -L3434:localhost:1212 server.aplace.net'

        with self.assertRaises(AttributeError):
            self.process_helper.extract_tunnel_info(line)
