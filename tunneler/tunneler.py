from pprint import pprint
from subprocess import call

from settings import TUNNELS

START_COMMAND = \
    'ssh -f -N -L{local_port}:localhost:{remote_port} {user}@{server}'


class Tunneler(object):
    def __init__(self, process_helper, config=None):
        self.process_helper = process_helper
        # self.load_config(config)

    def execute(self, command, parameters):
        if command == 'list':
            pprint(self.list_tunnels())
        elif command == 'start':
            print self.start_tunnel(parameters[0])
        else:
            raise NameError()

    def _find_tunnel_setting(self, server, port):
        for (name, tunnel) in TUNNELS.iteritems():
            if tunnel['server'] == server and tunnel['remote_port'] == port:
                return (name, tunnel)
        raise LookupError

    def _is_tunnel_active(self, name):
        for tunnel_description in self.list_tunnels():
            if name in tunnel_description:
                return True
        return False

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

            if self._is_tunnel_active(name):
                return 'Tunnel already active'

            command = START_COMMAND.format(
                local_port=data['local_port'],
                remote_port=data['remote_port'],
                user=data['user'],
                server=data['server']
            )
            if call(command.split()) == 0:
                return 'Tunnel started'
            else:
                return 'Tunnel NOT started'

        else:
            return 'Tunnel settings not found!'
