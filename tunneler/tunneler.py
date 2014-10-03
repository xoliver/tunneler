from settings import DEFAULT_USER, TUNNELS


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
        if name not in TUNNELS:
            raise NameError()

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
                    tunnel.server, tunnel.remote_port)
                if tunnel_name == name:
                    tunnel.name = name
                    return tunnel
            except LookupError:
                pass
        raise NameError()

    def get_active_tunnels(self):
        tunnels = []
        for tunnel in self.process_helper.get_active_tunnels():
            try:
                name, data = self._find_tunnel_setting(
                    tunnel.server, tunnel.remote_port)
                tunnels.append(
                    (name, data)
                )
            except LookupError:
                tunnels.append(
                    ('Unknown', {'found': '{}'.format(tunnel)})
                )
        return tunnels

    def start_tunnel(self, name):
        if name in TUNNELS:
            data = TUNNELS[name]

            if self.is_tunnel_active(name):
                return 'Tunnel already active'

            success = self.process_helper.start_tunnel(
                user=data['user'] if 'user' in data else DEFAULT_USER,
                server=data['server'],
                local_port=data['local_port'],
                remote_port=data['remote_port']
            )

            if success:
                return 'Tunnel started in port {}'.format(data['local_port'])
            else:
                return 'Tunnel NOT started'

        else:
            return 'Tunnel settings not found!'

    def stop_tunnel(self, name):
        if name in TUNNELS:
            try:
                tunnel = self.get_tunnel(name)
            except NameError:
                return 'Tunnel not active'

            success = self.process_helper.stop_tunnel(tunnel)
            if success:
                return 'Tunnel stopped'
            else:
                return 'Problem stopping tunnel'

        else:
            return 'Tunnel settings not found!'

    def stop_all_tunnels(self):
        results = ['Stopping all active tunnels']
        for name, tunnel in self.get_active_tunnels():
            # This is not the best approach since we have its pid already
            # but dirty will do right now
            results.append(self.stop_tunnel(name) + ': ' + name)

        return '\n'.join(results)
