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

        return Configuration(common, data, groups)
