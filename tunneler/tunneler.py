from pprint import pprint
from subprocess import call

from settings import DEFAULT_USER, TUNNELS

START_COMMAND = \
    'ssh -f -N -L{local_port}:localhost:{remote_port} {user}@{server}'


class Tunneler(object):
    def __init__(self, process_helper, verbose=False):
        self.process_helper = process_helper
        self.verbose = verbose

    def set_verbose(self, verbose):
        self.verbose = verbose

    def _find_tunnel_setting(self, server, port):
        for (name, tunnel) in TUNNELS.iteritems():
            if tunnel['server'] == server and tunnel['remote_port'] == port:
                return (name, tunnel)
        raise LookupError()

    def get_configured_tunnels(self, filter_active=None):
        keys = TUNNELS.keys()
        if filter_active is None:
            return keys
        elif filter_active:
            return [key for key in keys if self.is_tunnel_active(key)]
        else:
            return [key for key in keys if not self.is_tunnel_active(key)]

    def is_tunnel_active(self, name):
        try:
            self.get_tunnel(name)
        except NameError:
            return False
        else:
            return True

    def get_tunnel(self, name):
        for tunnel in self.process_helper.get_active_tunnels():
            try:
                tunnel_name, setting = self._find_tunnel_setting(
                    tunnel.server, tunnel.to_port)
                if tunnel_name == name:
                    return tunnel
            except LookupError:
                pass
        raise NameError()

    def list_tunnels(self):
        tunnels = []
        for tunnel in self.process_helper.get_active_tunnels():
            try:
                name, data = self._find_tunnel_setting(
                    tunnel.server, tunnel.to_port)
                tunnels.append('{} : {}'.format(name, data))
            except LookupError:
                tunnels.append('Unknown: {}'.format(tunnel))
        return tunnels

    def start_tunnel(self, name):
        if name in TUNNELS:
            data = TUNNELS[name]

            if self.is_tunnel_active(name):
                return 'Tunnel already active'

            command = START_COMMAND.format(
                local_port=data['local_port'],
                remote_port=data['remote_port'],
                user=data['user'] if 'user' in data else DEFAULT_USER,
                server=data['server']
            )
            if call(command.split()) == 0:
                return 'Tunnel started in port {}'.format(data['local_port'])
            else:
                return 'Tunnel NOT started'

        else:
            return 'Tunnel settings not found!'

    def stop_tunnel(self, name):
        raise NotImplementedError()
