import os.path
from unittest import TestCase

from ..config import *


def _config_path(name):
    here = os.path.dirname(__file__)
    path = os.path.join(here, 'data', name)
    return path


class TestConfig(TestCase):
    def test_happy_path(self):
        config = TunnelerConfigParser()
        config.read([_config_path('valid_config.ini')])
        self.assertEqual([], config.validate())

    def test_validate_same_name(self):
        config = TunnelerConfigParser()
        config.read([_config_path('same_name.ini')])
        self.assertEqual([
            'Found one group and a tunnel called the same: a',
        ], config.validate())

    def test_validate_missing_tunnel(self):
        config = TunnelerConfigParser()
        config.read([_config_path('missing_tunnel.ini')])
        self.assertEqual([
            '[group_a] tunnel b undefined',
        ], config.validate())

    def test_get_config(self):
        config = TunnelerConfigParser()
        config.read([_config_path('valid_config.ini')])
        c = config.get_config()
        self.assertEqual(c.common, {
            'default_user': 'mickey',
        })
        self.assertEqual(c.groups['group_ab'], [('a', None), ('b', 99)])
        self.assertEqual(c.tunnels['a'], {
            'local_port': 100,
            'name': 'this is tunnel a',
            'remote_port': 101,
            'server': 'not.a.server'
        })
