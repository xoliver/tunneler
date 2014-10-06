def check_tunnel_exists(f):
    def wrap(obj, name):
        if name not in obj.config.tunnels:
            return 'Tunnel config not found: {}'.format(name)
        else:
            return f(obj, name)
    return wrap


class Tunneler(object):
    def __init__(self, process_helper, config, verbose=False):
        self.process_helper = process_helper
        self.config = config
        self.verbose = verbose

    def _find_tunnel_config(self, server, port):
        for (name, tunnel) in self.config.tunnels.iteritems():
            if tunnel['server'] == server and tunnel['remote_port'] == port:
                return (name, tunnel)
        raise LookupError()

    def get_configured_tunnels(self, filter_active=None):
        keys = self.config.tunnels.keys()
        if filter_active is None:
            return keys
        elif filter_active:
            return [key for key in keys if self.is_tunnel_active(key)]
        else:
            return [key for key in keys if not self.is_tunnel_active(key)]

    @check_tunnel_exists
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
                tunnel_name, config = self._find_tunnel_config(
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
                name, config = self._find_tunnel_config(
                    tunnel.server, tunnel.remote_port)
                tunnels.append(
                    (name, config)
                )
            except LookupError:
                tunnels.append(
                    ('Unknown', {'found': '{}'.format(tunnel)})
                )
        return tunnels

    @check_tunnel_exists
    def start_tunnel(self, name):
        data = self.config.tunnels[name]

        if self.is_tunnel_active(name):
            return 'Tunnel already active'

        user_name = data['user'] if 'user' in data \
            else self.config.common['default_user']

        success = self.process_helper.start_tunnel(
            user=user_name,
            server=data['server'],
            local_port=data['local_port'],
            remote_port=data['remote_port']
        )

        if success:
            return 'Tunnel started in port {}'.format(data['local_port'])
        else:
            return 'Tunnel NOT started'

    @check_tunnel_exists
    def stop_tunnel(self, name):
        try:
            tunnel = self.get_tunnel(name)
        except NameError:
            return 'Tunnel not active'

        success = self.process_helper.stop_tunnel(tunnel)
        if success:
            return 'Tunnel stopped'
        else:
            return 'Problem stopping tunnel'

    def stop_all_tunnels(self):
        results = ['Stopping all active tunnels']
        for name, tunnel in self.get_active_tunnels():
            # This is not the best approach since we have its pid already
            # but dirty will do right now
            results.append(self.stop_tunnel(name) + ': ' + name)

        return '\n'.join(results)
