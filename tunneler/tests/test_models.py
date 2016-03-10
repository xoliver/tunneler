from unittest import TestCase

from ..models import Tunnel


class TestModels(TestCase):
    def test_defaults(self):
        tunnel = Tunnel()
        self.assertEquals(tunnel.name, 'unnamed')
        self.assertEquals(tunnel.process, None)
        self.assertEqual(tunnel.local_port, 0)
        self.assertEqual(tunnel.host, 'somehost')
        self.assertEqual(tunnel.remote_port, 0)
        self.assertEqual(tunnel.user, 'somebody')
        self.assertEqual(tunnel.server, 'somewhere')
