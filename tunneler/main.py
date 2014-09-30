import click

from tunneler import Tunneler
from processhelper import ProcessHelper

tunneler = Tunneler(ProcessHelper())


@click.group()
@click.option('--verbose', is_flag=True, help='Show verbose information')
def cli(verbose):
    tunneler.set_verbose(verbose)


@cli.command(short_help='Start a tunnel')
@click.argument('name', default=None)
def start(name):
    print tunneler.start_tunnel(name)


@cli.command(short_help='Show active tunnels')
def show():
    print tunneler.list_tunnels()

if __name__ == '__main__':
    cli(False)
