from unittest import TestCase

from mock import Mock

from ..process import ProcessHelper
from ..tunneler import Tunneler


class TunnelerTestCase(TestCase):
    def setUp(self):
        self.process_helper = Mock(ProcessHelper)
        self.tunneler = Tunneler(self.process_helper, {})

    def test_list_tunnels(self):
        pass
