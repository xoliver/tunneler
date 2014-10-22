from unittest import TestCase

from mock import Mock

from ..models import Configuration, Tunnel
from ..process import ProcessHelper
from ..tunneler import (
    AlreadyThereError,
    ConfigNotFound,
    Tunneler,
    check_tunnel_exists,
)


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

        with self.assertRaises(ConfigNotFound):
            _ = decorated_func(tunneler, name)  # NOQA

        self.assertEqual(func.call_count, 0)


class TunnelerTestCase(TestCase):
    def setUp(self):
        self.process_helper = Mock(ProcessHelper)
        self.tunnel_name = 'test_tunnel'
        self.tunnel = Tunnel(
            name=self.tunnel_name,
            user='somebody',
            server='somewhere',
            local_port=2323,
            remote_port=3434,
        )
        tunnel_config = {
            self.tunnel_name: {
                'user': self.tunnel.user,
                'server': self.tunnel.server,
                'local_port': self.tunnel.local_port,
                'remote_port': self.tunnel.remote_port,
            }
        }

        self.config = Configuration(
            common={},
            tunnels=tunnel_config,
            groups={})
        self.empty_config = Configuration({}, {}, {})

        self.tunneler = Tunneler(self.process_helper, self.empty_config)

    def test_find_tunnel_name(self):
        name = 'testserver'
        fullname = 'fullserver.name'
        port = 42

        tunnel_config = {
            'server': fullname,
            'remote_port': port,
        }
        self.tunneler.config = Configuration(
            common={},
            tunnels={name: tunnel_config},
            groups={},
        )

        result = self.tunneler.find_tunnel_name(fullname, port)
        self.assertEqual(result, name)

    def test_find_tunnel_name_when_not_found(self):
        with self.assertRaises(LookupError):
            self.tunneler.find_tunnel_name('someserver.somewhere', 69)

    def test_get_configured_tunnels(self):
        tunnel_config = {'a': None, 'b': None}
        self.tunneler.config = Configuration(
            common={},
            tunnels=tunnel_config,
            groups={},
        )

        configured_tunnels = self.tunneler.get_configured_tunnels()
        self.assertEqual(configured_tunnels, tunnel_config.keys())

    def test_get_configured_tunnels_with_filtering(self):
        tunnel_config = {'a': None, 'b': None}
        self.tunneler.config = Configuration(
            common={},
            tunnels=tunnel_config,
            groups={},
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

    def test_get_active_tunnel_when_active_and_in_config(self):
        self.process_helper.get_active_tunnels = Mock(
            return_value=[self.tunnel])
        self.tunneler.config = self.config
        found_tunnel = self.tunneler.get_active_tunnel(self.tunnel_name)
        self.assertEqual(self.tunnel, found_tunnel)

    def test_get_active_tunnel_when_active_and_not_in_config(self):
        self.process_helper.get_active_tunnels = Mock(
            return_value=[self.tunnel])
        self.tunneler.config = self.empty_config
        with self.assertRaises(NameError):
            self.tunneler.get_active_tunnel(self.tunnel_name)

    def test_get_active_tunnel_when_not_active_and_in_config(self):
        self.process_helper.get_active_tunnels = Mock(return_value=[])
        self.tunneler.config = self.config
        with self.assertRaises(NameError):
            self.tunneler.get_active_tunnel(self.tunnel_name)

    def test_get_active_tunnel_when_not_active_and_not_in_config(self):
        self.process_helper.get_active_tunnels = Mock(return_value=[])
        self.tunneler.config = self.empty_config
        with self.assertRaises(NameError):
            self.tunneler.get_active_tunnel('idonotexist')

    def test_is_tunnel_active(self):
        tunnel_config = {'server1': None, 'server2': None}
        self.tunneler.config = Configuration(
            common={},
            tunnels=tunnel_config,
            groups={},
        )
        self.tunneler.get_active_tunnel = Mock(
            side_effect=[Tunnel(), NameError])
        self.assertTrue(self.tunneler.is_tunnel_active('server1'))
        self.assertFalse(self.tunneler.is_tunnel_active('server2'))

    def test_get_active_tunnels(self):
        self.tunneler.config = self.config
        self.process_helper.get_active_tunnels = Mock(
            return_value=[self.tunnel])

        result = self.tunneler.get_active_tunnels()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], self.tunnel_name)

    def test_get_active_tunnels_handle_unknown(self):
        unknown_tunnel = Tunnel(name='iamnotinconfig')
        self.process_helper.get_active_tunnels = Mock(
            return_value=[unknown_tunnel])

        result = self.tunneler.get_active_tunnels()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'Unknown')

    def test_start_tunnel(self):
        self.tunneler.config = self.config
        self.tunneler.get_active_tunnel = Mock(side_effect=NameError)
        self.process_helper.start_tunnel = Mock(return_value=True)

        result = self.tunneler.start_tunnel(self.tunnel_name)

        self.assertEqual(self.process_helper.start_tunnel.call_count, 1)
        self.assertEqual(result, self.tunnel.local_port)

    def test_start_tunnel_if_command_fails(self):
        self.tunneler.config = self.config
        self.tunneler.get_active_tunnel = Mock(side_effect=NameError)
        self.process_helper.start_tunnel = Mock(return_value=False)

        result = self.tunneler.start_tunnel(self.tunnel_name)
        self.assertIsNone(result)

    def test_start_tunnel_if_already_active(self):
        self.tunneler.config = self.config
        self.tunneler.get_active_tunnel = Mock(return_value=object())

        with self.assertRaises(AlreadyThereError):
            self.tunneler.start_tunnel(self.tunnel_name)

    def test_stop_tunnel(self):
        self.tunneler.config = self.config
        self.tunneler.get_active_tunnel = Mock(return_value=object())
        self.process_helper.stop_tunnel = Mock(return_value=True)

        result = self.tunneler.stop_tunnel(self.tunnel_name)

        self.assertEqual(self.process_helper.stop_tunnel.call_count, 1)
        self.assertTrue(result)

    def test_stop_tunnel_if_command_fails(self):
        self.tunneler.config = self.config
        self.tunneler.get_active_tunnel = Mock(return_value=object())
        self.process_helper.stop_tunnel = Mock(return_value=False)

        result = self.tunneler.stop_tunnel(self.tunnel_name)

        self.assertFalse(result)

    def test_stop_tunnel_if_already_inactive(self):
        self.tunneler.config = self.config
        self.tunneler.get_active_tunnel = Mock(side_effect=NameError)

        with self.assertRaises(AlreadyThereError):
            self.tunneler.stop_tunnel(self.tunnel_name)

    def test_stop_all_tunnels(self):
        active_tunnels = [(self.tunnel_name, self.tunnel)]
        self.tunneler.get_active_tunnels = Mock(return_value=active_tunnels)
        self.tunneler.stop_tunnel = Mock(return_value='True')

        result = self.tunneler.stop_all_tunnels()

        self.assertEqual(len(result), len(active_tunnels))
        self.assertEqual(
            self.tunneler.stop_tunnel.call_count, len(active_tunnels))
