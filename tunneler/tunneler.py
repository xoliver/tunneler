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

    def __init__(self, process_helper, config, verbose=False, ssh_debug_level=0):
        self.process_helper = process_helper
        self.config = config
        self.verbose = verbose
        self.ssh_debug_level = ssh_debug_level

    def identify_tunnel(self, server, remote_port):
        """
        Retrieve tunnels matching parameters.

        Return list of tunnel names.
        """
        names = []
        for (name, tunnel) in self.config.tunnels.iteritems():
            if tunnel['server'] == server \
                    and tunnel['remote_port'] == remote_port:
                names.append(name)
        if names:
            return names
        raise LookupError()

    def identify_group(self, tunnels):
        """
        Retrieve tunnel group containing all the specified named tunnels.

        Return list of tunnel groups.
        """
        name_set = set(tunnels)
        groups = []

        for (group, contents) in self.config.groups.iteritems():
            group_names = set(g[0] for g in contents)
            if group_names.issubset(name_set):
                groups.append(group)
        return groups

    def get_configured_tunnels(self, filter_active=None):
        """
        Retrieve tunnels that are active, inactive or both.

        Return list of tunnel names.
        """
        tunnels = self.config.tunnels.keys()
        if filter_active is None:
            return tunnels
        elif filter_active:
            return [
                tunnel for tunnel in tunnels
                if self.is_tunnel_active(tunnel)
            ]
        else:
            return [
                tunnel for tunnel in tunnels
                if not self.is_tunnel_active(tunnel)
            ]

    def get_configured_groups(self, filter_active=None):
        """
        Retrieve groups that are active, inactive or both.

        Return list of group names.
        """
        groups = self.config.groups.keys()
        if filter_active is None:
            return groups
        else:
            tunnels = self.get_configured_tunnels(filter_active)
            return self.identify_group(tunnels)

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
            yield self._start_tunnel(tunnel_name, tunnel_port)[0]

    def _start_tunnel(self, name, local_port_override=None):
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

        local_port = local_port_override \
            if local_port_override is not None else data['local_port']

        success = self.process_helper.start_tunnel(
            user=user_name,
            server=data['server'],
            local_port=local_port,
            remote_port=data['remote_port'],
            ssh_debug_level=self.ssh_debug_level
        )

        if success:
            return [(name, local_port)]
        else:
            return [
                (
                    name,
                    '{user}@{server} - local:{local} - remote:{remote}'.format(
                        user=user_name,
                        server=data['server'],
                        local=local_port,
                        remote=data['remote_port'],
                    )
                )
            ]

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
