"""
Main entry point for tunneler.

Handle command line parameters and output.
"""
from __future__ import print_function
import os
from os.path import expanduser, join
import sys

import click

from .config import TunnelerConfigParser
from .models import Configuration
from .tunneler import ConfigNotFound, Tunneler
from .process import ProcessHelper
from .utils import (fail, ok)


TUNNELER = None
DEFAULT_USER = 'nobody'


@click.group()
@click.option('--verbose', is_flag=True, help='Show verbose information')
def cli(verbose):
    # Load configurations
    local_config_file = join(os.getcwd(), 'tunnels.cfg')
    local_config = load_config(local_config_file)

    global_config_file = join(expanduser('~'), '.tunneler.cfg')
    global_config = load_config(global_config_file)

    if not local_config and not global_config:
        print(
            'Could not find tunneler.cfg in this folder or .tunneler.cfg '
            'in your home folder!'
        )
        sys.exit(0)

    config = combine_configs([global_config, local_config])

    global TUNNELER
    TUNNELER = Tunneler(ProcessHelper(), config, verbose)


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


@cli.command(short_help='Stop and start specific or all active tunnels')
@click.argument('names', nargs=-1)
def restart(names):
    if not names:
        for (tunnel_name, _) in TUNNELER.get_active_tunnels():
            stop_call(tunnel_name)
            start_call(tunnel_name)
    else:
        for name in names:
            stop_call(name)
            start_call(name)


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
        for (tunnel_name, result) in TUNNELER.start(name):
            if type(result) == int:
                print(ok('{}:{}'.format(tunnel_name, result)))
            else:
                print(fail('{} : {}'.format(tunnel_name, result)))
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


def load_config(file_path):
    config_parser = TunnelerConfigParser()
    if not config_parser.read(file_path):
        return None

    validation_errors = config_parser.validate()
    if validation_errors:
        print('Problem loading {} :'.format(file_path))
        print('\n'.join(validation_errors))
        sys.exit(0)

    return config_parser.get_config()


def combine_configs(configs):
    """
    Generate a combined Configuration by overwriting earlier list elements.
    """
    combined_config = Configuration(common={}, tunnels={}, groups={})

    for config in configs:
        if not config:
            continue
        combined_config.common.update(config.common)
        combined_config.tunnels.update(config.tunnels)
        combined_config.groups.update(config.groups)

    if combined_config.common.get('default_user') is None:
        combined_config.common['default_user'] = DEFAULT_USER

    return combined_config


if __name__ == '__main__':
    cli(False)
