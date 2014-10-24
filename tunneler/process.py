import re
from subprocess import call

import psutil

from models import Tunnel

pid_matcher = re.compile(r'^(\d+)-')
port_matcher = re.compile(r'.*-L(\d+):localhost:(\d+).*')
login_matcher = re.compile(r'.* ([^@]+)@([^ ]+).*')

# -g allow remote host to connect to local port
# -f go to background
# -o StrictHostKeyChecking=no
START_COMMAND = \
    'ssh -g -f -N -L{local_port}:localhost:{remote_port} {user}@{server}'


class ProcessHelper(object):
    def get_active_tunnels(self):
        for process in psutil.process_iter():
            try:
                if process.name() == 'ssh' and '-N' in process.cmdline():
                    try:
                        command = ' '.join(process.cmdline())
                        local_port, remote_port, user, server = \
                            self.extract_tunnel_info(command)
                    except AttributeError:
                        pass
                    else:
                        yield Tunnel('unidentified', process, local_port, remote_port, user, server)  # NOQA
            except psutil.AccessDenied:
                pass

    def extract_tunnel_info(self, line):
        (local_port, remote_port) = port_matcher.match(line).groups()
        (user, server) = login_matcher.match(line).groups()

        return int(local_port), int(remote_port), user, server

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
