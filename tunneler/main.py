import ConfigParser
from os.path import expanduser, join

import click

from tunneler import Tunneler
from processhelper import ProcessHelper


class DictConfigParser(ConfigParser.ConfigParser):

    """
    Custom ConfigParser that allows the retrieval of config as a dictionary.
    From: http://stackoverflow.com/questions/3220670/read-all-the-contents-in-ini-file-into-dictionary-with-python/3220891#3220891
    """  # NOQA

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

tunneler = None


@click.group()
@click.option('--verbose', is_flag=True, help='Show verbose information')
def cli(verbose):
    # Load settings first
    config_file = join(expanduser('~'), '.tunneler.cfg')
    config_parser = DictConfigParser()
    if not config_parser.read(config_file):
        print 'Could not find valid ~/.tunneler.cfg! - Aborting'
        return

    global tunneler
    tunneler = Tunneler(ProcessHelper(), config_parser.as_dict())
    tunneler.set_verbose(verbose)


@cli.command(short_help='Check the state of a tunnel')
@click.argument('name')
def check(name):
    try:
        if tunneler.is_tunnel_active(name):
            print 'Tunnel is active'
        else:
            print 'Tunnel is NOT active'
    except NameError:
        print 'Unknown tunnel'


@cli.command(short_help='Start a tunnel')
@click.argument('name')
def start(name):
    print tunneler.start_tunnel(name)


@cli.command(short_help='Stop a tunnel')
@click.argument('name')
def stop(name):
    if name.lower() == 'all':
        print tunneler.stop_all_tunnels()
    else:
        print tunneler.stop_tunnel(name)


@cli.command(short_help='Show active tunnels')
def show():
    if tunneler.verbose:
        active = [
            '{}({})'.format(name, data['local_port'])
            for (name, data) in tunneler.get_active_tunnels()
        ]
    else:
        active = tunneler.get_configured_tunnels(filter_active=True)

    print 'Active:\t\t', ' '.join(sorted(active))
    inactive = tunneler.get_configured_tunnels(filter_active=False)
    print 'Inactive:\t', ' '.join(sorted(inactive))


if __name__ == '__main__':
    cli(False)
