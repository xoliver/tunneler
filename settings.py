TUNNELS = {}

# Redefine TUNNELS in a new file local_settings.py with data like this:
# TUNNELS = {
#     'short-tunnel-name': {
#         'name': 'Long tunnel name',
#         'local_port': 111,
#         'remote_port': 222,
#         'user': 'somebody',
#         'server': 'server.somewhere.net',
#     },
# }

try:
    from local_settings import *  # NOQA
except ImportError:
    pass
