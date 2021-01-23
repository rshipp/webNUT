# User-defined configuration.
# Rename this to config.py.

# Single server configuration, backards compatible:

server = '127.0.0.1'
port = 3493
username = None
password = None

# Multi-server configuration:

from .webnut import NUTServer

servers = [
  NUTServer('192.168.1.3', 3493, None, None),
  NUTServer('192.168.1.6', 3493, None, None)
]
