import click

from tunneler import Tunneler
from processhelper import ProcessHelper

tunneler = Tunneler(ProcessHelper())


@click.group()
@click.option('--verbose', is_flag=True, help='Show verbose information')
def cli(verbose):
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
    print tunneler.stop_tunnel(name)


@cli.command(short_help='Show active tunnels')
def show():
    if tunneler.verbose:
        active = [
            '{}: {}'.format(name, data)
            for (name, data) in tunneler.get_active_tunnels()
        ]
    else:
        active = tunneler.get_configured_tunnels(filter_active=True)

    print 'Active:\t\t', ' '.join(sorted(active))
    inactive = tunneler.get_configured_tunnels(filter_active=False)
    print 'Inactive:\t', ' '.join(sorted(inactive))


if __name__ == '__main__':
    cli(False)
