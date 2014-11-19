"""
Main entry point for tunneler.

Handle command line parameters and output.
"""
from __future__ import print_function
from os.path import expanduser, join
import sys

import click

from .config import TunnelerConfigParser
from .tunneler import ConfigNotFound, Tunneler
from .process import ProcessHelper
from .utils import (fail, ok)


TUNNELER = None


@click.group()
@click.option('--verbose', is_flag=True, help='Show verbose information')
def cli(verbose):
    # Load settings first
    config_file = join(expanduser('~'), '.tunneler.cfg')
    config_parser = TunnelerConfigParser()
    if not config_parser.read(config_file):
        print('Could not find valid ~/.tunneler.cfg! - Aborting')
        sys.exit(0)
    validation_errors = config_parser.validate()
    if validation_errors:
        print('Problem loading ~/.tunneler.cfg :')
        print('\n'.join(validation_errors))
        sys.exit(0)

    global TUNNELER
    TUNNELER = Tunneler(ProcessHelper(), config_parser.get_config(), verbose)


@cli.command(short_help='Check the state of a tunnel')
@click.argument('name')
def check(name):
    try:
        if TUNNELER.is_tunnel_active(name):
            print('Tunnel is active')
        else:
            print('Tunnel is NOT active')
    except NameError:
        print('Unknown tunnel')


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
        for (name, result) in TUNNELER.stop_all_tunnels():
            if result:
                print(ok(name))
            else:
                print(fail(name))
    else:
        for name in names:
            stop_call(name)


@cli.command(short_help='Show active/inactive (tunnels|groups|all)')
@click.argument('what', nargs=1, default='all')
def show(what):
    if what in ('all', 'tunnels'):
        print_active_tunnels(TUNNELER.verbose)
        print_inactive_tunnels()
    if what in ('all', 'groups'):
        print_active_groups()
        print_inactive_groups()
    if what not in ('all', 'groups', 'tunnels'):
        print('No idea what {} is'.format(what))


def start_call(name):
    try:
        for (tunnel_name, port) in TUNNELER.start(name):
            if type(port) == int:
                print(ok('{}:{}'.format(tunnel_name, port)))
            else:
                print(fail('{} : {}'.format(tunnel_name, port)))
    except ConfigNotFound:
        print('Tunnel config not found: {}'.format(name))


def stop_call(name):
    try:
        for (tunnel_name, success) in TUNNELER.stop(name):
            if success:
                print(ok(tunnel_name))
            else:
                print(fail(tunnel_name))
    except ConfigNotFound:
        print('Tunnel config not found: {}'.format(name))


def print_active_tunnels(verbose=False):
    if verbose:
        active = [
            '{}:{}'.format(name, data['local_port'])
            for (name, data) in TUNNELER.get_active_tunnels()
        ]
    else:
        active = TUNNELER.get_configured_tunnels(filter_active=True)

    if active:
        print('Active:\t\t', ' '.join(sorted(active)))
    else:
        print('No active tunnels')


def print_inactive_tunnels():
    inactive = TUNNELER.get_configured_tunnels(filter_active=False)

    if inactive:
        print('Inactive:\t', ' '.join(sorted(inactive)))
    else:
        print('No inactive tunnels')


def print_active_groups():
    active = TUNNELER.get_configured_groups(filter_active=True)
    if active:
        print('Active groups:\t', ' '.join(active))
    else:
        print('No active groups')


def print_inactive_groups():
    inactive = TUNNELER.get_configured_groups(filter_active=False)
    if inactive:
        print (
            'Inactive groups:\t', ' '.join(
                TUNNELER.get_configured_groups(filter_active=False))
        )
    else:
        print('No inactive groups')


if __name__ == '__main__':
    cli(False)
