from os.path import expanduser, join

import click

from config import TunnelerConfigParser
from tunneler import ConfigNotFound, Tunneler
from process import ProcessHelper


tunneler = None


@click.group()
@click.option('--verbose', is_flag=True, help='Show verbose information')
def cli(verbose):
    # Load settings first
    config_file = join(expanduser('~'), '.tunneler.cfg')
    config_parser = TunnelerConfigParser()
    if not config_parser.read(config_file):
        print 'Could not find valid ~/.tunneler.cfg! - Aborting'
        return

    global tunneler
    tunneler = Tunneler(ProcessHelper(), config_parser.get_config(), verbose)


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


@cli.command(short_help='Start one or more tunnels')
@click.argument('names', nargs=-1)
def start(names):
    if not names:
        print_inactive_tunnels()
    else:
        for name in names:
            start_tunnel(name)


@cli.command(short_help='Stop one or more or ALL tunnels')
@click.argument('names', nargs=-1)
def stop(names):
    if not names:
        print_active_tunnels()
    elif len(names) == 1 and names[0].lower() == 'all':
        print tunneler.stop_all_tunnels()
    else:
        for name in names:
            stop_tunnel(name)


@cli.command(short_help='Show active tunnels')
def show():
    print_active_tunnels(tunneler.verbose)
    print_inactive_tunnels()


def start_tunnel(name):
    try:
        tunneler.start_tunnel(name)
    except ConfigNotFound:
        print 'Tunnel config not found: {}'.format(name)


def stop_tunnel(name):
    try:
        tunneler.stop_tunnel(name)
    except ConfigNotFound:
        print 'Tunnel config not found: {}'.format(name)


def print_active_tunnels(verbose=False):
    if verbose:
        active = [
            '{}({})'.format(name, data['local_port'])
            for (name, data) in tunneler.get_active_tunnels()
        ]
    else:
        active = tunneler.get_configured_tunnels(filter_active=True)

    if active:
        print 'Active:\t\t', ' '.join(sorted(active))
    else:
        print 'No active tunnels'


def print_inactive_tunnels():
    inactive = tunneler.get_configured_tunnels(filter_active=False)

    if inactive:
        print 'Inactive:\t', ' '.join(sorted(inactive))
    else:
        print 'No inactive tunnels'


if __name__ == '__main__':
    cli(False)
