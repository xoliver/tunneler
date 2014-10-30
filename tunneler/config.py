"""
Custom configuration file parser.
"""
import ConfigParser

from .models import Configuration


DEFAULT_USER = 'mr-x'

DEFAULT_COMMON_CONFIG = {'default_user': DEFAULT_USER}


class TunnelerConfigParser(ConfigParser.ConfigParser):

    """
    Custom ConfigParser that allows the retrieval of config as a dictionary,
    extended from:
        http://stackoverflow.com/questions/3220670/read-all-the-contents-in-ini-file-into-dictionary-with-python/3220891#3220891
    """  # NOQA

    _config = None

    def _as_dict(self):
        """
        Generate dictionary from contained data.

        Return dict.
        """
        sec_dict = dict(self._sections)
        for key in sec_dict:
            sec_dict[key] = dict(self._defaults, **sec_dict[key])
            sec_dict[key].pop('__name__', None)
            for field in sec_dict[key]:
                if field.endswith('_port'):
                    sec_dict[key][field] = int(sec_dict[key][field])
        return sec_dict

    def _create_config(self):
        """
        Generate Configuration object from contained data.

        Return Configuration.
        """
        data = self._as_dict()
        common = data.pop('common', DEFAULT_COMMON_CONFIG)
        groups = data.pop('groups', {})

        for (name, value) in groups.items():
            processed_values = []
            for tunnel in value.strip().split('\n'):
                if ':' in tunnel:
                    parts = tunnel.rsplit(':', 1)
                    processed_values.append((parts[0], int(parts[1])))
                else:
                    processed_values.append((tunnel, None))
            groups[name] = processed_values

        self._config = Configuration(common, data, groups)

    def get_config(self):
        """
        Retrieve configuration, generating it first if it is not there.

        Return Configuration.
        """
        if self._config is None:
            self._create_config()

        return self._config

    def validate(self):
        """
        Check that the configuration is correct and consistent.

        Return list of error messages.
        """
        if not hasattr(self, '_config'):
            self._create_config()

        results = []

        for group_name, group_tunnels in self._config.groups.items():
            for (tunnel, _) in group_tunnels:
                if tunnel not in self._config.tunnels:
                    results.append(
                        '[{}] tunnel {} undefined'.format(
                            group_name, tunnel)
                    )
            if group_name in self._config.tunnels:
                results.append(
                    'Found one group and a tunnel called the same: {}'.format(
                        group_name)
                )
        return results
