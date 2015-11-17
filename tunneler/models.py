"""
Data storing entities.
"""
from collections import namedtuple


Configuration = namedtuple('ConfigTuple', ['common', 'tunnels', 'groups'])


class Tunnel(object):

    """
    Class encapsulating tunnel data.
    """

    def __init__(
            self, name='unnamed', process=None, local_port=0, host='somehost',
            remote_port=0, user='somebody', server='somewhere'):
        self.name = name
        self.process = process
        self.local_port = local_port
        self.host = host
        self.remote_port = remote_port
        self.user = user
        self.server = server
