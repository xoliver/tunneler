import re
from collections import namedtuple

import psutil


Tunnel = namedtuple(
    'Tunnel',
    ['pid', 'from_port', 'to_port', 'user', 'server']
)

pid_matcher = re.compile(r'^(\d+)-')
port_matcher = re.compile(r'.*-L(\d+):localhost:(\d+).*')
login_matcher = re.compile(r'.* ([^@]+)@([^ ]+).*')


class ProcessHelper(object):
    def list_ssh_tunnels(self):
        for process in psutil.process_iter():
            try:
                if process.name() == 'ssh' and '-N' in process.cmdline():
                    line = '{}-{}'.format(
                        process.pid, ' '.join(process.cmdline()))
                    yield line
            except psutil.AccessDenied:
                pass

    def process_line_to_tunnel(self, line):
        pid = pid_matcher.match(line).group(1)
        (from_port, to_port) = port_matcher.match(line).groups()
        (user, server) = login_matcher.match(line).groups()

        return Tunnel(int(pid), int(from_port), int(to_port), user, server)

    def get_active_tunnels(self):
        for line in self.list_ssh_tunnels():
            try:
                yield self.process_line_to_tunnel(line)
            except AttributeError:
                pass
