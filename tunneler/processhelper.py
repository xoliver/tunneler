import re
from collections import namedtuple
from subprocess import call

import psutil


Tunnel = namedtuple(
    'Tunnel',
    ['process', 'from_port', 'to_port', 'user', 'server']
)

pid_matcher = re.compile(r'^(\d+)-')
port_matcher = re.compile(r'.*-L(\d+):localhost:(\d+).*')
login_matcher = re.compile(r'.* ([^@]+)@([^ ]+).*')

START_COMMAND = \
    'ssh -f -N -L{local_port}:localhost:{remote_port} {user}@{server}'


class ProcessHelper(object):
    def get_active_tunnels(self):
        for process in psutil.process_iter():
            try:
                if process.name() == 'ssh' and '-N' in process.cmdline():
                    try:
                        command = ' '.join(process.cmdline())
                        from_port, to_port, user, server = \
                            self.extract_tunnel_info(command)
                    except AttributeError:
                        pass
                    else:
                        yield Tunnel(process, from_port, to_port, user, server)
            except psutil.AccessDenied:
                pass

    def extract_tunnel_info(self, line):
        (from_port, to_port) = port_matcher.match(line).groups()
        (user, server) = login_matcher.match(line).groups()

        return int(from_port), int(to_port), user, server

    def start_tunnel(self, user, server, local_port, remote_port):
        command = START_COMMAND.format(
            user=user,
            server=server,
            local_port=local_port,
            remote_port=remote_port
        )
        return call(command.split()) == 0

    def stop_tunnel(self, tunnel):
        try:
            tunnel.process.terminate()
            return True
        except:
            return False
