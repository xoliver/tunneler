import ConfigParser
from models import Configuration


DEFAULT_USER = 'mr-x'

DEFAULT_COMMON_CONFIG = {'default_user': DEFAULT_USER}


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
            for field in d[k]:
                if field.endswith('_port'):
                    d[k][field] = int(d[k][field])
        return d

    def get_config(self):
        data = self._as_dict()
        common = data.pop('common', DEFAULT_COMMON_CONFIG)

        return Configuration(common, data)
