from os.path import expanduser, join
import sys

import click

from config import TunnelerConfigParser
from tunneler import AlreadyThereError, ConfigNotFound, Tunneler
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
        sys.exit(0)
    validation_errors = config_parser.validate()
    if validation_errors:
        print 'Problem loading ~/.tunneler.cfg :'
        print '\n'.join(validation_errors)
        sys.exit(0)

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
            start_call(name)


@cli.command(short_help='Stop one or more or ALL tunnels')
@click.argument('names', nargs=-1)
def stop(names):
    if not names:
        print_active_tunnels()
    elif len(names) == 1 and names[0].lower() == 'all':
        for (name, result) in tunneler.stop_all_tunnels():
            print '{} {}'.format(
                name, 'stopped' if result else 'not stopped - problem!')
    else:
        for name in names:
            stop_call(name)


@cli.command(short_help='Show active tunnels')
def show():
    print_active_tunnels(tunneler.verbose)
    print_inactive_tunnels()


def start_call(name):
    try:
        port = tunneler.start(name)
    except AlreadyThereError:
        print 'Tunnel already active'
    except ConfigNotFound:
        print 'Tunnel config not found: {}'.format(name)
    else:
        if port:
            if type(port) == list:
                print 'Tunnels started in ports {}'.format(port)
            else:
                print 'Tunnel started in port {}'.format(port)
        else:
            print 'Tunnel NOT started'


def stop_call(name):
    try:
        success = tunneler.stop(name)
    except AlreadyThereError:
        print 'Tunnel already inactive'
    except ConfigNotFound:
        print 'Tunnel config not found: {}'.format(name)
    else:
        if type(success) == list:
            print 'Successes stopping tunnels: {}'.format(success)
        else:
            if success:
                print 'Tunnel stopped'
            else:
                print 'Problem stopping tunnel'


def print_active_tunnels(verbose=False):
    if verbose:
        active = [
            '{}:{}'.format(name, data['local_port'])
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
