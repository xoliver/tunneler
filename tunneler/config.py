import ConfigParser
from collections import namedtuple


DEFAULT_USER = 'mr-x'

DEFAULT_COMMON_CONFIG = {'default_user': DEFAULT_USER}

Config = namedtuple('ConfigTuple', ['common', 'tunnels'])


class TunnelerConfigParser(ConfigParser.ConfigParser):

    """
    Custom ConfigParser that allows the retrieval of config as a dictionary,
    extended from:
        http://stackoverflow.com/questions/3220670/read-all-the-contents-in-ini-file-into-dictionary-with-python/3220891#3220891
    """  # NOQA

    def _as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

    def get_config(self):
        data = self._as_dict()
        common = data.pop('common', DEFAULT_COMMON_CONFIG)

        return Config(common, data)
