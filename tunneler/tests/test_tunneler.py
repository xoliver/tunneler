from unittest import TestCase

from mock import Mock

from ..models import Configuration, Tunnel
from ..process import ProcessHelper
from ..tunneler import check_tunnel_exists, Tunneler


class CheckTunnelExistsTestCase(TestCase):
    def test_tunnel_exists(self):
        func = Mock()
        name = 'atunnel'
        tunneler = Mock()
        tunneler.config.tunnels = {'atunnel': 'yes indeed'}

        decorated_func = check_tunnel_exists(func)
        decorated_func(tunneler, name)

        func.assert_called_once_with(tunneler, name)

    def test_tunnel_does_not_exist(self):
        func = Mock()
        name = 'atunnel'
        tunneler = Mock()
        tunneler.config.tunnels = {}

        decorated_func = check_tunnel_exists(func)
        result = decorated_func(tunneler, name)

        self.assertTrue(type(result) == str)
        self.assertEqual(func.call_count, 0)


class TunnelerTestCase(TestCase):
    def setUp(self):
        self.process_helper = Mock(ProcessHelper)
        self.tunneler = Tunneler(self.process_helper, Configuration({}, {}))

    def test_find_tunnel_config_if_found(self):
        name = 'testserver'
        fullname = 'fullserver.name'
        port = 42

        tunnel_data = {
            'server': fullname,
            'remote_port': port,
        }
        self.tunneler.config = Configuration(
            common={},
            tunnels={name: tunnel_data},
        )

        result = self.tunneler._find_tunnel_config(fullname, port)
        self.assertEqual(result, (name, tunnel_data))

    def test_find_tunnel_config_if_not_found(self):
        with self.assertRaises(LookupError):
            self.tunneler._find_tunnel_config('someserver.somewhere', 69)

    def test_get_configured_tunnels(self):
        tunnel_data = {'a': None, 'b': None}
        self.tunneler.config = Configuration(
            common={},
            tunnels=tunnel_data,
        )

        configured_tunnels = self.tunneler.get_configured_tunnels()
        self.assertEqual(configured_tunnels, tunnel_data.keys())

    def test_get_configured_tunnels_filtering_active(self):
        tunnel_data = {'a': None, 'b': None}
        self.tunneler.config = Configuration(
            common={},
            tunnels=tunnel_data,
        )

        configured_tunnels = self.tunneler.get_configured_tunnels()
        self.assertEqual(configured_tunnels, tunnel_data.keys())

    def test_get_configured_tunnels_with_filtering(self):
        tunnel_data = {'a': None, 'b': None}
        self.tunneler.config = Configuration(
            common={},
            tunnels=tunnel_data,
        )

        # Filtering active
        self.tunneler.is_tunnel_active = Mock(side_effect=[True, False])
        configured_tunnels = self.tunneler.get_configured_tunnels(
            filter_active=True)
        self.assertEqual(configured_tunnels, ['a'])
        self.assertEqual(self.tunneler.is_tunnel_active.call_count, 2)

        # Filtering inactive
        self.tunneler.is_tunnel_active = Mock(side_effect=[True, False])
        configured_tunnels = self.tunneler.get_configured_tunnels(
            filter_active=False)
        self.assertEqual(configured_tunnels, ['b'])
        self.assertEqual(self.tunneler.is_tunnel_active.call_count, 2)

    def test_is_tunnel_active(self):
        tunnel_data = {'server': None}
        self.tunneler.config = Configuration(
            common={},
            tunnels=tunnel_data,
        )
        # TODO redo this test - it's not clear
        self.tunneler.get_tunnel = Mock(side_effect=[Tunnel(), NameError])

        self.assertTrue(self.tunneler.is_tunnel_active('server'))
        self.assertFalse(self.tunneler.is_tunnel_active('server'))
