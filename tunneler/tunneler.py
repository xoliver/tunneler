"""
Code to operate with tunnels and helpful functions.
"""


class ConfigNotFound(LookupError):
    """
    Indicate that configuration for whatever does not exist.
    """
    pass


def check_name_exists(func):
    """
    Decorator, ensure name passed to function is configured as group or tunnel.

    Raise ConfigNotFound if name not identified.
    """
    def wrap(obj, name):
        "Das wrapper."
        if name not in obj.config.tunnels and name not in obj.config.groups:
            raise ConfigNotFound()
        else:
            return func(obj, name)
    return wrap


class Tunneler(object):
    """
    Class to handle tunnel operations at a higher level.
    """

    def __init__(self, process_helper, config, verbose=False):
        self.process_helper = process_helper
        self.config = config
        self.verbose = verbose

    def identify_tunnel(self, server, port):
        """
        Retrieve tunnels matching parameters.

        Return list of tunnel names.
        """
        names = []
        for (name, tunnel) in self.config.tunnels.iteritems():
            if tunnel['server'] == server and tunnel['remote_port'] == port:
                names.append(name)
        if names:
            return names
        raise LookupError()

    def get_configured_tunnels(self, filter_active=None):
        """
        Retrieve tunnels that are active, inactive or both.

        Return list of tunnel names.
        """
        keys = self.config.tunnels.keys()
        if filter_active is None:
            return keys
        elif filter_active:
            return [key for key in keys if self.is_tunnel_active(key)]
        else:
            return [key for key in keys if not self.is_tunnel_active(key)]

    @check_name_exists
    def is_tunnel_active(self, name):
        """
        Check whether the specified tunnel is active.

        Return True/False
        """
        try:
            self.get_active_tunnel(name)
        except NameError:
            return False
        else:
            return True

    def get_active_tunnel(self, name):
        """
        Retrieve information for the specified tunnel if it is active.

        Return Tunnel if named tunnel found.
        NameError if it is not active.
        """
        for tunnel in self.process_helper.get_active_tunnels():
            try:
                tunnel_names = self.identify_tunnel(
                    tunnel.server, tunnel.remote_port)
                for tunnel_name in tunnel_names:
                    if tunnel_name == name:
                        tunnel.name = name
                        return tunnel
            except LookupError:
                pass
        raise NameError()

    def get_active_tunnels(self):
        """
        Retrieve information on running tunnels.

        Return list of Tunnel.
        """
        tunnels = []
        for tunnel in self.process_helper.get_active_tunnels():
            try:
                names = self.identify_tunnel(
                    tunnel.server, tunnel.remote_port)
                for name in names:
                    tunnels.append(
                        (name, self.config.tunnels[name])
                    )
            except LookupError:
                tunnels.append(
                    ('Unknown', {'found': '{}'.format(tunnel)})
                )
        return tunnels

    @check_name_exists
    def start(self, name):
        """
        Launch specified tunnel group or individual tunnel.

        Return list of tuples (tunnel name, started port OR status/error).
        """
        if name in self.config.groups:
            return self._start_group(name)
        else:
            return self._start_tunnel(name)

    def _start_group(self, name):
        """
        Launch specified group of tunnels.

        Yield tuples (tunnel name, started port OR status/error).
        """
        for (tunnel_name, tunnel_port) in self.config.groups[name]:
            if tunnel_port:
                print 'Ignoring tunnel port for {} in group {}'.format(
                    tunnel_name, name)
            yield self._start_tunnel(tunnel_name)[0]

    def _start_tunnel(self, name):
        """
        Launch specified tunnel.

        Return list with tuple (tunnel name, started port OR status/error).
        """
        data = self.config.tunnels[name]

        try:
            self.get_active_tunnel(name)
            return [(name, 'already running')]
        except NameError:
            pass

        user_name = data['user'] if 'user' in data \
            else self.config.common['default_user']

        success = self.process_helper.start_tunnel(
            user=user_name,
            server=data['server'],
            local_port=data['local_port'],
            remote_port=data['remote_port']
        )

        if success:
            return [(name, data['local_port'])]
        else:
            return [(name, None)]

    @check_name_exists
    def stop(self, name):
        """
        Stop specified tunnel group or individual tunnel.

        Return list with tuples (tunnel name, operation success).
        """
        if name in self.config.groups:
            return self._stop_group(name)
        else:
            return self._stop_tunnel(name)

    def _stop_group(self, name):
        """
        Stop specified tunnel group.

        Yield tuples (tunnel name, operation success).
        """
        for (tunnel_name, _) in self.config.groups[name]:
            yield self._stop_tunnel(tunnel_name)[0]

    def _stop_tunnel(self, name):
        """
        Stop specified tunnel.

        Return list with tuple (tunnel name, operation success).
        """
        try:
            tunnel = self.get_active_tunnel(name)
        except NameError:
            return [(name, False)]

        return [(name, self.process_helper.stop_tunnel(tunnel))]

    def stop_all_tunnels(self):
        """
        Stop all the detected tunnels (including those not identified!).

        Return list of tuples (tunnel name, operation success).
        """
        results = []
        for name, _ in self.get_active_tunnels():
            if name == 'Unknown':
                continue
            # This is not the best approach since we have its pid already
            # but dirty will do right now
            result = self._stop_tunnel(name)
            results.append((name, result,))

        return results
